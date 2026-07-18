import cv2
#import numpy as np
from layout import *
from draw import *
from processing import *
from utils import *
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
import time
from csv_logger import CSVLogger
from database_logger import DatabaseLogger
from speed_estimator import SpeedEstimator



video = cv2.VideoCapture("data/pak_kasih.dav")

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

#################

while True:

    ret, frame = video.read()

    if not ret:
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

video.release()
cv2.destroyAllWindows()