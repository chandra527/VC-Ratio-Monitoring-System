from yolo_detector import (
    CLASS_NAMES,
    VEHICLE_CLASSES,
)


def record_track_timelines(
    result,
    frame_number,
    timeline_debugger,
    virtual_gate,
    debug_track_ids,
):
    """
    Mencatat timeline hanya untuk Track ID yang sedang
    diinvestigasi.

    Fungsi ini tidak mengubah state Virtual Gate,
    trajectory, tracking, atau counter.
    """

    if result.boxes is None:
        return

    debug_track_ids = set(
        int(track_id)
        for track_id in debug_track_ids
    )

    for box in result.boxes:

        if box.id is None:
            continue

        track_id = int(box.id[0])

        if track_id not in debug_track_ids:
            continue

        class_id = int(box.cls[0])
        class_name = CLASS_NAMES[class_id]

        if class_name not in VEHICLE_CLASSES:
            continue

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0],
        )

        bottom_center = (
            (x1 + x2) // 2,
            y2,
        )

        signed_distance = (
            virtual_gate.get_signed_distance(
                bottom_center
            )
        )

        side = virtual_gate.get_side(
            bottom_center
        )

        timeline_debugger.record(
            track_id=track_id,
            frame_number=frame_number,
            point=bottom_center,
            signed_distance=signed_distance,
            side=side,
        )