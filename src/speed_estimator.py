from yolo_detector import CLASS_NAMES
from yolo_detector import VEHICLE_CLASSES


class SpeedEstimator:

    def __init__(
        self,
        line_a_start,
        line_a_end,
        line_b_start,
        line_b_end,
        fps,
        distance_meters=10,
    ):

        self.line_a_start = line_a_start
        self.line_a_end = line_a_end

        self.line_b_start = line_b_start
        self.line_b_end = line_b_end

        self.fps = fps
        self.distance_meters = distance_meters

        # Posisi kendaraan pada frame sebelumnya
        self.previous_point = {}

        # Menyimpan garis pertama yang dilewati kendaraan
        # Contoh:
        # {
        #   track_id: {
        #       "line": "A",
        #       "frame": 100
        #   }
        # }
        self.first_crossing = {}

        # Hasil kecepatan kendaraan
        # Contoh:
        # {
        #   track_id: {
        #       "speed_kmh": 42.5,
        #       "direction": "A_TO_B"
        #   }
        # }
        self.vehicle_speeds = {}


    # ==========================================
    # POSISI TITIK TERHADAP GARIS
    # ==========================================

    def _line_side(
        self,
        point,
        line_start,
        line_end,
    ):

        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end

        return (
            (x2 - x1) * (py - y1)
            -
            (y2 - y1) * (px - x1)
        )


    # ==========================================
    # CEK CROSSING GARIS
    # ==========================================

    def _crossed_line(
        self,
        old_point,
        current_point,
        line_start,
        line_end,
    ):

        old_side = self._line_side(
            old_point,
            line_start,
            line_end,
        )

        current_side = self._line_side(
            current_point,
            line_start,
            line_end,
        )

        # Harus benar-benar berpindah sisi
        crossed_infinite_line = (
            old_side == 0
            or current_side == 0
            or (
                old_side < 0 < current_side
            )
            or (
                old_side > 0 > current_side
            )
        )

        if not crossed_infinite_line:
            return False

        # ==========================================
        # CARI TITIK POTONG TRAJECTORY DENGAN GARIS
        # ==========================================

        x1, y1 = old_point
        x2, y2 = current_point

        x3, y3 = line_start
        x4, y4 = line_end

        denominator = (
            (x1 - x2) * (y3 - y4)
            -
            (y1 - y2) * (x3 - x4)
        )

        # Garis sejajar / hampir sejajar
        if denominator == 0:
            return False

        t = (
            (x1 - x3) * (y3 - y4)
            -
            (y1 - y3) * (x3 - x4)
        ) / denominator

        u = -(
            (x1 - x2) * (y1 - y3)
            -
            (y1 - y2) * (x1 - x3)
        ) / denominator

        # t = posisi titik potong pada trajectory kendaraan
        # u = posisi titik potong pada speed line
        #
        # Crossing sah hanya jika:
        # - titik potong berada di antara old_point-current_point
        # - titik potong berada di antara endpoint speed line
        return (
            0.0 <= t <= 1.0
            and
            0.0 <= u <= 1.0
        )


    # ==========================================
    # SIMPAN CROSSING PERTAMA
    # ==========================================

    def _register_first_crossing(
        self,
        track_id,
        line_name,
        frame_ke,
        vehicle_label,
    ):

        if track_id in self.first_crossing:
            return

        self.first_crossing[
            track_id
        ] = {
            "line": line_name,
            "frame": frame_ke,
        }

        print(
            f"[SPEED] ID {track_id} "
            f"({vehicle_label}) "
            f"START di Line {line_name} "
            f"frame {frame_ke}"
        )


    # ==========================================
    # HITUNG SPEED SAAT GARIS KEDUA DILEWATI
    # ==========================================

    def _calculate_if_complete(
        self,
        track_id,
        crossed_line_name,
        frame_ke,
        vehicle_label,
    ):

        if track_id not in self.first_crossing:
            return

        if track_id in self.vehicle_speeds:
            return

        first_data = (
            self.first_crossing[
                track_id
            ]
        )

        first_line = first_data["line"]
        first_frame = first_data["frame"]

        # Kalau masih crossing garis yang sama,
        # jangan hitung speed
        if crossed_line_name == first_line:
            return


        # ======================================
        # TENTUKAN ARAH
        # ======================================

        if (
            first_line == "A"
            and crossed_line_name == "B"
        ):

            direction = "A_TO_B"

        elif (
            first_line == "B"
            and crossed_line_name == "A"
        ):

            direction = "B_TO_A"

        else:
            return


        # ======================================
        # HITUNG WAKTU
        # ======================================

        frame_difference = (
            frame_ke
            -
            first_frame
        )

        if (
            frame_difference <= 0
            or self.fps <= 0
        ):
            return

        travel_time_seconds = (
            frame_difference
            /
            self.fps
        )


        # ======================================
        # HITUNG KECEPATAN
        # ======================================

        speed_mps = (
            self.distance_meters
            /
            travel_time_seconds
        )

        speed_kmh = (
            speed_mps
            *
            3.6
        )


        # ======================================
        # SIMPAN HASIL
        # ======================================

        self.vehicle_speeds[
            track_id
        ] = {
            "speed_kmh": speed_kmh,
            "direction": direction,
        }


        print(
            f"[SPEED] ID {track_id} "
            f"({vehicle_label}) "
            f"= {speed_kmh:.2f} km/jam "
            f"| arah {direction} "
            f"| waktu "
            f"{travel_time_seconds:.2f} detik "
            f"| frame "
            f"{first_frame} -> {frame_ke}"
        )


    # ==========================================
    # UPDATE
    # ==========================================

    def update(
        self,
        result,
        frame_ke,
        vehicle_tracker=None,
    ):

        for box in result.boxes:

            if box.id is None:
                continue

            track_id = int(
                box.id[0]
            )

            cls = int(
                box.cls[0]
            )

            class_name = (
                CLASS_NAMES[cls]
            )

            if (
                class_name
                not in VEHICLE_CLASSES
            ):
                continue


            # ==================================
            # LABEL KENDARAAN
            # ==================================

            vehicle_label = (
                VEHICLE_CLASSES[
                    class_name
                ]["label"]
            )

            if vehicle_tracker is not None:

                stable_label = (
                    vehicle_tracker
                    .get_vehicle_label(
                        track_id
                    )
                )

                if (
                    stable_label
                    is not None
                ):
                    vehicle_label = (
                        stable_label
                    )


            # ==================================
            # TITIK KENDARAAN
            # ==================================

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            current_point = (
                (x1 + x2) // 2,
                y2,
            )

            old_point = (
                self.previous_point.get(
                    track_id
                )
            )

            if old_point is None:

                self.previous_point[
                    track_id
                ] = current_point

                continue


            # ==================================
            # CEK SPEED LINE A
            # ==================================

            crossed_line_a = (
                self._crossed_line(
                    old_point,
                    current_point,
                    self.line_a_start,
                    self.line_a_end,
                )
            )


            # ==================================
            # CEK SPEED LINE B
            # ==================================

            crossed_line_b = (
                self._crossed_line(
                    old_point,
                    current_point,
                    self.line_b_start,
                    self.line_b_end,
                )
            )

            if crossed_line_a or crossed_line_b:

                print(
                    f"[SPEED DEBUG] "
                    f"ID {track_id} "
                    f"| jenis={vehicle_label} "
                    f"| crossed_A={crossed_line_a} "
                    f"| crossed_B={crossed_line_b} "
                    f"| point={current_point}"
                )


            # ==================================
            # JIKA MENYENTUH LINE A
            # ==================================

            if crossed_line_a:

                if (
                    track_id
                    not in self.first_crossing
                ):

                    self._register_first_crossing(
                        track_id,
                        "A",
                        frame_ke,
                        vehicle_label,
                    )

                else:

                    self._calculate_if_complete(
                        track_id,
                        "A",
                        frame_ke,
                        vehicle_label,
                    )


            # ==================================
            # JIKA MENYENTUH LINE B
            # ==================================

            if crossed_line_b:

                if (
                    track_id
                    not in self.first_crossing
                ):

                    self._register_first_crossing(
                        track_id,
                        "B",
                        frame_ke,
                        vehicle_label,
                    )

                else:

                    self._calculate_if_complete(
                        track_id,
                        "B",
                        frame_ke,
                        vehicle_label,
                    )


            # ==================================
            # SIMPAN POSISI
            # ==================================

            self.previous_point[
                track_id
            ] = current_point


    # ==========================================
    # GET SPEED PER ID
    # ==========================================

    def get_speed(
        self,
        track_id,
    ):

        result = (
            self.vehicle_speeds.get(
                track_id
            )
        )

        if result is None:
            return None

        return result["speed_kmh"]


    # ==========================================
    # GET DIRECTION PER ID
    # ==========================================

    def get_direction(
        self,
        track_id,
    ):

        result = (
            self.vehicle_speeds.get(
                track_id
            )
        )

        if result is None:
            return None

        return result["direction"]


    # ==========================================
    # GET FULL RESULT PER ID
    # ==========================================

    def get_result(
        self,
        track_id,
    ):

        return (
            self.vehicle_speeds.get(
                track_id
            )
        )


    # ==========================================
    # GET SEMUA SPEED
    # ==========================================

    def get_all_speeds(
        self,
    ):

        return (
            self.vehicle_speeds.copy()
        )