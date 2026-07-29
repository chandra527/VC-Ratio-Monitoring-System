from config import CONFIDENCE, IMAGE_SIZE
from yolo_detector import model


VEHICLE_CLASSES = [2, 3, 5, 7]


def track(frame):
    """
    Menjalankan deteksi dan tracking kendaraan pada satu frame.

    Class YOLO yang diproses:
    2 = car
    3 = motorcycle
    5 = bus
    7 = truck
    """

    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE,
        classes=VEHICLE_CLASSES,
    )

    return results[0]
