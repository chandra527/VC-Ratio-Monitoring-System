from collections import Counter

from yolo_detector import CLASS_NAMES
from yolo_detector import VEHICLE_CLASSES


class VehicleTracker:

    def __init__(
        self,
        line_y,
        line_tolerance=35,
        min_track_frames=3
    ):

        # Posisi utama garis hitung
        self.line_y = line_y

        # Lebar zona toleransi di sekitar garis
        self.line_tolerance = line_tolerance

        # Minimal jumlah frame agar ID dianggap stabil
        self.min_track_frames = min_track_frames

        # Jumlah kemunculan setiap tracking ID
        self.track_frames = {}

        # Voting jenis kendaraan setiap ID
        self.class_votes = {}

        # ID yang pernah terlihat sebelum zona hitung
        self.seen_above = set()

        # ID yang sudah dihitung
        self.crossed_ids = set()

        # Rekap kendaraan yang sudah memasuki zona
        self.vehicle_count = {
            "motor": 0,
            "mobil": 0,
            "bus": 0,
            "truk": 0,
            "ambulans": 0
        }


    def update(self, result):

        zone_top = self.line_y - self.line_tolerance

        for box in result.boxes:

            # Lewati objek yang belum mendapat tracking ID
            if box.id is None:
                continue

            track_id = int(box.id[0])
            cls = int(box.cls[0])

            class_name = CLASS_NAMES[cls]

            # Abaikan objek selain kendaraan
            if class_name not in VEHICLE_CLASSES:
                continue

            detected_key = VEHICLE_CLASSES[class_name]["key"]

            # Hitung jumlah frame kemunculan ID
            self.track_frames[track_id] = (
                self.track_frames.get(track_id, 0) + 1
            )

            # Siapkan voting kelas untuk ID ini
            if track_id not in self.class_votes:
                self.class_votes[track_id] = Counter()

            self.class_votes[track_id][detected_key] += 1

            # Pilih kelas yang paling sering muncul
            key = self.class_votes[track_id].most_common(1)[0][0]

            # Ambil koordinat bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Posisi bawah box dianggap sebagai posisi kendaraan di jalan
            current_y = y2

            # Tandai bahwa kendaraan pernah berada di atas zona
            if current_y < zone_top:
                self.seen_above.add(track_id)

            track_is_stable = (
                self.track_frames[track_id]
                >= self.min_track_frames
            )

            entered_counting_zone = (
                track_id in self.seen_above
                and current_y >= zone_top
            )

            not_counted_yet = (
                track_id not in self.crossed_ids
            )

            if (
                track_is_stable
                and entered_counting_zone
                and not_counted_yet
            ):
                self.vehicle_count[key] += 1
                self.crossed_ids.add(track_id)

                print(
                    f"TERHITUNG: {key} "
                    f"ID #{track_id} "
                    f"Total = {self.vehicle_count[key]}"
                )


    def get_vehicle_data(self):

        return self.vehicle_count.copy()
    

    def get_vehicle_label(self, track_id):

        if track_id not in self.class_votes:
            return None

        key = self.class_votes[track_id].most_common(1)[0][0]

        return key