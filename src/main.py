import cv2
import time
import os
#import numpy as np
from layout import *
from draw import *
from processing import *
from utils import *
from utils import show_banner
from yolo_detector import detect, count_vehicle
from yolo_detector import draw_detection
from tracker import track
from vehicle_tracker import VehicleTracker
from line_counter import (
    get_counting_line_y,
    draw_counting_line,
    get_speed_line_a_y,
    draw_speed_line_a
)


from csv_logger import CSVLogger
from database_logger import DatabaseLogger
from speed_estimator import SpeedEstimator
from config import VIDEO_PATH, MODEL_PATH


selected_device = get_selected_device()
show_banner(selected_device)

video = cv2.VideoCapture(
    VIDEO_PATH
)


frame_ke = 0
fps = video.get(cv2.CAP_PROP_FPS)

#panel_Vehicle_Count
vehicle_data = create_vehicle_data()

#panel_Traffic_Analysis
traffic_data = create_traffic_data()

#tracker = VehicleTracker()

tracker = None
speed_estimator = None

WINDOW_NAME = "VC Ratio Monitoring"

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_AUTOSIZE
)


cv2.moveWindow(
    WINDOW_NAME,
    10,
    10
)

csv_logger = CSVLogger()

database_logger = DatabaseLogger()

SAVE_INTERVAL_SECONDS = 60

last_save_time = time.time()

benchmark_start_time = time.perf_counter()

benchmark_completed = False

#################

while True:

    ret, frame = video.read()

    if not ret:
        benchmark_completed = True
        break

    frame_ke += 1

    if tracker is None:

        # Garis akhir speed sekaligus garis utama counting
        line_b_y = get_counting_line_y(frame)

        # Garis awal speed, 100 piksel di atas Line B
        line_a_y = get_speed_line_a_y(line_b_y)

        tracker = VehicleTracker(
        line_y=line_b_y
        )

        speed_estimator = SpeedEstimator(
        line_a_y=line_a_y,
        line_b_y=line_b_y,
        fps=fps,
        distance_meters=10
        )



    result = track(frame)

    # VehicleTracker melakukan voting lebih dahulu
    tracker.update(result)

    # SpeedEstimator mengambil hasil voting tersebut
    speed_estimator.update(
    result,
    frame_ke,
    tracker
    )

    vehicle_data = tracker.get_vehicle_data()



    vehicle_data, traffic_data = update_traffic_data(
        vehicle_data,
        traffic_data
    )

    current_time = time.time()

    if (
        current_time - last_save_time
        >= SAVE_INTERVAL_SECONDS
    ):

        csv_logger.save(
        vehicle_data,
        traffic_data
        )

        database_logger.save(
        vehicle_data,
        traffic_data
        )

        last_save_time = current_time


    frame = draw_detection(
        frame,
        result,
        speed_estimator,
        tracker
    )

    frame = draw_speed_line_a(
        frame,
        speed_estimator.line_a_y
    )

    frame = draw_counting_line(
        frame,
        tracker.line_y
    )


    tinggi, lebar = frame.shape[:2]

    frame_kecil = resize_frame(frame)

    dashboard = create_dashboard()

    # Tempel satu video utama
    dashboard = draw_video(
    dashboard,
    frame_kecil
    )

    # Bingkai video utama
    dashboard = draw_video_frame(dashboard)

    # Garis layout
    dashboard = draw_lines(dashboard)

    # Header
    dashboard = draw_header(dashboard)

    # ==========================
    # Informasi Sistem  
    # ==========================
    dashboard = draw_system_information(
    dashboard,
    frame_ke,
    fps,
    lebar,
    tinggi
    )

    
    #dashboard = draw_vehicle_panel(
    #dashboard,
    #vehicle_data
    #)

            
    #dashboard = draw_analysis_panel(
    #dashboard,
    #traffic_data
    #)

    dashboard = draw_compact_summary(
    dashboard,
    vehicle_data,
    traffic_data
    )
    
    #footer
    dashboard = draw_footer(dashboard)

     
    # Menampilkan dashboard
    cv2.imshow(WINDOW_NAME, dashboard)

    # Keluar jika tombol q ditekan
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

benchmark_processing_seconds = (
    time.perf_counter() - benchmark_start_time
)

benchmark_average_fps = (
    frame_ke / benchmark_processing_seconds
    if benchmark_processing_seconds > 0
    else 0.0
)

benchmark_status = (
    "COMPLETED"
    if benchmark_completed
    else "STOPPED_BY_USER"
)


if frame_ke > 0:

    benchmark_processing_seconds = (
        time.perf_counter() - benchmark_start_time
    )

    benchmark_average_fps = (
        frame_ke / benchmark_processing_seconds
        if benchmark_processing_seconds > 0
        else 0.0
    )

    benchmark_status = (
        "COMPLETED"
        if benchmark_completed
        else "STOPPED_BY_USER"
    )

    database_logger.save_benchmark(
        model_name=os.path.basename(str(MODEL_PATH)),
        video_name=os.path.basename(str(VIDEO_PATH)),
        device=str(selected_device),
        run_status=benchmark_status,
        processed_frames=frame_ke,
        source_fps=fps,
        processing_seconds=benchmark_processing_seconds,
        average_fps=benchmark_average_fps,
        vehicle_data=vehicle_data,
        traffic_data=traffic_data,
        notes="Pengujian aplikasi VC Ratio pada server Dishub"
    )

    print()
    print("=" * 60)
    print("HASIL BENCHMARK")
    print("=" * 60)
    print(f"Model          : {os.path.basename(str(MODEL_PATH))}")
    print(f"Video          : {os.path.basename(str(VIDEO_PATH))}")
    print(f"Device         : {selected_device}")
    print(f"Status         : {benchmark_status}")
    print(f"Frame diproses : {frame_ke}")
    print(
        f"Waktu proses   : "
        f"{benchmark_processing_seconds:.2f} detik"
    )
    print(f"FPS rata-rata  : {benchmark_average_fps:.2f}")
    print(f"Motor          : {vehicle_data['motor']}")
    print(f"Mobil          : {vehicle_data['mobil']}")
    print(f"Bus            : {vehicle_data['bus']}")
    print(f"Truk           : {vehicle_data['truk']}")
    print(f"Ambulans       : {vehicle_data['ambulans']}")
    print(f"Total          : {vehicle_data['total']}")
    print(f"VC Ratio       : {traffic_data['vc_ratio']:.4f}")
    print(f"Status Jalan   : {traffic_data['status']}")
    print("=" * 60)

else:

    print(
        "BENCHMARK TIDAK DISIMPAN: "
        "tidak ada frame yang berhasil diproses."
    )


video.release()
cv2.destroyAllWindows()

video.release()
cv2.destroyAllWindows()