from yolo_detector import model


def track(frame):

    results = model.track(

        frame,

        persist=True,

        verbose=False,

        imgsz=960,

        conf=0.15

    )

    return results[0]