from collections import Counter

from yolo_detector import CLASS_NAMES
from yolo_detector import VEHICLE_CLASSES


class VehicleTracker:

    ABOVE = "ABOVE"
    BELOW = "BELOW"
    ZONE = "ZONE"

    DIRECTION_UP = "UP"
    DIRECTION_DOWN = "DOWN"

    def __init__(
        self,
        line_y,
        line_tolerance=35,
        min_track_frames=3,
    ):
        # Posisi utama garis hitung
        self.line_y = line_y

        # Lebar zona toleransi di sekitar garis
        self.line_tolerance = line_tolerance

        # Minimal jumlah frame agar tracking ID dianggap stabil
        self.min_track_frames = min_track_frames

        # Jumlah kemunculan setiap tracking ID
        self.track_frames = {}

        # Voting jenis kendaraan untuk setiap tracking ID
        self.class_votes = {}

        # Sisi terakhir kendaraan di luar zona hitung
        self.last_non_zone_side = {}

        # ID kendaraan yang sudah dihitung
        self.crossed_ids = set()

        # Arah perjalanan setiap kendaraan yang sudah dihitung
        self.vehicle_directions = {}

        # Rekap jumlah kendaraan
        self.vehicle_count = {
            "motor": 0,
            "mobil": 0,
            "bus": 0,
            "truk": 0,
            "ambulans": 0,
        }

        # Rekap berdasarkan arah
        self.direction_count = {
            self.DIRECTION_UP: 0,
            self.DIRECTION_DOWN: 0,
        }

    def _get_position_side(self, current_y):
        """
        Menentukan posisi kendaraan terhadap zona hitung.
        """

        zone_top = self.line_y - self.line_tolerance
        zone_bottom = self.line_y + self.line_tolerance

        if current_y < zone_top:
            return self.ABOVE

        if current_y > zone_bottom:
            return self.BELOW

        return self.ZONE

    def _get_crossing_direction(
        self,
        previous_side,
        current_side,
    ):
        """
        Menentukan arah kendaraan berdasarkan perpindahan sisi.
        """

        if (
            previous_side == self.ABOVE
            and current_side == self.BELOW
        ):
            return self.DIRECTION_DOWN

        if (
            previous_side == self.BELOW
            and current_side == self.ABOVE
        ):
            return self.DIRECTION_UP

        return None

    def update(self, result):
        """
        Memperbarui lifecycle kendaraan dari hasil tracking.

        Mengembalikan daftar event kendaraan yang baru
        melintasi zona hitung.
        """

        crossing_events = []

        if result.boxes is None:
            return crossing_events

        for box in result.boxes:

            # Lewati objek yang belum memperoleh tracking ID
            if box.id is None:
                continue

            track_id = int(box.id[0])
            class_id = int(box.cls[0])

            class_name = CLASS_NAMES[class_id]

            # Abaikan objek selain kendaraan
            if class_name not in VEHICLE_CLASSES:
                continue

            detected_key = VEHICLE_CLASSES[class_name]["key"]

            # Hitung jumlah frame kemunculan tracking ID
            self.track_frames[track_id] = (
                self.track_frames.get(track_id, 0) + 1
            )

            # Siapkan voting kelas untuk tracking ID
            if track_id not in self.class_votes:
                self.class_votes[track_id] = Counter()

            self.class_votes[track_id][detected_key] += 1

            # Gunakan kelas yang paling sering terdeteksi
            vehicle_key = (
                self.class_votes[track_id]
                .most_common(1)[0][0]
            )

            # Ambil koordinat bounding box
            _, _, _, y2 = map(int, box.xyxy[0])

            # Bagian bawah bounding box dianggap menyentuh jalan
            current_y = y2

            current_side = self._get_position_side(
                current_y
            )

            previous_side = self.last_non_zone_side.get(
                track_id
            )

            track_is_stable = (
                self.track_frames[track_id]
                >= self.min_track_frames
            )

            not_counted_yet = (
                track_id not in self.crossed_ids
            )

            direction = self._get_crossing_direction(
                previous_side,
                current_side,
            )

            if (
                track_is_stable
                and not_counted_yet
                and direction is not None
            ):
                self.vehicle_count[vehicle_key] += 1
                self.direction_count[direction] += 1

                self.crossed_ids.add(track_id)
                self.vehicle_directions[track_id] = direction

                event = {
                    "track_id": track_id,
                    "vehicle_type": vehicle_key,
                    "direction": direction,
                    "position_y": current_y,
                }

                crossing_events.append(event)

                print(
                    f"TERHITUNG: {vehicle_key} "
                    f"ID #{track_id} "
                    f"Arah = {direction} "
                    f"Total = "
                    f"{self.vehicle_count[vehicle_key]}"
                )

            # Posisi di dalam zona tidak mengganti sisi terakhir.
            # Ini mencegah perubahan arah palsu akibat bounding box
            # yang bergoyang di sekitar garis.
            if current_side != self.ZONE:
                self.last_non_zone_side[track_id] = (
                    current_side
                )

        return crossing_events

    def get_vehicle_data(self):
        return self.vehicle_count.copy()

    def get_direction_data(self):
        return self.direction_count.copy()

    def get_vehicle_direction(self, track_id):
        return self.vehicle_directions.get(track_id)

    def get_vehicle_label(self, track_id):
        if track_id not in self.class_votes:
            return None

        vehicle_key = (
            self.class_votes[track_id]
            .most_common(1)[0][0]
        )

        return vehicle_key