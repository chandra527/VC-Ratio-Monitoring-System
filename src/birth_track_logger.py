class BirthTrackLogger:
    """
    Menyimpan informasi kemunculan pertama
    setiap tracking ID.

    Modul ini hanya untuk investigasi.
    Tidak memengaruhi counting.
    """

    def __init__(self):
        self.birth_data = {}

    def record(
        self,
        track_id,
        frame_number,
        point,
        side=None,
        vehicle_type=None,
    ):
        """
        Menyimpan data hanya pada kemunculan pertama ID.
        """

        track_id = int(track_id)

        if track_id in self.birth_data:
            return

        self.birth_data[track_id] = {
            "track_id": track_id,
            "first_seen_frame": frame_number,
            "first_point": point,
            "first_side": side,
            "vehicle_type": vehicle_type,
        }

    def get(
        self,
        track_id,
    ):
        """
        Mengambil data kelahiran satu tracking ID.
        """

        return self.birth_data.get(
            int(track_id)
        )

    def has(
        self,
        track_id,
    ):
        return int(track_id) in self.birth_data

    def count(self):
        return len(self.birth_data)

    def remove(
        self,
        track_id,
    ):
        self.birth_data.pop(
            int(track_id),
            None,
        )

    def clear(self):
        self.birth_data.clear()