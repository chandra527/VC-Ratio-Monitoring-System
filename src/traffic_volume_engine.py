class TrafficVolumeEngine:
    """
    Menghitung volume lalu lintas berdasarkan
    jumlah kendaraan dalam window waktu tertentu.

    Hasil volume dinyatakan dalam smp/jam.
    """

    EMP = {
        "motor": 0.4,
        "mobil": 1.0,
        "bus": 1.3,
        "truk": 1.3,
    }

    def __init__(
        self,
        window_seconds=60,
    ):
        self.window_seconds = window_seconds

        self.counts = {
            "motor": 0,
            "mobil": 0,
            "bus": 0,
            "truk": 0,
        }

    def add_vehicle(
        self,
        vehicle_type,
    ):
        """
        Menambahkan satu kendaraan
        ke window pengamatan saat ini.
        """

        if vehicle_type not in self.counts:
            return

        self.counts[
            vehicle_type
        ] += 1

    def get_total_smp(self):
        """
        Menghitung total smp dalam
        window pengamatan.
        """

        total_smp = 0.0

        for vehicle_type, count in self.counts.items():

            emp = self.EMP[
                vehicle_type
            ]

            total_smp += (
                count * emp
            )

        return total_smp

    def get_volume_per_hour(self):
        """
        Mengkonversi jumlah smp
        dalam window menjadi smp/jam.
        """

        total_smp = (
            self.get_total_smp()
        )

        if self.window_seconds <= 0:
            return 0.0

        return (
            total_smp
            / self.window_seconds
            * 3600
        )

    def reset(self):
        """
        Mengosongkan counter
        untuk window berikutnya.
        """

        for vehicle_type in self.counts:
            self.counts[
                vehicle_type
            ] = 0


