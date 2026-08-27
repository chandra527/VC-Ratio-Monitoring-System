from math import hypot


class VirtualGate:
    """
    Garis virtual yang dibentuk oleh dua titik.

    Pada tahap ini VirtualGate hanya mendeteksi
    perpindahan trajectory dari satu sisi garis
    ke sisi lainnya. Belum menambah counter.
    """

    SIDE_A = "SIDE_A"
    SIDE_B = "SIDE_B"
    ON_GATE = "ON_GATE"

    A_TO_B = "A_TO_B"
    B_TO_A = "B_TO_A"

    def __init__(
        self,
        start_point,
        end_point,
        tolerance=5,
    ):
        self.start_point = tuple(start_point)
        self.end_point = tuple(end_point)
        self.tolerance = tolerance

        start_x, start_y = self.start_point
        end_x, end_y = self.end_point

        self.length = hypot(
            end_x - start_x,
            end_y - start_y,
        )

        if self.length == 0:
            raise ValueError(
                "Titik awal dan akhir VirtualGate "
                "tidak boleh sama."
            )

    def get_signed_distance(self, point):
        """
        Menghasilkan jarak bertanda titik terhadap garis.
        Tanda positif/negatif menunjukkan sisi berbeda.
        """

        start_x, start_y = self.start_point
        end_x, end_y = self.end_point
        point_x, point_y = point

        cross_product = (
            (end_x - start_x)
            * (point_y - start_y)
            - (end_y - start_y)
            * (point_x - start_x)
        )

        return cross_product / self.length

    def intersects_segment(
        self,
        previous_point,
        current_point,
    ):
        """
        Mengecek apakah trajectory kendaraan
        benar-benar memotong segmen Virtual Gate.

        Bukan sekadar memotong perpanjangan
        garis Virtual Gate.
        """

        if (
            previous_point is None
            or current_point is None
        ):
            return False

        p_x, p_y = previous_point
        r_x = current_point[0] - p_x
        r_y = current_point[1] - p_y

        q_x, q_y = self.start_point
        s_x = self.end_point[0] - q_x
        s_y = self.end_point[1] - q_y

        denominator = (
            r_x * s_y
            - r_y * s_x
        )

        # Paralel / tidak memiliki
        # titik potong yang jelas.
        if denominator == 0:
            return False

        q_minus_p_x = q_x - p_x
        q_minus_p_y = q_y - p_y

        t = (
            q_minus_p_x * s_y
            - q_minus_p_y * s_x
        ) / denominator

        u = (
            q_minus_p_x * r_y
            - q_minus_p_y * r_x
        ) / denominator

        return (
            0.0 <= t <= 1.0
            and 0.0 <= u <= 1.0
        )

    def get_side(self, point):
        signed_distance = self.get_signed_distance(
            point
        )

        if abs(signed_distance) <= self.tolerance:
            return self.ON_GATE

        if signed_distance > 0:
            return self.SIDE_A

        return self.SIDE_B

    def detect_crossing(
        self,
        previous_point,
        current_point,
    ):
        """
        Mengembalikan A_TO_B, B_TO_A, atau None.
        """

        if (
            previous_point is None
            or current_point is None
        ):
            return None

        previous_side = self.get_side(
            previous_point
        )

        current_side = self.get_side(
            current_point
        )

        if (
            previous_side == self.SIDE_A
            and current_side == self.SIDE_B
        ):
            return self.A_TO_B

        if (
            previous_side == self.SIDE_B
            and current_side == self.SIDE_A
        ):
            return self.B_TO_A

        return None