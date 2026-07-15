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
    draw_counting_line
)

video = cv2.VideoCapture("data/pak_kasih.dav")

frame_ke = 0
fps = video.get(cv2.CAP_PROP_FPS)

#panel_Vehicle_Count
vehicle_data = create_vehicle_data()

#panel_Traffic_Analysis
traffic_data = create_traffic_data()

#tracker = VehicleTracker()

tracker = None

#################

while True:
    
    ret, frame = video.read()

    if not ret:
        break

    frame_ke += 1

    # Dibuat satu kali berdasarkan ukuran frame asli
    if tracker is None:

        line_y = get_counting_line_y(frame)

        tracker = VehicleTracker(line_y)

    result = track(frame)

    tracker.update(result)

    vehicle_data = tracker.get_vehicle_data()

    vehicle_data, traffic_data = update_traffic_data(
        vehicle_data,
        traffic_data
    )

    frame = draw_detection(
        frame,
        result
    )

    frame = draw_counting_line(
        frame,
        tracker.line_y
    )


    tinggi, lebar = frame.shape[:2]
        
    gray = convert_to_gray(frame)

    frame_kecil = resize_frame(frame)

    gray_kecil = resize_frame(gray)

    dashboard = create_dashboard()
        
    # Tempel video kiri & kanan
    dashboard = draw_video(
    dashboard,
    frame_kecil,
    gray_kecil
    )

    # Bingkai video kiri & kanan
    dashboard = draw_video_frame(dashboard)
    
    #line
    dashboard = draw_lines(dashboard)

    #judul_header
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

    
    dashboard = draw_vehicle_panel(
    dashboard,
    vehicle_data
    )

            
    dashboard = draw_analysis_panel(
    dashboard,
    traffic_data
    )
    
    #footer
    dashboard = draw_footer(dashboard)

     
    # Menampilkan dashboard
    cv2.imshow("VC Ratio Monitoring", dashboard)

    # Keluar jika tombol q ditekan
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()