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
from config import (
    VIDEO_PATH,
    MODEL_PATH,
    ACTIVE_CAMERA,
    ACTIVE_CAMERA_NAME,
    DEBUG_TRACK_ENABLED,
    DEBUG_TRACK_IDS,
    SHOW_ONLY_DEBUG_TRACKS,
    KEEP_DEBUG_TRAJECTORY_VISIBLE,
    PERFORMANCE_AUDIT_ENABLED,
    PERFORMANCE_REPORT_INTERVAL_FRAMES,
    TIMELINE_DEBUG_ENABLED,
    TIMELINE_DEBUG_TRACK_IDS,
    GATE_CROSSING_COOLDOWN_FRAMES,
    GATE_REARM_DISTANCE,
    GATE_HYSTERESIS_DISTANCE,
    BIRTH_DEBUG_ENABLED,
    MULTI_CROSSING_DEBUG_ENABLED,
    ROAD_BASE_CAPACITY,
    ROAD_FC_WIDTH,
    ROAD_FC_DIRECTION,
    ROAD_FC_SIDE_FRICTION,
    ROAD_FC_CITY_SIZE,
    VIRTUAL_GATE_START_POINT,
    VIRTUAL_GATE_END_POINT,
    VC_TARGET_DIRECTION,
)

from trajectory_engine import TrajectoryEngine
from yolo_detector import CLASS_NAMES, VEHICLE_CLASSES
from virtual_gate import VirtualGate
from audit_engine import AuditEngine
from birth_track_logger import BirthTrackLogger
from birth_track_utils import record_birth_tracks
from track_timeline_debugger import (
    TrackTimelineDebugger,
)

from track_timeline_utils import (
    record_track_timelines,
)

from traffic_volume_engine import TrafficVolumeEngine
from road_capacity_engine import RoadCapacityEngine
from vc_ratio_engine import VCRatioEngine


selected_device = get_selected_device()

def open_video_source(
    source,
    is_rtsp,
):
    """
    Membuka file video atau stream RTSP.

    Fungsi ini hanya membuat dan mengembalikan
    objek cv2.VideoCapture.
    """

    if is_rtsp:
        video = cv2.VideoCapture(
            source,
            cv2.CAP_FFMPEG,
        )

        video.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1,
        )

    else:
        video = cv2.VideoCapture(
            source
        )

    return video    

benchmark_device = (
    "CUDA"
    if selected_device != "cpu"
    else "CPU"
)
show_banner(selected_device)

#video = cv2.VideoCapture(VIDEO_PATH)
source = str(VIDEO_PATH)

is_rtsp = source.lower().startswith(
    ("rtsp://", "rtsps://")
)

print(f"Kamera aktif : {ACTIVE_CAMERA_NAME}")

if is_rtsp:
    print("Sumber video : RTSP Camera")

    video = cv2.VideoCapture(
        source,
        cv2.CAP_FFMPEG
    )

    video.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

else:
    print(f"Sumber video : {source}")

    video = cv2.VideoCapture(source)

if not video.isOpened():
    raise RuntimeError(
        f"Gagal membuka sumber video "
        f"untuk {ACTIVE_CAMERA_NAME}."
    )

frame_ke = 0
#fps = video.get(cv2.CAP_PROP_FPS)
fps = video.get(
    cv2.CAP_PROP_FPS
)

if fps is None or fps <= 0 or fps > 120:
    fps = 25.0

    print(
        "FPS sumber tidak valid. "
        "Menggunakan fallback 25 FPS."
    )

else:
    print(
        f"Source FPS   : {fps:.2f}"
    )

#panel_Vehicle_Count
vehicle_data = create_vehicle_data()


#tracker = VehicleTracker()

tracker = None
speed_estimator = None

trajectory_engine = TrajectoryEngine(
    max_history=30
)

# ==========================================
# DEBUG TRACK
# ==========================================

#inisialisasi

audit_engine = AuditEngine()

birth_logger = BirthTrackLogger()

timeline_debugger = TrackTimelineDebugger()

virtual_gate = None

observed_gate_sides = {}
gate_crossing_states = {}

virtual_gate_count = {
    VirtualGate.A_TO_B: 0,
    VirtualGate.B_TO_A: 0,
}

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

benchmark_start_time = time.perf_counter()

