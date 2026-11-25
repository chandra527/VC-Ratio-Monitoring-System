import cv2
import time
import os
import signal

from layout import *
from draw import *
from processing import *
from utils import *
from utils import show_banner
from yolo_detector import draw_detection
from tracker import track
from vehicle_tracker import VehicleTracker
from line_counter import draw_speed_lines
from csv_logger import CSVLogger
from database_logger import DatabaseLogger
from vehicle_event_logger import VehicleEventLogger
from vehicle_event_sender import VehicleEventSender
from speed_estimator import SpeedEstimator
from config import (
    VIDEO_PATH,
    MODEL_PATH,
    ACTIVE_CAMERA_NAME,
    ACTIVE_CAMERA_CODE,
    TARGET_PROCESSING_FPS,
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
    VC_DIRECTION_MAP,
    VC_DIRECTIONS,
    CAMERA_CALIBRATION_MODE,
    SPEED_LINE_A_START,
    SPEED_LINE_A_END,
    SPEED_LINE_B_START,
    SPEED_LINE_B_END,
    SPEED_DISTANCE_METERS,
    STREAM_PORT,
)
from trajectory_engine import TrajectoryEngine
from yolo_detector import CLASS_NAMES, VEHICLE_CLASSES
from virtual_gate import VirtualGate
from birth_track_logger import BirthTrackLogger
from birth_track_utils import record_birth_tracks
from track_timeline_debugger import TrackTimelineDebugger
from track_timeline_utils import record_track_timelines
from traffic_volume_engine import TrafficVolumeEngine
from road_capacity_engine import RoadCapacityEngine
from vc_ratio_engine import VCRatioEngine
import threading

from stream_server import (
    run_stream_server,
    update_stream_frame,
    update_live_data,
)

selected_device = get_selected_device()

# ============================================================
# HEADLESS MODE
# ============================================================

# True:
# - Detection / tracking / counting / speed / database tetap jalan.
# - API realtime /api/live tetap jalan.
# - Rendering video, JPEG stream, dan OpenCV preview dimatikan.
#
# False:
# - Tampilan dan web video stream berjalan seperti biasa.
HEADLESS_MODE = True
WEB_STREAM_ENABLED = True

# ==========================================
# TARGET FPS PEMROSESAN
# ==========================================

print(
    f"Target Processing FPS : "
    f"{TARGET_PROCESSING_FPS:.2f}"
)

print(
    f"Headless mode     : "
    f"{'ON' if HEADLESS_MODE else 'OFF'}"
)

stop_requested = False


def handle_stop_signal(signum, frame):
    global stop_requested

    print()
    print("=" * 60)
    print("STOP REQUESTED")
    print("Menyelesaikan proses dan menyimpan benchmark...")
    print("=" * 60)

    stop_requested = True


signal.signal(
    signal.SIGINT,
    handle_stop_signal,
)



# ============================================================
# WEB STREAM SERVER
# ============================================================

stream_thread = threading.Thread(
    target=run_stream_server,
    kwargs={
        "host": "127.0.0.1",
        "port": STREAM_PORT,
    },
    daemon=True,
)

stream_thread.start()

print(
    f"Web stream server : "
    f"http://127.0.0.1:{STREAM_PORT}/stream"
)

# Web stream tidak perlu mengikuti seluruh processing FPS.
STREAM_FPS = 10.0
STREAM_FRAME_INTERVAL = 1.0 / STREAM_FPS
last_stream_time = 0.0

print(f"Web stream FPS    : {STREAM_FPS:.0f}")


def open_video_source(source, is_rtsp):
    """Membuka file video atau stream RTSP."""

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
        video = cv2.VideoCapture(source)

    return video


benchmark_device = (
    "CUDA"
    if selected_device != "cpu"
    else "CPU"
)

show_banner(selected_device)

source = str(VIDEO_PATH)
is_rtsp = source.lower().startswith(
    ("rtsp://", "rtsps://")
)

print(f"Kamera aktif : {ACTIVE_CAMERA_NAME}")
print(f"VC DIRECTIONS : {VC_DIRECTIONS}")

