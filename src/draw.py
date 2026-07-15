import cv2
import numpy as np

from layout import *
from utils import *

# =====================================================
# CREATE DASHBOARD
# =====================================================

def create_dashboard():

    return np.zeros(
        (DASHBOARD_HEIGHT, DASHBOARD_WIDTH, 3),
        dtype=np.uint8
    )


# =====================================================
# DRAW VIDEO
# =====================================================

def draw_video(
    dashboard,
    frame_kecil,
    gray_kecil
):

    dashboard[
        VIDEO_LEFT_Y:VIDEO_LEFT_Y + VIDEO_HEIGHT,
        VIDEO_LEFT_X:VIDEO_LEFT_X + VIDEO_WIDTH
    ] = frame_kecil

    dashboard[
        VIDEO_RIGHT_Y:VIDEO_RIGHT_Y + VIDEO_HEIGHT,
        VIDEO_RIGHT_X:VIDEO_RIGHT_X + VIDEO_WIDTH
    ] = gray_kecil

    return dashboard


# =====================================================
# DRAW VIDEO FRAME
# =====================================================

def draw_video_frame(dashboard):

    cv2.rectangle(
        dashboard,
        (VIDEO_LEFT_X-2, VIDEO_LEFT_Y-2),
        (
            VIDEO_LEFT_X + VIDEO_WIDTH + 2,
            VIDEO_LEFT_Y + VIDEO_HEIGHT + 2
        ),
        WHITE,
        THICKNESS_BORDER
    )

    cv2.rectangle(
        dashboard,
        (VIDEO_RIGHT_X-2, VIDEO_RIGHT_Y-2),
        (
            VIDEO_RIGHT_X + VIDEO_WIDTH + 2,
            VIDEO_RIGHT_Y + VIDEO_HEIGHT + 2
        ),
        WHITE,
        THICKNESS_BORDER
    )

    return dashboard


# =====================================================
# DRAW LINES
# =====================================================

def draw_lines(dashboard):

    horizontal_lines = [

        LINE_HEADER,
        LINE_VIDEO,
        LINE_INFO,
        LINE_PANEL

    ]

    for y in horizontal_lines:

        cv2.line(

            dashboard,

            (0, y),

            (DASHBOARD_WIDTH, y),

            WHITE,

            THICKNESS_LINE

        )

    cv2.line(

        dashboard,

        (LINE_MIDDLE, LINE_INFO),

        (LINE_MIDDLE, MID_LINE_END_Y),

        WHITE,

        THICKNESS_LINE

    )

    return dashboard


# =====================================================
# DRAW HEADER
# =====================================================

