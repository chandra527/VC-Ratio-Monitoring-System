from collections import defaultdict, deque


class TrajectoryEngine:
    """
    Menyimpan riwayat posisi bottom-center
    untuk setiap tracking ID.

    Modul ini belum melakukan counting.
    """

    def __init__(
        self,
        max_history=30,
    ):
        self.max_history = max_history

        self.track_history = defaultdict(
            lambda: deque(
                maxlen=self.max_history
            )
        )

    def update(
        self,
        track_id,
        point,
    ):
        """
        Menambahkan posisi terbaru satu tracking ID.

        Args:
            track_id: ID dari ByteTrack.
            point: Tuple koordinat (x, y).
        """

        self.track_history[
            track_id
        ].append(point)

    def get_trajectory(
        self,
        track_id,
    ):
        """
        Mengambil trajectory satu tracking ID.
        """

        return list(
            self.track_history.get(
                track_id,
                []
            )
        )

    def get_previous_point(
        self,
        track_id,
    ):
        """
        Mengambil titik sebelum posisi terbaru.
        """

        trajectory = self.track_history.get(
            track_id
        )

        if (
            trajectory is None
            or len(trajectory) < 2
        ):
            return None

        return trajectory[-2]

    def get_current_point(
        self,
        track_id,
    ):
        """
        Mengambil posisi terbaru.
        """

        trajectory = self.track_history.get(
            track_id
        )

        if not trajectory:
            return None

        return trajectory[-1]

    def get_all_trajectories(self):
        """
        Mengambil seluruh trajectory yang tersimpan.
        """

        return {
            track_id: list(points)
            for track_id, points
            in self.track_history.items()
        }

    def remove_track(
        self,
        track_id,
    ):
        """
        Menghapus riwayat satu tracking ID.
        """

        self.track_history.pop(
            track_id,
            None,
        )

    def clear(self):
        """
        Menghapus seluruh trajectory.
        """

        self.track_history.clear()