if is_rtsp:
    print("Sumber video : RTSP Camera")
else:
    print(f"Sumber video : {source}")

video = open_video_source(
    source,
    is_rtsp,
)

if not video.isOpened():
    raise RuntimeError(
        f"Gagal membuka sumber video "
        f"untuk {ACTIVE_CAMERA_NAME}."
    )

frame_ke = 0
fps = video.get(cv2.CAP_PROP_FPS)

if fps is None or fps <= 0 or fps > 120:
    fps = 25.0
    print(
        "FPS sumber tidak valid. "
        "Menggunakan fallback 25 FPS."
    )
else:
    print(f"Source FPS   : {fps:.2f}")


# ============================================================
# FRAME SAMPLING CONFIG
# ============================================================

if TARGET_PROCESSING_FPS <= 0:
    raise ValueError(
        "TARGET_PROCESSING_FPS harus lebih besar dari 0."
    )

sampling_fps = min(TARGET_PROCESSING_FPS, fps)

# Akumulator untuk memilih frame secara merata.
sampling_accumulator = 0.0

# Menghitung frame yang benar-benar masuk YOLO.
processed_frame_count = 0

print(
    f"Sampling FPS       : {sampling_fps:.2f}"
)


# ============================================================
# DATA / ENGINE
# ============================================================

vehicle_data = create_vehicle_data()

# VehicleTracker sekarang hanya melakukan voting kelas kendaraan.
tracker = VehicleTracker()

speed_estimator = SpeedEstimator(
    line_a_start=SPEED_LINE_A_START,
    line_a_end=SPEED_LINE_A_END,
    line_b_start=SPEED_LINE_B_START,
    line_b_end=SPEED_LINE_B_END,
    fps=fps,
    distance_meters=SPEED_DISTANCE_METERS,
)

trajectory_engine = TrajectoryEngine(
    max_history=30
)

birth_logger = BirthTrackLogger()
timeline_debugger = TrackTimelineDebugger()

virtual_gate = VirtualGate(
    start_point=VIRTUAL_GATE_START_POINT,
    end_point=VIRTUAL_GATE_END_POINT,
    tolerance=0,
)

observed_gate_sides = {}
gate_crossing_states = {}

# ==================================================
# TRACK CACHE LIFECYCLE
# ==================================================

# Frame terakhir setiap Tracking ID terlihat.
track_last_seen = {}

# Toleransi ID tidak aktif sebelum dibersihkan.
TRACK_CACHE_TTL_FRAMES = 750

# Pemeriksaan cleanup setiap 300 frame.
TRACK_CACHE_CLEANUP_INTERVAL = 300

virtual_gate_count = {
    VirtualGate.A_TO_B: 0,
    VirtualGate.B_TO_A: 0,
}

print()
print("=" * 60)
print("COUNTING CONFIGURATION")
print("=" * 60)
print("Counting source     : VIRTUAL GATE")
print(
    f"Virtual Gate start  : "
    f"{virtual_gate.start_point}"
)
print(
    f"Virtual Gate end    : "
    f"{virtual_gate.end_point}"
)
print(
    f"Virtual tolerance   : "
    f"{virtual_gate.tolerance}"
)
print("Legacy counter      : DISABLED")
print("=" * 60)


WINDOW_NAME = "VC Ratio Monitoring"

if not HEADLESS_MODE:
    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_AUTOSIZE,
    )

    cv2.moveWindow(
        WINDOW_NAME,
        10,
        10,
    )

csv_logger = CSVLogger()
database_logger = DatabaseLogger()

# Antrean event kendaraan per kamera.
vehicle_event_logger = VehicleEventLogger(ACTIVE_CAMERA_CODE)
vehicle_event_sender = VehicleEventSender(
    event_logger=vehicle_event_logger,
    database_config=database_logger.database_config,
    interval=1.0,
    retry_interval=5.0,
    batch_size=100,
)
vehicle_event_sender.start()
print('Vehicle event sender: ACTIVE')

# Tracking ID yang sudah dicoba disimpan ke MySQL.
attempted_speed_track_ids = set()

