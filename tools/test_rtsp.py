import cv2
import time

RTSP_URL = "rtsp://admin:T3LKOM@ptk@172.16.3.122:554/cam/realmonitor?channel=1&subtype=0"


print("Mencoba membuka RTSP...")

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    raise RuntimeError("RTSP gagal dibuka.")

print("RTSP berhasil terhubung.")

frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()

    if not ret or frame is None:
        print("Gagal membaca frame dari RTSP.")
        break

    frame_count += 1

    cv2.putText(
        frame,
        f"Frame: {frame_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("RTSP Connection Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

elapsed = time.time() - start_time

print(f"Frame terbaca : {frame_count}")
print(f"Waktu         : {elapsed:.2f} detik")

cap.release()
cv2.destroyAllWindows()