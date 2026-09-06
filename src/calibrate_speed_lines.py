import cv2

from config import VIDEO_PATH


points = []

point_names = [
    "SPEED_LINE_A_START",
    "SPEED_LINE_A_END",
    "SPEED_LINE_B_START",
    "SPEED_LINE_B_END",
]


def mouse_callback(
    event,
    x,
    y,
    flags,
    param,
):

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    if len(points) >= 4:
        return

    points.append((x, y))

    index = len(points) - 1

    print(
        f"{point_names[index]} = ({x}, {y})"
    )


source = str(VIDEO_PATH)

video = cv2.VideoCapture(
    source,
    cv2.CAP_FFMPEG,
)

if not video.isOpened():
    raise RuntimeError(
        "Gagal membuka kamera."
    )


# Ambil satu frame terbaru
frame = None

for _ in range(20):

    success, current_frame = video.read()

    if success:
        frame = current_frame


video.release()


if frame is None:
    raise RuntimeError(
        "Tidak berhasil mengambil frame kamera."
    )


window_name = "Speed Line Calibration"

cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL,
)

cv2.setMouseCallback(
    window_name,
    mouse_callback,
)


while True:

    display = frame.copy()

    # Titik yang sudah diklik
    for index, point in enumerate(points):

        cv2.circle(
            display,
            point,
            8,
            (0, 0, 255),
            -1,
        )

        cv2.putText(
            display,
            str(index + 1),
            (
                point[0] + 10,
                point[1] - 10,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

    # Gambar Line A
    if len(points) >= 2:

        cv2.line(
            display,
            points[0],
            points[1],
            (255, 0, 0),
            3,
            cv2.LINE_AA,
        )

    # Gambar Line B
    if len(points) >= 4:

        cv2.line(
            display,
            points[2],
            points[3],
            (0, 255, 0),
            3,
            cv2.LINE_AA,
        )

    cv2.putText(
        display,
        "Klik: A_START -> A_END -> B_START -> B_END",
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
    )

    cv2.putText(
        display,
        "R = reset | ESC = keluar",
        (30, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )

    cv2.imshow(
        window_name,
        display,
    )

    key = cv2.waitKey(20) & 0xFF

    if key == 27:
        break

    if key == ord("r"):
        points.clear()
        print("Kalibrasi di-reset.")


cv2.destroyAllWindows()


print()
print("=" * 50)
print("HASIL KALIBRASI")
print("=" * 50)

if len(points) == 4:

    print(
        '"speed_line_a_start": '
        f'{points[0]},'
    )

    print(
        '"speed_line_a_end": '
        f'{points[1]},'
    )

    print(
        '"speed_line_b_start": '
        f'{points[2]},'
    )

    print(
        '"speed_line_b_end": '
        f'{points[3]},'
    )

else:

    print(
        "Belum ada 4 titik lengkap."
    )