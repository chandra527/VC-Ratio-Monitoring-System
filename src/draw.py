import cv2
import numpy as np

from layout import *
from utils import *
from config import ACTIVE_CAMERA_NAME

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
    frame_kecil
):

    dashboard[
        VIDEO_Y:VIDEO_Y + VIDEO_HEIGHT,
        VIDEO_X:VIDEO_X + VIDEO_WIDTH
    ] = frame_kecil

    return dashboard


# =====================================================
# DRAW VIDEO FRAME
# =====================================================

def draw_video_frame(dashboard):

    cv2.rectangle(
        dashboard,

        (
            VIDEO_X - 2,
            VIDEO_Y - 2
        ),

        (
            VIDEO_X + VIDEO_WIDTH + 2,
            VIDEO_Y + VIDEO_HEIGHT + 2
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
        SUMMARY_LINE_BOTTOM_Y
    ]

    for y in horizontal_lines:

        cv2.line(
            dashboard,
            (0, y),
            (DASHBOARD_WIDTH, y),
            WHITE,
            THICKNESS_LINE
        )

    # Garis vertikal pemisah dua kelompok ringkasan
    cv2.line(
        dashboard,
        (SUMMARY_MIDDLE_X, LINE_INFO),
        (SUMMARY_MIDDLE_X, SUMMARY_LINE_BOTTOM_Y),
        WHITE,
        THICKNESS_LINE
    )

    return dashboard


# =====================================================
# DRAW HEADER
# =====================================================

def draw_header(dashboard):

    # Judul utama
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

    # Nama kamera
    text = f"Camera : {ACTIVE_CAMERA_NAME}"

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

    # Judul video utama
    video_title = "LIVE TRAFFIC CAMERA"

    video_title_size, _ = cv2.getTextSize(
        video_title,
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SUBTITLE,
        THICKNESS_TEXT
    )

    video_title_x = (
        VIDEO_X
        + get_center_x(
            VIDEO_WIDTH,
            video_title_size[0]
        )
    )

    cv2.putText(
        dashboard,
        video_title,
        (video_title_x, VIDEO_TITLE_Y),
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
    text = "Traffic Monitoring & VC Ratio System | Development Version"

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

def draw_compact_summary(
    dashboard,
    vehicle_data,
    latest_volume_smp_per_hour,
    road_capacity,
    latest_vc_ratio,
    latest_status,
    latest_status_color,
):

    # =====================================
    # JUDUL PANEL
    # =====================================

    vehicle_title = "VEHICLE COUNT"

    vehicle_title_size, _ = cv2.getTextSize(
        vehicle_title,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        1
    )

    vehicle_title_x = get_center_x(
        SUMMARY_MIDDLE_X,
        vehicle_title_size[0]
    )

    cv2.putText(
        dashboard,
        vehicle_title,
        (vehicle_title_x, SUMMARY_TITLE_Y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        YELLOW,
        1
    )

    traffic_title = "TRAFFIC ANALYSIS"

    traffic_title_size, _ = cv2.getTextSize(
        traffic_title,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        1
    )

    traffic_title_x = (
        SUMMARY_MIDDLE_X
        + get_center_x(
            DASHBOARD_WIDTH - SUMMARY_MIDDLE_X,
            traffic_title_size[0]
        )
    )

    cv2.putText(
        dashboard,
        traffic_title,
        (traffic_title_x, SUMMARY_TITLE_Y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        YELLOW,
        1
    )

    # =====================================
    # VEHICLE COUNT
    # =====================================

    vehicle_columns = [
        (35,  "Motor", vehicle_data["motor"]),
        (130, "Mobil", vehicle_data["mobil"]),
        (225, "Bus",   vehicle_data["bus"]),
        (315, "Truk",  vehicle_data["truk"]),
        (400, "Total", vehicle_data["total"])
    ]

    for x, label, value in vehicle_columns:

        label_text = f"{label}:"

        cv2.putText(
            dashboard,
            label_text,
            (x, SUMMARY_VALUE_Y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            WHITE,
            1
        )

        label_size, _ = cv2.getTextSize(
            label_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            1
        )

        cv2.putText(
            dashboard,
            str(value),
            (x + label_size[0] + 8, SUMMARY_VALUE_Y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            GREEN,
            2
        )

    # =====================================
    # TRAFFIC ANALYSIS
    # =====================================

    traffic_columns = [
        (
            500,
            "Volume",
            f"{latest_volume_smp_per_hour:.2f}",
            GREEN
        ),
        (
            610,
            "Capacity",
            f"{road_capacity:.2f}",
            GREEN
        ),
        (
            735,
            "V/C",
            f"{latest_vc_ratio:.2f}",
            GREEN
        ),
        (
            840,
            "Status",
            latest_status,
            latest_status_color
        )
    ]

    for x, label, value, value_color in traffic_columns:

        label_text = f"{label}:"

        cv2.putText(
            dashboard,
            label_text,
            (x, SUMMARY_VALUE_Y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            WHITE,
            1
        )

        label_size, _ = cv2.getTextSize(
            label_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            1
        )

        cv2.putText(
            dashboard,
            str(value),
            (x + label_size[0] + 6, SUMMARY_VALUE_Y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            value_color,
            2
        )

    return dashboard

def draw_trajectories(
    frame,
    trajectory_engine,
    active_track_ids,
    debug_track_ids=None,
    show_only_debug=False,
    keep_debug_visible=True,
):
    """
    Menggambar trajectory kendaraan aktif.

    debug_track_ids:
        ID yang ingin disorot merah.

    show_only_debug:
        Jika True, hanya trajectory ID debug
        yang ditampilkan.
    """

    debug_track_ids = set(
        debug_track_ids or []
    )

    trajectories = (
        trajectory_engine
        .get_all_trajectories()
    )

    track_ids_to_draw = set(
    active_track_ids
    )

    if keep_debug_visible:
        track_ids_to_draw.update(
            debug_track_ids
        )

    #for track_id in active_track_ids:
    for track_id in track_ids_to_draw:

        is_debug_track = (
            track_id in debug_track_ids
        )

        if (
            show_only_debug
            and not is_debug_track
        ):
            continue

        points = trajectories.get(
            track_id,
            [],
        )

        if len(points) < 2:
            continue

        # Merah untuk ID audit,
        # kuning untuk kendaraan biasa.
        line_color = (
            (0, 0, 255)
            if is_debug_track
            else (0, 255, 255)
        )

        line_thickness = (
            8
            if is_debug_track
            else 2
        )

        for index in range(
            1,
            len(points),
        ):
            previous_point = points[
                index - 1
            ]

            current_point = points[
                index
            ]

            cv2.line(
                frame,
                previous_point,
                current_point,
                line_color,
                line_thickness,
                cv2.LINE_AA,
            )

        current_point = points[-1]

        if is_debug_track:
            for point in points:
                cv2.circle(
                    frame,
                    point,
                    6,
                    (0, 0, 255),
                    -1,
                    cv2.LINE_AA,
                )

        cv2.circle(
            frame,
            current_point,
            12 if is_debug_track else 4,
            line_color,
            -1,
            cv2.LINE_AA,
        )

        if is_debug_track:
            label_position = (
                current_point[0] + 10,
                current_point[1] - 10,
            )

            cv2.putText(
                frame,
                f"DEBUG ID #{track_id}",
                label_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

    return frame

def draw_virtual_gate(
    frame,
    virtual_gate,
):
    """
    Menggambar Virtual Gate sebagai garis kuning.
    """

    cv2.line(
        frame,
        virtual_gate.start_point,
        virtual_gate.end_point,
        (0, 255, 255),
        3,
        cv2.LINE_AA,
    )

    label_x = virtual_gate.start_point[0] + 10
    label_y = virtual_gate.start_point[1] - 20

    cv2.putText(
        frame,
        "VIRTUAL GATE OBSERVER",
        (label_x, label_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return frame

def draw_virtual_gate_summary(
    frame,
    virtual_gate_count,
):
    """
    Menampilkan ringkasan observer Virtual Gate.

    Panel ini hanya sebagai pembanding.
    Belum mengganti counter utama.
    """

    a_to_b = virtual_gate_count.get(
        "A_TO_B",
        0,
    )

    b_to_a = virtual_gate_count.get(
        "B_TO_A",
        0,
    )

    total = a_to_b + b_to_a

    x = 15
    y = frame.shape[0] - 95

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (x - 5, y - 25),
        (x + 170, y + 65),
        (0, 0, 0),
        -1,
    )

    cv2.addWeighted(
        overlay,
        0.45,
        frame,
        0.55,
        0,
        frame,
    )

    cv2.putText(
        frame,
        "VIRTUAL GATE",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"A -> B : {a_to_b}",
        (x, y + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255,255,255),
        1,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"B -> A : {b_to_a}",
        (x, y + 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255,255,255),
        1,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"TOTAL : {total}",
        (x, y + 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0,255,0),
        2,
        cv2.LINE_AA,
    )

    return frame