def draw_header(dashboard):

    text = "VC RATIO MONITORING SYSTEM"

    text_size, _ = cv2.getTextSize(
    text,
    cv2.FONT_HERSHEY_DUPLEX,
    FONT_TITLE,
    THICKNESS_TITLE
    )

    title_x = get_center_x(
    DASHBOARD_WIDTH,
    text_size[0]
    )

    cv2.putText(

        dashboard,

        text,

        (title_x, TITLE_Y),

        cv2.FONT_HERSHEY_DUPLEX,

        FONT_TITLE,

        YELLOW,

        THICKNESS_TITLE

    )

    text = "Camera : Jl. Pak Kasih"

    text_size, _ = cv2.getTextSize(
    text,
    cv2.FONT_HERSHEY_SIMPLEX,
    FONT_FOOTER,
    THICKNESS_FOOTER
    )

    camera_x = get_center_x(
    DASHBOARD_WIDTH,
    text_size[0]
    )

    cv2.putText(

        dashboard,

        text,

        (camera_x, CAMERA_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_FOOTER,

        GRAY,

        THICKNESS_FOOTER

    )

    cv2.putText(

        dashboard,

        "CAMERA VIEW",

        (LEFT_TITLE_X, LEFT_TITLE_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_SUBTITLE,

        GREEN,

        THICKNESS_TEXT

    )

    cv2.putText(

        dashboard,

        "IMAGE PROCESSING",

        (RIGHT_TITLE_X, RIGHT_TITLE_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_SUBTITLE,

        GREEN,

        THICKNESS_TEXT

    )

    return dashboard


# =====================================================
# SYSTEM INFORMATION
# =====================================================

def draw_system_information(

    dashboard,

    frame_ke,

    fps,

    lebar,

    tinggi

):

    informasi = [

        ("Frame :", frame_ke, FRAME_LABEL_X, FRAME_VALUE_X),

        ("FPS :", f"{fps:.2f}", FPS_LABEL_X, FPS_VALUE_X),

        (

            "Resolution :",

            f"{lebar} x {tinggi}",

            RESOLUTION_LABEL_X,

            RESOLUTION_VALUE_X

        )

    ]

    for label, value, label_x, value_x in informasi:

        cv2.putText(

            dashboard,

            label,

            (label_x, INFO_Y),

            cv2.FONT_HERSHEY_SIMPLEX,

            FONT_TEXT,

            WHITE,

            THICKNESS_TEXT

        )

        cv2.putText(

            dashboard,

            str(value),

            (value_x, INFO_Y),

            cv2.FONT_HERSHEY_SIMPLEX,

            FONT_VALUE,

            GREEN,

            THICKNESS_TEXT

        )

    return dashboard

# =====================================================
# VEHICLE COUNT PANEL
# =====================================================

def draw_vehicle_panel(
    dashboard,
    vehicle_data
):

    # Judul Panel
    cv2.putText(

        dashboard,

        "VEHICLE COUNT",

        (VEHICLE_TITLE_X, VEHICLE_TITLE_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_SUBTITLE,

        WHITE,

        THICKNESS_TITLE

    )

    data = [

        ("Motor", vehicle_data["motor"]),

        ("Mobil", vehicle_data["mobil"]),

        ("Bus", vehicle_data["bus"]),

        ("Truk", vehicle_data["truk"]),

        ("Ambulans", vehicle_data["ambulans"])

    ]

    # Data Kendaraan
    
    y = VEHICLE_START_Y

    for nama, jumlah in data:

        # Label kendaraan
        cv2.putText(

            dashboard,

            nama,

            (VEHICLE_LABEL_X, y),

            cv2.FONT_HERSHEY_SIMPLEX,

            FONT_TEXT,

            WHITE,

            THICKNESS_TEXT

        )

        # Nilai kendaraan
        cv2.putText(

            dashboard,

            str(jumlah),

            (VEHICLE_VALUE_X, y),

            cv2.FONT_HERSHEY_SIMPLEX,

            FONT_VALUE,

            GREEN,

            THICKNESS_TEXT

        )

        y += VEHICLE_ROW_GAP

    # Hitung Total
    total = sum(data[1] for data in data)
    
    # Garis pemisah Total
   
    cv2.line(
    dashboard,
    (TOTAL_LINE_START_X, TOTAL_LINE_Y),
    (TOTAL_LINE_END_X, TOTAL_LINE_Y),
    GRAY,
    THICKNESS_LINE
    )

    # Label Total
    cv2.putText(

        dashboard,

        "TOTAL",

        (VEHICLE_LABEL_X, TOTAL_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_VALUE,

        YELLOW,

        THICKNESS_TITLE

    )

    # Nilai Total
    cv2.putText(

        dashboard,

        str(total),

        (VEHICLE_VALUE_X, TOTAL_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_VALUE,

        GREEN,

        THICKNESS_TITLE

    )

    return dashboard

# =====================================================
# TRAFFIC ANALYSIS PANEL
# =====================================================

def draw_analysis_panel(
    dashboard,
    traffic_data
):

    cv2.putText(

        dashboard,

        "TRAFFIC ANALYSIS",

        (ANALYSIS_TITLE_X, ANALYSIS_TITLE_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_SUBTITLE,

        WHITE,

        THICKNESS_TITLE

    )

    informasi = [

        ("Volume", traffic_data["volume"]),

        ("Capacity", traffic_data["capacity"]),

        ("VC Ratio", f'{traffic_data["vc_ratio"]:.2f}')

    ]

    y = ANALYSIS_START_Y

    for nama, nilai in informasi:

        cv2.putText(

            dashboard,

            nama,

            (ANALYSIS_LABEL_X, y),

            cv2.FONT_HERSHEY_SIMPLEX,

            FONT_TEXT,

            WHITE,

            THICKNESS_TEXT

        )

        cv2.putText(

            dashboard,

            str(nilai),

            (ANALYSIS_VALUE_X, y),

            cv2.FONT_HERSHEY_SIMPLEX,

            FONT_VALUE,

            GREEN,

            THICKNESS_TEXT

        )

        y += ANALYSIS_ROW_GAP

    # Garis Status
    cv2.line(
    dashboard,
    (STATUS_LINE_START_X, STATUS_LINE_Y),
    (STATUS_LINE_END_X, STATUS_LINE_Y),
    GRAY,
    THICKNESS_LINE
    )

    # Status Label
    cv2.putText(

        dashboard,

        "STATUS",

        (ANALYSIS_LABEL_X, STATUS_LABEL_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_VALUE,

        WHITE,

        THICKNESS_TITLE

    )

    # Status Value
    cv2.putText(

        dashboard,

        traffic_data["status"],

        (ANALYSIS_VALUE_X, STATUS_LABEL_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_VALUE,

        traffic_data["warna_status"],

        THICKNESS_TITLE

    )

    return dashboard

# =====================================================
# FOOTER
# =====================================================

def draw_footer(dashboard):

    #garis_footer
    cv2.line(
    dashboard,
    (FOOTER_LINE_START_X, FOOTER_LINE_Y),
    (FOOTER_LINE_END_X, FOOTER_LINE_Y),
    WHITE,
    THICKNESS_LINE
    )

    #tulisan_footer
    text = "Powered by OpenCV + YOLOv8 | Eggi Chandra"

    text_size, baseline = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_FOOTER,
        THICKNESS_FOOTER
    )

    text_width = text_size[0]

    #x = (DASHBOARD_WIDTH - text_width) // 2
    x = get_center_x(
    DASHBOARD_WIDTH,
    text_width
    )

    cv2.putText(

        dashboard,

        text,

        (x, FOOTER_Y),

        cv2.FONT_HERSHEY_SIMPLEX,

        FONT_FOOTER,

        GRAY,

        THICKNESS_FOOTER

    )

    return dashboard