# Tracking ID yang sudah masuk statistik speed realtime.
counted_speed_track_ids = set()

# Akumulasi speed untuk rata-rata realtime.
total_speed_kmh = 0.0
total_speed_count = 0

# Statistik kecepatan khusus interval V/C
window_speed_sum = 0.0
window_speed_count = 0
latest_window_average_speed = None

benchmark_start_time = time.perf_counter()
performance_last_time = time.perf_counter()
performance_last_processed_count = 0
performance_last_frame = 0
benchmark_completed = False

consecutive_read_failures = 0
MAX_READ_FAILURES = 5
reconnect_count = 0

traffic_volume_engine = TrafficVolumeEngine(
    window_seconds=60
)

vc_ratio_engine = VCRatioEngine()

if CAMERA_CALIBRATION_MODE:
    road_capacity_engine = None
    road_capacity = 0.0

    print()
    print("=" * 60)
    print("CAMERA CALIBRATION MODE")
    print("=" * 60)
    print("V/C calculation : DISABLED")
    print("Traffic logging  : DISABLED")
    print("Virtual Gate     : ENABLED")
    print("=" * 60)
else:
    road_capacity_engine = RoadCapacityEngine(
        base_capacity=ROAD_BASE_CAPACITY,
        fc_width=ROAD_FC_WIDTH,
        fc_direction=ROAD_FC_DIRECTION,
        fc_side_friction=ROAD_FC_SIDE_FRICTION,
        fc_city_size=ROAD_FC_CITY_SIZE,
    )

    road_capacity = (
        road_capacity_engine.get_capacity()
    )

latest_volume_smp_per_hour = 0.0
latest_vc_ratio = 0.0

latest_status, latest_status_color = (
    get_traffic_status(latest_vc_ratio)
)


# ============================================================
# HELPER
# ============================================================

