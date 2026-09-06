from collections import Counter

from yolo_detector import CLASS_NAMES
from yolo_detector import VEHICLE_CLASSES


class VehicleTracker:
    """
    Menstabilkan jenis kendaraan per Tracking ID melalui voting kelas.

    Catatan:
    - Tidak melakukan counting garis legacy.
    - Counting dan arah kendaraan sepenuhnya ditangani Virtual Gate.
    """

    def __init__(self, min_track_frames=3):
        self.min_track_frames = min_track_frames

        # Jumlah kemunculan setiap Tracking ID.
        self.track_frames = {}

        # Voting jenis kendaraan setiap Tracking ID.
        self.class_votes = {}

    def update(self, result):
        """Memperbarui voting kelas kendaraan untuk setiap Tracking ID."""

        if result.boxes is None:
            return

        for box in result.boxes:
            if box.id is None:
                continue

            track_id = int(box.id[0])
            cls = int(box.cls[0])

            class_name = CLASS_NAMES[cls]

            if class_name not in VEHICLE_CLASSES:
                continue

            detected_key = VEHICLE_CLASSES[class_name]["key"]

            self.track_frames[track_id] = (
                self.track_frames.get(track_id, 0) + 1
            )

            if track_id not in self.class_votes:
                self.class_votes[track_id] = Counter()

            self.class_votes[track_id][detected_key] += 1

    def get_vehicle_label(self, track_id):
        """Mengembalikan hasil voting jenis kendaraan untuk Tracking ID."""

        if track_id not in self.class_votes:
            return None

        return self.class_votes[track_id].most_common(1)[0][0]

    def is_track_stable(self, track_id):
        """Menandai apakah Tracking ID sudah muncul cukup banyak frame."""

        return (
            self.track_frames.get(track_id, 0)
            >= self.min_track_frames
        )
