from yolo_detector import model


def track(frame):

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False,
        imgsz=960,
        conf=0.15,
        classes=[2, 3, 5, 7]
    )

    return results[0]