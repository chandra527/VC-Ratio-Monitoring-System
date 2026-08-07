import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================================
# PROJECT PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# ==========================================
# YOLO CONFIGURATION
# ==========================================

model_value = os.getenv(
    "MODEL_PATH",
    "models/yolo11s.pt"
)

model_candidate = Path(model_value)

MODEL_PATH = str(
    model_candidate
    if model_candidate.is_absolute()
    else BASE_DIR / model_candidate
)

DEVICE = os.getenv(
    "DEVICE",
    "auto"
)

IMAGE_SIZE = int(
    os.getenv(
        "IMAGE_SIZE",
        "960"
    )
)

CONFIDENCE = float(
    os.getenv(
        "CONFIDENCE",
        "0.15"
    )
)


# ==========================================
# VIDEO SOURCE
# ==========================================

VIDEO_SOURCE_TYPE = os.getenv(
    "VIDEO_SOURCE_TYPE",
    "file"
).lower()

ACTIVE_CAMERA = os.getenv(
    "ACTIVE_CAMERA",
    "1"
)

RTSP_CAMERAS = {
    "1": os.getenv("RTSP_CAMERA_1"),
    "2": os.getenv("RTSP_CAMERA_2"),
}

if VIDEO_SOURCE_TYPE == "rtsp":

    VIDEO_PATH = RTSP_CAMERAS.get(
        ACTIVE_CAMERA
    )

    if not VIDEO_PATH:
        raise ValueError(
            f"RTSP untuk kamera {ACTIVE_CAMERA} "
            "belum dikonfigurasi di file .env."
        )

else:

    video_value = os.getenv(
        "VIDEO_SOURCE",
        "data/benchmark_10menit_25_35.mp4"
    )

    video_candidate = Path(video_value)

    VIDEO_PATH = str(
        video_candidate
        if video_candidate.is_absolute()
        else BASE_DIR / video_candidate
    )

# ==========================================
# DISPLAY
# ==========================================

WINDOW_NAME = os.getenv(
    "WINDOW_NAME",
    "VC Ratio Monitoring"
)

CAMERA_NAMES = {
    "1": "Kamera Komyos sudarso tengah",
    "2": "Kamera Komyos ujung",
}

ACTIVE_CAMERA_NAME = CAMERA_NAMES.get(
    ACTIVE_CAMERA,
    f"Kamera {ACTIVE_CAMERA}"
)

# ==========================================
# TRACK DEBUG MODE
# ==========================================

DEBUG_TRACK_ENABLED = False

DEBUG_TRACK_IDS = {
    1851,
}

# True:
# hanya trajectory ID debug yang digambar.
#
# False:
# semua trajectory digambar,
# ID debug tetap diberi warna merah.
SHOW_ONLY_DEBUG_TRACKS = True

# Mempertahankan trajectory merah setelah
# tracking ID sudah tidak aktif.
KEEP_DEBUG_TRAJECTORY_VISIBLE = True

TIMELINE_DEBUG_ENABLED = True

TIMELINE_DEBUG_TRACK_IDS = {
    4619,
}

# ==========================================
# PERFORMANCE AUDIT
# ==========================================

PERFORMANCE_AUDIT_ENABLED = True
PERFORMANCE_REPORT_INTERVAL_FRAMES = 300

