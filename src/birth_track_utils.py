from yolo_detector import CLASS_NAMES
from yolo_detector import VEHICLE_CLASSES


def record_birth_tracks(
    result,
    frame_number,
    birth_logger,
    virtual_gate,
):
    """
    Membaca hasil ByteTrack dan merekam
    kemunculan pertama setiap tracking ID.

    Fungsi ini hanya mencatat data investigasi.
    Tidak memengaruhi counting.
    """

    if result.boxes is None:
        return

    for box in result.boxes:

        if box.id is None:
            continue

        track_id = int(box.id[0])
        class_id = int(box.cls[0])

        class_name = CLASS_NAMES[class_id]

        if class_name not in VEHICLE_CLASSES:
            continue

        vehicle_type = (
            VEHICLE_CLASSES[class_name]["key"]
        )

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0],
        )

        bottom_center = (
            (x1 + x2) // 2,
            y2,
        )

        first_side = virtual_gate.get_side(
            bottom_center
        )

        birth_logger.record(
            track_id=track_id,
            frame_number=frame_number,
            point=bottom_center,
            side=first_side,
            vehicle_type=vehicle_type,
        )