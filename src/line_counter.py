import cv2


LINE_COLOR = (0, 0, 255)
ZONE_COLOR = (0, 255, 255)

LINE_THICKNESS = 2
LINE_TOLERANCE = 35


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