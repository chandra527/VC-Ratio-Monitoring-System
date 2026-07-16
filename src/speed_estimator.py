from yolo_detector import CLASS_NAMES
from yolo_detector import VEHICLE_CLASSES



class SpeedEstimator:

    def __init__(
        self,
        line_a_y,
        line_b_y,
        fps,
        distance_meters=10,
        line_tolerance=15
    ):

        # Garis awal pengukuran
        self.line_a_y = line_a_y

        # Garis akhir pengukuran
        self.line_b_y = line_b_y

        # FPS asli video
        self.fps = fps

        # Asumsi jarak nyata antar-garis
        self.distance_meters = distance_meters

        # Toleransi agar kendaraan tidak harus
        # tepat menyentuh satu koordinat piksel
        self.line_tolerance = line_tolerance

        # Posisi Y kendaraan pada frame sebelumnya
        self.previous_y = {}

        # Menyimpan nomor frame saat ID melewati Line A
        self.line_a_frames = {}

        # Menyimpan hasil estimasi kecepatan setiap ID
        self.vehicle_speeds = {}


    def update(
        self,
        result,
        frame_ke
    ):

        for box in result.boxes:

            # Kecepatan membutuhkan tracking ID
            if box.id is None:
                continue

            track_id = int(box.id[0])

            cls = int(box.cls[0])

            class_name = CLASS_NAMES[cls]

            if class_name not in VEHICLE_CLASSES:
                continue

            vehicle_key = VEHICLE_CLASSES[class_name]["key"]
            
            # Ambil bounding box
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            # Bagian bawah bounding box dianggap
            # sebagai posisi kendaraan pada jalan
            current_y = y2

            # Ambil posisi ID pada frame sebelumnya
            old_y = self.previous_y.get(track_id)

            # Jika ID baru pertama terlihat,
            # simpan posisinya dan lanjut ke box berikutnya
            if old_y is None:

                self.previous_y[track_id] = current_y

                continue


            # =====================================
            # CEK LINE A
            # =====================================

            crossed_line_a = (
                old_y
                < self.line_a_y - self.line_tolerance
                and current_y
                >= self.line_a_y - self.line_tolerance
            )

            if (
                crossed_line_a
                and track_id not in self.line_a_frames
            ):

                self.line_a_frames[track_id] = frame_ke

                print(
                    f"SPEED LINE A: "
                    f"{vehicle_key} "
                    f"ID #{track_id} "
                    f"Frame {frame_ke}"
                )


            # =====================================
            # CEK LINE B
            # =====================================

            crossed_line_b = (
                old_y
                < self.line_b_y - self.line_tolerance
                and current_y
                >= self.line_b_y - self.line_tolerance
            )

            can_calculate_speed = (
                crossed_line_b
                and track_id in self.line_a_frames
                and track_id not in self.vehicle_speeds
            )

            if can_calculate_speed:

                frame_a = self.line_a_frames[track_id]

                frame_difference = (
                    frame_ke - frame_a
                )

                if (
                    frame_difference > 0
                    and self.fps > 0
                ):

                    travel_time_seconds = (
                        frame_difference / self.fps
                    )

                    speed_mps = (
                        self.distance_meters
                        / travel_time_seconds
                    )

                    speed_kmh = speed_mps * 3.6

                    self.vehicle_speeds[track_id] = (
                        speed_kmh
                    )

                    print(
                        f"KECEPATAN ESTIMASI: "
                        f"{vehicle_key} "
                        f"ID #{track_id} "
                        f"{speed_kmh:.1f} km/jam "
                        f"({travel_time_seconds:.2f} detik)"
                    )


            # Posisi sekarang digunakan sebagai
            # posisi lama pada frame berikutnya
            self.previous_y[track_id] = current_y


    def get_speed(self, track_id):

        return self.vehicle_speeds.get(track_id)


    def get_all_speeds(self):

        return self.vehicle_speeds.copy()