def update_trajectories(
    result,
    trajectory_engine,
):
    """
    Merekam bottom-center setiap kendaraan
    berdasarkan Tracking ID ByteTrack.
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
    active_track_ids,
):
    """
    Mendeteksi crossing Virtual Gate.

    Satu Tracking ID dapat menghasilkan lebih dari satu
    crossing yang valid dengan hysteresis, cooldown,
    dan mekanisme re-arm.
    """

    events = []

    for track_id in active_track_ids:
        points = trajectory_engine.get_trajectory(
        track_id
        )

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

        # Hysteresis side.
        if signed_distance > hysteresis_distance:
            current_side = VirtualGate.SIDE_A
        elif signed_distance < -hysteresis_distance:
            current_side = VirtualGate.SIDE_B
        else:
            current_side = VirtualGate.ON_GATE

        previous_side = observed_gate_sides.get(
            track_id
        )

        state = gate_crossing_states.setdefault(
            track_id,
            {
                "last_crossing_frame": None,
                "last_direction": None,
                "armed": True,
            },
        )

        # Re-arm setelah kendaraan cukup jauh dari gate.
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

        # Deteksi arah berdasarkan perpindahan sisi.
        direction = None

        if (
            previous_side == VirtualGate.SIDE_A
            and current_side == VirtualGate.SIDE_B
        ):
            direction = VirtualGate.B_TO_A

        elif (
            previous_side == VirtualGate.SIDE_B
            and current_side == VirtualGate.SIDE_A
        ):
            direction = VirtualGate.A_TO_B

        # ON_GATE tidak mengganti last valid side.
        if current_side != VirtualGate.ON_GATE:
            observed_gate_sides[
                track_id
            ] = current_side

        if direction is None:
            continue

        # Pastikan trajectory benar-benar memotong segmen gate.
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
        state["last_direction"] = direction
        state["armed"] = False

        event = {
            "track_id": track_id,
            "direction": direction,
            "point": current_point,
        }

        events.append(event)

        print(
            "VIRTUAL GATE EVENT | "
            f"ID #{track_id} | "
            f"Arah = {direction} | "
            f"Point = {current_point}"
        )

    return events

def cleanup_inactive_tracks(
    frame_number,
    track_last_seen,
    active_track_ids,
    trajectory_engine,
    tracker,
    speed_estimator,
    observed_gate_sides,
    gate_crossing_states,
    attempted_speed_track_ids,
    counted_speed_track_ids,
    ttl_frames,
):
    """
    Membersihkan cache Tracking ID yang sudah
    tidak aktif melewati batas TTL.
    """

    expired_ids = [
        track_id
        for track_id, last_seen in track_last_seen.items()
        if (
            track_id not in active_track_ids
            and frame_number - last_seen > ttl_frames
        )
    ]

    for track_id in expired_ids:
        trajectory_engine.remove_track(track_id)
        tracker.remove_track(track_id)
        speed_estimator.remove_track(track_id)

        observed_gate_sides.pop(track_id, None)
        gate_crossing_states.pop(track_id, None)
        attempted_speed_track_ids.discard(track_id)
        counted_speed_track_ids.discard(track_id)

        track_last_seen.pop(track_id, None)

    return len(expired_ids)


def get_active_track_ids(result):
    """Mengambil Tracking ID yang terlihat pada frame saat ini."""

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


# ============================================================
# MAIN LOOP
# ============================================================

while True:
    if stop_requested:
        break

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
                is_rtsp,
            )

            if video.isOpened():
                reconnect_count += 1

                # Mulai ulang fase sampling setelah RTSP reconnect.
                sampling_accumulator = 0.0

                print(
                    "Reconnect berhasil. "
                    f"Total reconnect: {reconnect_count}"
                )

                consecutive_read_failures = 0
                continue

            print("Reconnect gagal.")
            consecutive_read_failures = 0
            time.sleep(5)
            continue

        time.sleep(0.2)
        continue

    consecutive_read_failures = 0
    frame_ke += 1

    # ============================================================
    # FRAME SAMPLING - SEBELUM YOLO
    # ============================================================

    # Akumulator mengikuti rasio FPS target terhadap FPS sumber.
    sampling_accumulator += sampling_fps

    if sampling_accumulator < fps:
        continue

    sampling_accumulator -= fps

    # Hanya frame terpilih yang diproses YOLO.
    processed_frame_count += 1

    result = track(frame)

    # Voting kelas selalu diperbarui sebelum event gate/speed diproses.
    tracker.update(result)

    active_track_ids = get_active_track_ids(
        result
    )

    # TRACK CACHE LIFECYCLE
    # Catat frame terakhir setiap Tracking ID aktif.
    for track_id in active_track_ids:
        track_last_seen[track_id] = frame_ke

    # Cleanup cache secara berkala.
    if processed_frame_count % TRACK_CACHE_CLEANUP_INTERVAL == 0:
        removed_count = cleanup_inactive_tracks(
            frame_number=frame_ke,
            track_last_seen=track_last_seen,
            active_track_ids=active_track_ids,
            trajectory_engine=trajectory_engine,
            tracker=tracker,
            speed_estimator=speed_estimator,
            observed_gate_sides=observed_gate_sides,
            gate_crossing_states=gate_crossing_states,
            attempted_speed_track_ids=attempted_speed_track_ids,
            counted_speed_track_ids=counted_speed_track_ids,
            ttl_frames=TRACK_CACHE_TTL_FRAMES,
        )

        if removed_count > 0:
            print(
                f"TRACK CACHE CLEANUP | "
                f"Frame={frame_ke} | "
                f"Removed={removed_count}"
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
                "DEBUG TRACK AKTIF | "
                f"Frame={frame_ke} | "
                f"ID={debug_track_id} | "
                f"Point={current_point} | "
                f"Trajectory Length={len(trajectory)}"
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
        active_track_ids,
    )

    for event in gate_events:
        track_id = event["track_id"]
        direction = event["direction"]

        physical_direction = (
            VC_DIRECTION_MAP.get(
                direction,
                direction,
            )
        )

        vehicle_type = tracker.get_vehicle_label(
            track_id
        )

        virtual_gate_count[direction] += 1

        print(
            "VIRTUAL GATE COUNT | "
            f"A_TO_B="
            f"{virtual_gate_count[VirtualGate.A_TO_B]} | "
            f"B_TO_A="
            f"{virtual_gate_count[VirtualGate.B_TO_A]}"
        )

        print(
            "ARAH KENDARAAN | "
            f"Gate={direction} | "
            f"Fisik={physical_direction}"
        )

        if vehicle_type is None:
            print(
                "VIRTUAL GATE WARNING | "
                f"ID #{track_id} belum memiliki "
                "hasil voting kelas."
            )
            continue

        # Hanya arah yang dikonfigurasi sebagai VC_DIRECTIONS
        # yang masuk rekap kendaraan dan perhitungan V/C.
        if direction in VC_DIRECTIONS:
            if vehicle_type in vehicle_data:
                vehicle_data[vehicle_type] += 1

                try:
                    vehicle_event_logger.record(
                        vehicle_type,
                        direction,
                    )
                except Exception as exc:
                    print(
                        'VEHICLE EVENT ERROR | '
                        f'ID #{track_id} | {exc}'
                    )

            traffic_volume_engine.add_vehicle(
                vehicle_type
            )

            print(
                "VC VOLUME INPUT | "
                f"ID #{track_id} | "
                f"Jenis={vehicle_type} | "
                f"Arah={direction} | "
                f"Fisik={physical_direction} | "
                f"Counts={traffic_volume_engine.counts}"
            )

    # SpeedEstimator memakai hasil voting kelas yang sama.
    speed_estimator.update(
        result,
        frame_ke,
        tracker,
    )

    # ============================================================
    # SIMPAN HASIL SPEED PER KENDARAAN
    # ============================================================

    for track_id in active_track_ids:
        if track_id in attempted_speed_track_ids:
            continue

        speed_result = speed_estimator.get_result(
            track_id
        )

        if speed_result is None:
            continue


        speed_kmh = speed_result.get("speed_kmh")
        direction = speed_result.get("direction")

        if speed_kmh is None or direction is None:
            continue

        vehicle_type = tracker.get_vehicle_label(
            track_id
        )

        if vehicle_type is None:
            continue

        physical_direction = (
            VC_DIRECTION_MAP.get(
                direction,
                direction,
            )
        )

        if track_id not in counted_speed_track_ids:
            total_speed_kmh += speed_kmh
            total_speed_count += 1

            # Kecepatan interval hanya untuk arah V/C.
            if direction in VC_DIRECTIONS:
                window_speed_sum += speed_kmh
                window_speed_count += 1

            counted_speed_track_ids.add(track_id)

        save_success = database_logger.save_vehicle_speed(
            track_id=track_id,
            vehicle_type=vehicle_type,
            direction=direction,
            physical_direction=physical_direction,
            speed_kmh=speed_kmh,
            frame_number=frame_ke,
        )

        # Tandai sudah dicoba agar tidak retry otomatis.
        attempted_speed_track_ids.add(track_id)

        if not save_success:
            print(
                f"MYSQL SPEED GAGAL | Track ID={track_id} | "
                "Tidak dilakukan retry otomatis"
            )

    if (
        not CAMERA_CALIBRATION_MODE
        and traffic_volume_engine.is_window_complete()
        ):

        interval_elapsed_seconds = (
            traffic_volume_engine.get_elapsed_seconds()
        )

        volume_smp_per_hour = (
            traffic_volume_engine
            .get_volume_per_hour(
                elapsed_seconds=interval_elapsed_seconds
            )
        )

        vc_ratio = vc_ratio_engine.calculate(
            volume=volume_smp_per_hour,
            capacity=road_capacity,
        )

        latest_volume_smp_per_hour = (
            volume_smp_per_hour
        )
        latest_vc_ratio = vc_ratio

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

        interval_vehicle_data = {
            "motor": traffic_volume_engine.counts["motor"],
            "mobil": traffic_volume_engine.counts["mobil"],
            "bus": traffic_volume_engine.counts["bus"],
            "truk": traffic_volume_engine.counts["truk"],
            "ambulans": 0,
            "total": sum(
                traffic_volume_engine.counts.values()
            ),
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
            interval_vehicle_data,
            latest_vc_data,
        )

        # Rata-rata kecepatan pada interval V/C yang baru selesai.
        latest_window_average_speed = (
            window_speed_sum / window_speed_count
            if window_speed_count > 0
            else None
        )

        window_speed_sum = 0.0
        window_speed_count = 0

        traffic_volume_engine.reset()

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
            processed_frame_count
            - performance_last_processed_count
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
            f"Class voting cache   : "
            f"{len(tracker.track_frames)}"
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
            f"Gate state cache     : "
            f"{len(gate_crossing_states)}"
        )
        print("=" * 60)

        performance_last_time = performance_now
        performance_last_frame = frame_ke
        performance_last_processed_count = processed_frame_count

    vehicle_data = update_vehicle_total(
        vehicle_data
    )

    live_average_speed = (
        total_speed_kmh / total_speed_count
        if total_speed_count > 0
        else 0.0
    )


    update_live_data({
        "camera": ACTIVE_CAMERA_NAME,
        "motor": vehicle_data["motor"],
        "mobil": vehicle_data["mobil"],
        "truk": vehicle_data["truk"],
        "bus": vehicle_data["bus"],
        "ambulans": vehicle_data["ambulans"],
        "total": vehicle_data["total"],
        "average_speed": live_average_speed,
        "interval_average_speed": latest_window_average_speed,
        "volume": latest_volume_smp_per_hour,
        "capacity": road_capacity,
        "vc_ratio": latest_vc_ratio,
        "status": latest_status,
    })



    # Web streaming tanpa mengaktifkan GUI Python.
    # Tidak menjalankan inferensi YOLO tambahan.
    if WEB_STREAM_ENABLED and HEADLESS_MODE:
        current_stream_time = time.perf_counter()

        if current_stream_time - last_stream_time >= STREAM_FRAME_INTERVAL:
            stream_frame = frame.copy()

            stream_frame = draw_detection(
                stream_frame,
                result,
                speed_estimator,
                tracker,
            )

            stream_frame = draw_virtual_gate(
                stream_frame,
                virtual_gate,
            )

            stream_frame = draw_virtual_gate_summary(
                stream_frame,
                virtual_gate_count,
            )

            stream_frame = draw_speed_lines(
                stream_frame,
                SPEED_LINE_A_START,
                SPEED_LINE_A_END,
                SPEED_LINE_B_START,
                SPEED_LINE_B_END,
            )

            # Optimasi ukuran frame khusus streaming web.
            stream_height, stream_width = stream_frame.shape[:2]
            if stream_width > 960:
                stream_frame = cv2.resize(
                    stream_frame,
                    (960, round(stream_height * 960 / stream_width)),
                    interpolation=cv2.INTER_AREA,
                )

            encode_ok, jpeg_buffer = cv2.imencode(
                ".jpg",
                stream_frame,
                [cv2.IMWRITE_JPEG_QUALITY, 65],
            )

            if encode_ok:
                update_stream_frame(jpeg_buffer.tobytes())

            last_stream_time = current_stream_time

    if not HEADLESS_MODE:
        frame = draw_detection(
                frame,
                result,
                speed_estimator,
                tracker,
            )

        # TRAJECTORY DRAWING DISABLED (performance test)

        frame = draw_virtual_gate(
            frame,
            virtual_gate,
        )

        frame = draw_virtual_gate_summary(
            frame,
            virtual_gate_count,
        )

        frame = draw_speed_lines(
            frame,
            SPEED_LINE_A_START,
            SPEED_LINE_A_END,
            SPEED_LINE_B_START,
            SPEED_LINE_B_END,
        )

        frame_kecil = resize_frame(frame)
        tinggi, lebar = frame.shape[:2]

        dashboard = create_dashboard()
        dashboard = draw_video(
            dashboard,
            frame_kecil,
        )
        dashboard = draw_video_frame(dashboard)
        dashboard = draw_lines(dashboard)
        dashboard = draw_header(dashboard)

        dashboard = draw_system_information(
            dashboard,
            frame_ke,
            fps,
            lebar,
            tinggi,
        )

        dashboard = draw_compact_summary(
            dashboard,
            vehicle_data,
            latest_volume_smp_per_hour,
            road_capacity,
            latest_vc_ratio,
            latest_status,
            latest_status_color,
        )

        dashboard = draw_footer(dashboard)

        # Kirim dashboard final ke web stream dengan FPS terbatas.
        current_stream_time = time.perf_counter()

        if (
            current_stream_time - last_stream_time
            >= STREAM_FRAME_INTERVAL
        ):
            encode_ok, jpeg_buffer = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 75],
            )

            if encode_ok:
                update_stream_frame(
                    jpeg_buffer.tobytes()
                )

            last_stream_time = current_stream_time

        cv2.imshow(
            WINDOW_NAME,
            dashboard,
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break




# ============================================================
# BENCHMARK / SHUTDOWN
# ============================================================

benchmark_processing_seconds = (
    time.perf_counter()
    - benchmark_start_time
)

benchmark_average_fps = (
    processed_frame_count / benchmark_processing_seconds
    if benchmark_processing_seconds > 0
    else 0.0
)

benchmark_status = (
    "COMPLETED"
    if benchmark_completed
    else "STOPPED_BY_USER"
)

if frame_ke > 0:
    benchmark_vc_data = {
        "volume": latest_volume_smp_per_hour,
        "capacity": road_capacity,
        "vc_ratio": latest_vc_ratio,
        "status": latest_status,
    }

    database_logger.save_benchmark(
        model_name=os.path.basename(
            str(MODEL_PATH)
        ),
        video_name=(
            ACTIVE_CAMERA_NAME
            if is_rtsp
            else os.path.basename(
                str(VIDEO_PATH)
            )
        ),
        device=benchmark_device,
        run_status=benchmark_status,
        processed_frames=processed_frame_count,
        source_fps=fps,
        processing_seconds=benchmark_processing_seconds,
        average_fps=benchmark_average_fps,
        vehicle_data=vehicle_data,
        vc_data=benchmark_vc_data,
        notes=(
            "Pengujian aplikasi VC Ratio pada server Dishub. "
            f"Total RTSP reconnect: {reconnect_count}"
        ),
    )

    source_name = (
        ACTIVE_CAMERA_NAME
        if is_rtsp
        else os.path.basename(
            str(VIDEO_PATH)
        )
    )

    print()
    print("=" * 60)
    print("HASIL BENCHMARK")
    print("=" * 60)
    print(
        f"Model          : "
        f"{os.path.basename(str(MODEL_PATH))}"
    )
    print(f"Sumber         : {source_name}")
    print(f"Device         : {benchmark_device}")
    print(f"Status         : {benchmark_status}")
    print(f"Frame dibaca   : {frame_ke}")
    print(f"Frame diproses : {processed_frame_count}")
    print(
        f"Waktu proses   : "
        f"{benchmark_processing_seconds:.2f} detik"
    )
    print(
        f"FPS rata-rata  : "
        f"{benchmark_average_fps:.2f}"
    )
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


if TIMELINE_DEBUG_ENABLED:
    for debug_track_id in (
        TIMELINE_DEBUG_TRACK_IDS
    ):
        timeline_debugger.print_timeline(
            track_id=debug_track_id
        )

print()
print("=" * 60)
print("VIRTUAL GATE DIRECTION SUMMARY")
print("=" * 60)
print(
    f"A_TO_B : "
    f"{virtual_gate_count[VirtualGate.A_TO_B]}"
)
print(
    f"B_TO_A : "
    f"{virtual_gate_count[VirtualGate.B_TO_A]}"
)
print(
    f"Total  : "
    f"{sum(virtual_gate_count.values())}"
)
print("=" * 60)

# Hentikan sender pada shutdown normal.
sender_stopped = vehicle_event_sender.stop(timeout=10)
if not sender_stopped:
    print('WARNING: Vehicle event sender belum berhenti.')

video.release()
cv2.destroyAllWindows()