performance_last_time = time.perf_counter()
performance_last_frame = 0

benchmark_completed = False


consecutive_read_failures = 0
MAX_READ_FAILURES = 5
reconnect_count = 0

traffic_volume_engine = TrafficVolumeEngine(
    window_seconds=60
)

road_capacity_engine = RoadCapacityEngine(
    base_capacity=ROAD_BASE_CAPACITY,
    fc_width=ROAD_FC_WIDTH,
    fc_direction=ROAD_FC_DIRECTION,
    fc_side_friction=ROAD_FC_SIDE_FRICTION,
    fc_city_size=ROAD_FC_CITY_SIZE,
)

vc_ratio_engine = VCRatioEngine()

road_capacity = (
    road_capacity_engine.get_capacity()
)

latest_volume_smp_per_hour = 0.0
latest_vc_ratio = 0.0

latest_status, latest_status_color = (
    get_traffic_status(
        latest_vc_ratio
    )
)

def update_trajectories(
    result,
    trajectory_engine,
):
    """
    Merekam bottom-center setiap kendaraan
    berdasarkan tracking ID ByteTrack.
    """

    if result.boxes is None:
        return

    for box in result.boxes:

        if box.id is None:
            continue

        track_id = int(box.id[0])
        class_id = int(box.cls[0])

        class_name = CLASS_NAMES[class_id]

        if class_name not in VEHICLE_CLASSES:
            continue

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0],
        )

        bottom_center = (
            (x1 + x2) // 2,
            y2,
        )

        trajectory_engine.update(
            track_id,
            bottom_center,
        )


def observe_virtual_gate(
    trajectory_engine,
    virtual_gate,
    observed_gate_sides,
    gate_crossing_states,
    frame_number,
    cooldown_frames,
    rearm_distance,
    hysteresis_distance,
):
    """
    Mendeteksi crossing Virtual Gate.

    Satu tracking ID dapat menghasilkan
    lebih dari satu crossing yang valid.

    Pengaman:
    - hysteresis terhadap jitter dekat garis;
    - cooldown antar crossing;
    - re-arm setelah kendaraan cukup jauh
      dari gate.
    """

    events = []

    trajectories = (
        trajectory_engine
        .get_all_trajectories()
    )

    for track_id, points in trajectories.items():

        if not points:
            continue

        current_point = points[-1]

        previous_point = None

        if len(points) >= 2:
            previous_point = points[-2]

        signed_distance = (
            virtual_gate.get_signed_distance(
                current_point
            )
        )

        # ==========================================
        # HYSTERESIS SIDE
        # ==========================================

        if (
            signed_distance
            > hysteresis_distance
        ):
            current_side = (
                VirtualGate.SIDE_A
            )

        elif (
            signed_distance
            < -hysteresis_distance
        ):
            current_side = (
                VirtualGate.SIDE_B
            )

        else:
            current_side = (
                VirtualGate.ON_GATE
            )

        previous_side = (
            observed_gate_sides.get(
                track_id
            )
        )

        state = gate_crossing_states.setdefault(
            track_id,
            {
                "last_crossing_frame": None,
                "last_direction": None,
                "armed": True,
            },
        )

        # ==========================================
        # RE-ARM
        # ==========================================

        if not state["armed"]:

            moved_far_enough = (
                abs(signed_distance)
                >= rearm_distance
            )

            last_direction = state[
                "last_direction"
            ]

            on_expected_side = (
                (
                    last_direction
                    == VirtualGate.B_TO_A
                    and current_side
                    == VirtualGate.SIDE_A
                )
                or
                (
                    last_direction
                    == VirtualGate.A_TO_B
                    and current_side
                    == VirtualGate.SIDE_B
                )
            )

            if (
                moved_far_enough
                and on_expected_side
            ):
                state["armed"] = True

        # ==========================================
        # DETECT DIRECTION
        # ==========================================

        direction = None

        if (
            previous_side
            == VirtualGate.SIDE_A
            and current_side
            == VirtualGate.SIDE_B
        ):
            direction = VirtualGate.B_TO_A

        elif (
            previous_side
            == VirtualGate.SIDE_B
            and current_side
            == VirtualGate.SIDE_A
        ):
            direction = VirtualGate.A_TO_B

        # ON_GATE tidak mengganti
        # last valid side.
        if (
            current_side
            != VirtualGate.ON_GATE
        ):
            observed_gate_sides[
                track_id
            ] = current_side

        if direction is None:
            continue

        # ==========================================
        # SEGMENT BOUNDARY CHECK
        # ==========================================

        if not virtual_gate.intersects_segment(
            previous_point,
            current_point,
        ):
            continue

        if not state["armed"]:
            continue

        last_crossing_frame = state[
            "last_crossing_frame"
        ]

        if (
            last_crossing_frame is not None
            and (
                frame_number
                - last_crossing_frame
            ) < cooldown_frames
        ):
            continue

        # ==========================================
        # ACCEPT CROSSING
        # ==========================================

        if (
            MULTI_CROSSING_DEBUG_ENABLED
            and state["last_crossing_frame"] is not None
        ):
            print(
                "MULTI-CROSSING EVENT | "
                f"ID #{track_id} | "
                f"Previous={state['last_direction']} | "
                f"Current={direction} | "
                f"Previous Frame="
                f"{state['last_crossing_frame']} | "
                f"Current Frame={frame_number}"
            )

        state["last_crossing_frame"] = (
            frame_number
        )

        state["last_direction"] = (
            direction
        )

        state["armed"] = False

        event = {
            "track_id": track_id,
            "direction": direction,
            "point": current_point,
        }

        events.append(event)

        print(
            f"VIRTUAL GATE EVENT | "
            f"ID #{track_id} | "
            f"Arah = {direction} | "
            f"Point = {current_point}"
        )

    return events

