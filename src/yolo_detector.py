from ultralytics import YOLO
import cv2
from layout import *

model = YOLO("models/yolov8n.pt")

CLASS_NAMES = model.names

# ==========================================
# VEHICLE CLASS
# ==========================================

VEHICLE_CLASSES = {

    "motorcycle": {

        "label": "Motor",

        "key": "motor"

    },

    "car": {

        "label": "Mobil",

        "key": "mobil"

    },

    "bus": {

        "label": "Bus",

        "key": "bus"

    },

    "truck": {

        "label": "Truk",

        "key": "truk"

    },

    "ambulance": {

        "label": "Ambulans",

        "key": "ambulans"

    }

}


def detect(frame):

    #results = model(frame)
    results = model(

        frame,

        imgsz=960,

        conf=0.15,

        verbose=False
    )

    return results[0]


def count_vehicle(result):

    vehicle_data = {

        "motor": 0,

        "mobil": 0,

        "bus": 0,

        "truk": 0,

        "ambulans": 0

    }


    for box in result.boxes:

        cls = int(box.cls[0])

        class_name = CLASS_NAMES[cls]
        #print(class_name)

        if class_name not in VEHICLE_CLASSES:
            continue

        key = VEHICLE_CLASSES[class_name]["key"]

        vehicle_data[key] += 1

    return vehicle_data


def draw_corner_box(frame, x1, y1, x2, y2):

    l = CORNER_LENGTH
    t = BOX_THICKNESS
    c = BOX_COLOR

    # kiri atas
    cv2.line(frame,(x1,y1),(x1+l,y1),c,t)
    cv2.line(frame,(x1,y1),(x1,y1+l),c,t)

    # kanan atas
    cv2.line(frame,(x2,y1),(x2-l,y1),c,t)
    cv2.line(frame,(x2,y1),(x2,y1+l),c,t)

    # kiri bawah
    cv2.line(frame,(x1,y2),(x1+l,y2),c,t)
    cv2.line(frame,(x1,y2),(x1,y2-l),c,t)

    # kanan bawah
    cv2.line(frame,(x2,y2),(x2-l,y2),c,t)
    cv2.line(frame,(x2,y2),(x2,y2-l),c,t)

def draw_detection(frame, result):

    for box in result.boxes:

        x1,y1,x2,y2 = map(int, box.xyxy[0])

        conf = float(box.conf[0])

        cls = int(box.cls[0])
        print(box.id)

        track_id = None

        if box.id is not None:
            track_id = int(box.id[0])

        
        class_name = CLASS_NAMES[cls]

        
        if class_name not in VEHICLE_CLASSES:
            continue

        label = VEHICLE_CLASSES[class_name]["label"]
        print(f"ID = {track_id}, Label = {label}")

        if track_id is None:
            text = label
            
        else:
            text = f"{label} #{track_id}"
            
                        

        #text = f"{label} {conf*100:.0f}%"
        #text = label
        print(text)

        draw_corner_box(

            frame,

            x1,

            y1,

            x2,

            y2

        )

        draw_label(

            frame,

            text,

            x1,

            y1

        )
       

    return frame


def draw_label(frame, text, x, y):

    (w,h), baseline = cv2.getTextSize(

        text,

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        2

    )

    cv2.rectangle(

        frame,

        (x, y-h-10),

        (x+w+10, y),

        LABEL_BG_COLOR,

        -1

    )

    cv2.putText(

        frame,

        text,

        (x+5, y-5),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.5,

        LABEL_TEXT_COLOR,

        2

    )