import cv2

LINE_COLOR = (0, 0, 255)
ZONE_COLOR = (0, 255, 255)

LINE_THICKNESS = 2
LINE_TOLERANCE = 35

SPEED_LINE_COLOR = (255, 0, 0)
SPEED_LINE_THICKNESS = 2

def get_counting_line_y(frame):

    tinggi = frame.shape[0]

    return int(tinggi * 0.50)


def draw_counting_line(frame, line_y):

    lebar = frame.shape[1]

    zone_top = line_y - LINE_TOLERANCE
    zone_bottom = line_y + LINE_TOLERANCE

    # Batas atas zona hitung
    cv2.line(
        frame,
        (0, zone_top),
        (lebar, zone_top),
        ZONE_COLOR,
        1
    )

    # Garis utama
    cv2.line(
        frame,
        (0, line_y),
        (lebar, line_y),
        LINE_COLOR,
        LINE_THICKNESS
    )

    # Batas bawah zona hitung
    cv2.line(
        frame,
        (0, zone_bottom),
        (lebar, zone_bottom),
        ZONE_COLOR,
        1
    )

    cv2.putText(
        frame,
        "COUNTING ZONE",
        (20, zone_top - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        LINE_COLOR,
        2
    )

    return frame

def get_speed_line_a_y(line_b_y):

    # Line A berada 100 piksel di atas Line B
    return line_b_y - 100


def draw_speed_line_a(frame, line_a_y):

    lebar = frame.shape[1]

    cv2.line(
        frame,
        (0, line_a_y),
        (lebar, line_a_y),
        SPEED_LINE_COLOR,
        SPEED_LINE_THICKNESS
    )

    cv2.putText(
        frame,
        "SPEED LINE A",
        (20, line_a_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        SPEED_LINE_COLOR,
        2
    )

    return frame