def get_active_track_ids(result):
    """
    Mengambil tracking ID yang terlihat
    pada frame saat ini.
    """
    active_track_ids = set()

    if result.boxes is None:
        return active_track_ids

    for box in result.boxes:
        if box.id is None:
            continue

        active_track_ids.add(
            int(box.id[0])
        )

    return active_track_ids

#################

while True:

    ret, frame = video.read()

    if not ret or frame is None:

        consecutive_read_failures += 1

        print(
            "Gagal membaca frame "
            f"({consecutive_read_failures}/"
            f"{MAX_READ_FAILURES})"
        )

        if not is_rtsp:
            benchmark_completed = True
            break

        if consecutive_read_failures >= MAX_READ_FAILURES:

            print()
            print("=" * 60)
            print("RTSP TERPUTUS")
            print("Mencoba reconnect...")
            print("=" * 60)

            video.release()

            time.sleep(3)

            video = open_video_source(
                source,
                is_rtsp
            )

            if video.isOpened():
                reconnect_count += 1

                print(
                    f"Reconnect berhasil."
                    f"Total reconnect: {reconnect_count}"
                )

                consecutive_read_failures = 0

                continue

            print(
                "Reconnect gagal."
            )

            consecutive_read_failures = 0

            time.sleep(5)
            continue

        # Gangguan singkat, belum perlu reconnect
        time.sleep(0.2)
        continue

    # Frame berhasil dibaca
    consecutive_read_failures = 0

    frame_ke += 1

    if tracker is None:

        # Garis akhir speed sekaligus garis utama counting
        line_b_y = get_counting_line_y(frame)

        # Garis awal speed
        line_a_y = get_speed_line_a_y(line_b_y)

        tracker = VehicleTracker(
            line_y=line_b_y
        )

        # Counter lama mulai menghitung ketika kendaraan
        # mencapai batas atas counting zone.
        legacy_trigger_y = (
            tracker.line_y
            - tracker.line_tolerance
        )

        # Virtual Gate disamakan dengan posisi trigger legacy
        # agar perbandingan audit adil.
        virtual_gate = VirtualGate(
            start_point=VIRTUAL_GATE_START_POINT,
            end_point=VIRTUAL_GATE_END_POINT,
            tolerance=0,
        )

        print()
        print("=" * 60)
        print("COUNTING CONFIGURATION")
        print("=" * 60)
        print(
            f"Legacy line Y       : "
            f"{tracker.line_y}"
        )
        print(
            f"Legacy tolerance    : "
            f"{tracker.line_tolerance}"
        )
        print(
            f"Legacy trigger Y    : "
            f"{legacy_trigger_y}"
        )
        print(
            f"Virtual Gate Y      : "
            f"{virtual_gate.start_point[1]}"
        )
        print(
            f"Virtual tolerance   : "
            f"{virtual_gate.tolerance}"
        )
        print("=" * 60)

        speed_estimator = SpeedEstimator(
            line_a_y=line_a_y,
            line_b_y=line_b_y,
            fps=fps,
            distance_meters=10,
        )

    result = track(frame)

    active_track_ids = get_active_track_ids(
        result
        )

    update_trajectories(
        result,
        trajectory_engine,
        )
    
    if BIRTH_DEBUG_ENABLED:
        record_birth_tracks(
            result=result,
            frame_number=frame_ke,
            birth_logger=birth_logger,
            virtual_gate=virtual_gate,
        )

    if TIMELINE_DEBUG_ENABLED:
        record_track_timelines(
            result=result,
            frame_number=frame_ke,
            timeline_debugger=timeline_debugger,
            virtual_gate=virtual_gate,
            debug_track_ids=(
                TIMELINE_DEBUG_TRACK_IDS
            ),
        )

        
    # ==========================================
    # LOG DEBUG TRACK ID
    # ==========================================

    if DEBUG_TRACK_ENABLED:
        for debug_track_id in DEBUG_TRACK_IDS:

            if debug_track_id not in active_track_ids:
                continue

            trajectory = (
                trajectory_engine.get_trajectory(
                debug_track_id
                )
            )

            current_point = (
                trajectory[-1]
                if trajectory
                else None
            )

            print(
                f"DEBUG TRACK AKTIF | "
                f"Frame={frame_ke} | "
                f"ID={debug_track_id} | "
                f"Point={current_point} | "
                f"Trajectory Length="
                f"{len(trajectory)}"
            )

    gate_events = observe_virtual_gate(
        trajectory_engine,
        virtual_gate,
        observed_gate_sides,
        gate_crossing_states,
        frame_ke,
        GATE_CROSSING_COOLDOWN_FRAMES,
        GATE_REARM_DISTANCE,
        GATE_HYSTERESIS_DISTANCE,
    )

    for event in gate_events:

        direction = event["direction"]

        virtual_gate_count[
            direction
        ] += 1

        print(
            "VIRTUAL GATE COUNT | "
            f"A_TO_B="
            f"{virtual_gate_count[VirtualGate.A_TO_B]} | "
            f"B_TO_A="
            f"{virtual_gate_count[VirtualGate.B_TO_A]}"
        )

    
    # VehicleTracker melakukan voting lebih dahulu
    #tracker.update(result)

    
    # VehicleTracker melakukan voting lebih dahulu
    legacy_events = tracker.update(result)

    for event in legacy_events:

        audit_engine.record_legacy(
            track_id=event["track_id"],
            vehicle_type=event["vehicle_type"],
            direction=event["direction"],
            frame_number=frame_ke,
            point=event["point"],
        )

    
    
    for event in gate_events:

        track_id = event["track_id"]

        vehicle_type = tracker.get_vehicle_label(
            track_id
        )

        audit_engine.record_virtual_gate(
            track_id=track_id,
            vehicle_type=vehicle_type,
            direction=event["direction"],
            frame_number=frame_ke,
            point=event["point"],
        )

        if (
            event["direction"]
            == VC_TARGET_DIRECTION
        ):
            traffic_volume_engine.add_vehicle(
                vehicle_type
            )

            print(
                "VC VOLUME INPUT | "
                f"ID #{track_id} | "
                f"Jenis={vehicle_type} | "
                f"Arah={event['direction']} | "
                f"Counts={traffic_volume_engine.counts}"
            )

    if traffic_volume_engine.is_window_complete():
        # 1. Hitung V
        volume_smp_per_hour = (
            traffic_volume_engine
            .get_volume_per_hour()
        )
        # 2. Hitung V/C
        vc_ratio = vc_ratio_engine.calculate(
            volume=volume_smp_per_hour,
            capacity=road_capacity,
        )
        # 3. Simpan sebagai nilai terbaru
        latest_volume_smp_per_hour = (
            volume_smp_per_hour
        )

        latest_vc_ratio = vc_ratio
        # 4. Tentukan status berdasarkan V/C baru
        latest_status, latest_status_color = (
            get_traffic_status(
                latest_vc_ratio
            )
        )

        latest_vc_data = {
            "volume": latest_volume_smp_per_hour,
            "capacity": road_capacity,
            "vc_ratio": latest_vc_ratio,
            "status": latest_status,
        }

        print()
        print("=" * 60)
        print("VC VOLUME REPORT - 1 MINUTE")
        print("=" * 60)

        print(
            f"Counts     : "
            f"{traffic_volume_engine.counts}"
        )

        print(
            f"Total SMP  : "
            f"{traffic_volume_engine.get_total_smp():.2f}"
        )

        print(
            f"Volume (V)    : "
            f"{volume_smp_per_hour:.2f} smp/jam"
        )

        print(
            f"Capacity(C) : "
            f"{road_capacity:.2f} smp/jam"
        )

        print(
            f"V/C Ratio   : "
            f"{vc_ratio:.2f}"
        )

        print(
            f"Status      : "
            f"{latest_status}"
        )

        print("=" * 60)

        csv_logger.save(
            vehicle_data,
            latest_vc_data,
        )

        database_logger.save(
            vehicle_data,
            latest_vc_data,
        )

        traffic_volume_engine.reset()

    # SpeedEstimator mengambil hasil voting tersebut
    speed_estimator.update(
    result,
    frame_ke,
    tracker
    )


    vehicle_data = tracker.get_vehicle_data()

    if (
        PERFORMANCE_AUDIT_ENABLED
        and frame_ke
        % PERFORMANCE_REPORT_INTERVAL_FRAMES
        == 0
    ):
        performance_now = time.perf_counter()

        interval_seconds = (
            performance_now
            - performance_last_time
        )

        interval_frames = (
            frame_ke
            - performance_last_frame
        )

        processing_fps = (
            interval_frames / interval_seconds
            if interval_seconds > 0
            else 0.0
        )

        stored_trajectories = (
            trajectory_engine
            .get_all_trajectories()
        )

        active_track_count = len(
            active_track_ids
        )

        stored_trajectory_count = len(
            stored_trajectories
        )

        total_trajectory_points = sum(
            len(points)
            for points
            in stored_trajectories.values()
        )

        print()
        print("=" * 60)
        print("PERFORMANCE AUDIT")
        print("=" * 60)
        print(
            f"Frame aktif          : "
            f"{frame_ke}"
        )
        print(
            f"Processing FPS       : "
            f"{processing_fps:.2f}"
        )
        print(
            f"Track aktif frame    : "
            f"{active_track_count}"
        )
        print(
            f"Trajectory tersimpan : "
            f"{stored_trajectory_count}"
        )
        if BIRTH_DEBUG_ENABLED:
            print(
                f"Birth track cache    : "
                f"{birth_logger.count()}"
            )
        print(
            f"Total titik history  : "
            f"{total_trajectory_points}"
        )
        print(
            f"Gate side cache      : "
            f"{len(observed_gate_sides)}"
        )
        print(
            f"Gate crossed cache   : "
            f"{len(gate_crossing_states)}"
        )
        print(
            f"Legacy track cache   : "
            f"{len(tracker.track_frames)}"
        )
        print(
            f"Legacy crossed cache : "
            f"{len(tracker.crossed_ids)}"
        )
        print("=" * 60)

        performance_last_time = performance_now
        performance_last_frame = frame_ke

    vehicle_data = update_vehicle_total(
        vehicle_data
    )

    current_time = time.time()

    frame = draw_detection(
        frame,
        result,
        speed_estimator,
        tracker
    )

    frame = draw_trajectories(
    frame,
    trajectory_engine,
    active_track_ids,
    debug_track_ids=(
        DEBUG_TRACK_IDS
        if DEBUG_TRACK_ENABLED
        else set()
        ),
    show_only_debug=(
        SHOW_ONLY_DEBUG_TRACKS
        if DEBUG_TRACK_ENABLED
        else False
        ),
    keep_debug_visible=(
        KEEP_DEBUG_TRAJECTORY_VISIBLE
        ),
    )

    frame = draw_virtual_gate(
    frame,
    virtual_gate,
    )

    frame = draw_virtual_gate_summary(
    frame,
    virtual_gate_count,
    )
    
    frame = draw_speed_line_a(
        frame,
        speed_estimator.line_a_y
    )
    # Legacy line tetap aktif untuk audit,
    # tetapi tidak ditampilkan di dashboard.
    #frame = draw_counting_line(
    #    frame,
    #   tracker.line_y
    #)

    frame_kecil = resize_frame(frame)


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

            
    dashboard = draw_compact_summary(
    dashboard,
    vehicle_data,
    latest_volume_smp_per_hour,
    road_capacity,
    latest_vc_ratio,
    latest_status,
    latest_status_color,
    )
     
    #footer
    dashboard = draw_footer(dashboard)

     
    # Menampilkan dashboard
    cv2.imshow(WINDOW_NAME, dashboard)

    # Keluar jika tombol q ditekan
    if cv2.waitKey(1) & 0xFF == ord("q"):
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

    benchmark_vc_data = {
        "volume": latest_volume_smp_per_hour,
        "capacity": road_capacity,
        "vc_ratio": latest_vc_ratio,
        "status": latest_status,
    }

    database_logger.save_benchmark(
        model_name=os.path.basename(str(MODEL_PATH)),
        video_name=(
            ACTIVE_CAMERA_NAME
            if is_rtsp
            else os.path.basename(str(VIDEO_PATH))
        ),
        device=benchmark_device,
        run_status=benchmark_status,
        processed_frames=frame_ke,
        source_fps=fps,
        processing_seconds=benchmark_processing_seconds,
        average_fps=benchmark_average_fps,
        vehicle_data=vehicle_data,
        vc_data=benchmark_vc_data,
        notes=(
            "Pengujian aplikasi VC Ratio pada server Dishub. "
            f"Total RTSP reconnect: {reconnect_count}"
        )
    )

    print()
    print("=" * 60)
    print("HASIL BENCHMARK")
    print("=" * 60)
    print(f"Model          : {os.path.basename(str(MODEL_PATH))}")
    #print(f"Video          : {os.path.basename(str(VIDEO_PATH))}")
    source_name = (
    ACTIVE_CAMERA_NAME
    if is_rtsp
    else os.path.basename(
        str(VIDEO_PATH)
    )
    )
    print(f"Sumber         : {source_name}")
    print(f"Device         : {benchmark_device}")
    print(f"Status         : {benchmark_status}")
    print(f"Frame diproses : {frame_ke}")
    print(
        f"Waktu proses   : "
        f"{benchmark_processing_seconds:.2f} detik"
    )
    print(f"FPS rata-rata  : {benchmark_average_fps:.2f}")
    print(f"RTSP Reconnect : {reconnect_count}")
    print(f"Motor          : {vehicle_data['motor']}")
    print(f"Mobil          : {vehicle_data['mobil']}")
    print(f"Bus            : {vehicle_data['bus']}")
    print(f"Truk           : {vehicle_data['truk']}")
    print(f"Ambulans       : {vehicle_data['ambulans']}")
    print(f"Total          : {vehicle_data['total']}")
    print(
        f"Volume (V)     : "
        f"{latest_volume_smp_per_hour:.2f} smp/jam"
    )

    print(
        f"Capacity (C)   : "
        f"{road_capacity:.2f} smp/jam"
    )

    print(
        f"VC Ratio       : "
        f"{latest_vc_ratio:.4f}"
    )

    print(
        f"Status Jalan   : "
        f"{latest_status}"
    )
    print("=" * 60)

else:

    print(
        "BENCHMARK TIDAK DISIMPAN: "
        "tidak ada frame yang berhasil diproses."
    )

# ==========================================
# AUDIT DAN INVESTIGASI
# ==========================================

audit_result = audit_engine.compare(
    direction_filter=VC_TARGET_DIRECTION
)

audit_engine.print_report(
    direction_filter=VC_TARGET_DIRECTION
)
if BIRTH_DEBUG_ENABLED:
    birth_logger.print_legacy_only_analysis(
        legacy_only_ids=audit_result[
            "legacy_only_ids"
        ],
        legacy_events=audit_result[
            "legacy_events"
        ],
    )

if TIMELINE_DEBUG_ENABLED:

    for debug_track_id in (
        TIMELINE_DEBUG_TRACK_IDS
    ):
        timeline_debugger.print_timeline(
            track_id=debug_track_id
        )

audit_engine.print_virtual_direction_summary()

video.release()
cv2.destroyAllWindows()
