import cv2

from layout import *

from utils import calculate_total

#1
def convert_to_gray(frame):
    # Mengubah menjadi hitam putih
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )
    # Mengubah kembali menjadi 3 channel agar bisa digabung
    gray = cv2.cvtColor(
        gray,
        cv2.COLOR_GRAY2BGR
    )

    return gray

#2
def resize_frame(frame):

    return cv2.resize(
        frame,
        (VIDEO_WIDTH, VIDEO_HEIGHT)
    )


#3
def copy_frame(frame):

    return frame.copy()

#4
def gaussian_blur(frame):

    blur = cv2.GaussianBlur(
        frame,
        (5,5),
        0
    )

    return blur

#5
def edge_detection(frame):

    edge = cv2.Canny(
        frame,
        100,
        200
    )

    edge = cv2.cvtColor(
        edge,
        cv2.COLOR_GRAY2BGR
    )

    return edge





def update_vehicle_total(
    vehicle_data,
):
    """
    Memperbarui total kendaraan kumulatif.
    """

    vehicle_data["total"] = calculate_total(
        vehicle_data
    )

    return vehicle_data