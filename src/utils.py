import torch

from config import (
    MODEL_PATH,
    IMAGE_SIZE,
    CONFIDENCE,
    DEVICE
)

def get_selected_device():
    """
    Menentukan device inferensi berdasarkan konfigurasi:
    cpu, cuda, atau auto.
    """

    configured_device = DEVICE.strip().lower()

    if configured_device == "cpu":
        return "cpu"

    if configured_device == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError(
                "DEVICE='cuda', tetapi CUDA tidak tersedia pada komputer ini."
            )

        return 0

    if configured_device == "auto":
        return 0 if torch.cuda.is_available() else "cpu"

    raise ValueError(
        "Nilai DEVICE tidak valid. Gunakan 'cpu', 'cuda', atau 'auto'."
    )


def show_banner(selected_device):
    """
    Menampilkan informasi konfigurasi aplikasi.
    """

    #selected_device = get_selected_device()

    print("=" * 55)
    print("      VC RATIO MONITORING SYSTEM")
    print("=" * 55)

    print(f"Model       : {MODEL_PATH}")
    print(f"Image Size  : {IMAGE_SIZE}")
    print(f"Confidence  : {CONFIDENCE}")

    if selected_device == "cpu":
        print("Device      : CPU")

    else:
        print("Device      : CUDA")
        print(f"GPU         : {torch.cuda.get_device_name(selected_device)}")
        print(f"CUDA Ver    : {torch.version.cuda}")

    print("=" * 55)

def create_vehicle_data():

    return {
        "motor":0,
        "mobil":0,
        "bus":0,
        "truk":0,
        "ambulans":0
    }

def calculate_total(vehicle_data):

    total = (
        vehicle_data["motor"]
        + vehicle_data["mobil"]
        + vehicle_data["bus"]
        + vehicle_data["truk"]
        + vehicle_data["ambulans"]
    )

    return total


def create_traffic_data():

     return {
        "volume": 0,
        "capacity": 320,
        "vc_ratio": 0
    }


def calculate_vc_ratio(volume, capacity):

    if capacity == 0:
        return 0

    return volume / capacity


def get_traffic_status(vc_ratio):

    if vc_ratio < 0.60:
        return "LANCAR", (0,255,0)

    elif vc_ratio < 0.85:
        return "PADAT", (0,255,255)

    else:
        return "MACET", (0,0,255)
    


def get_center_x(container_width, object_width):
    """
    Menghitung posisi X agar objek berada tepat di tengah.
    """

    return (container_width - object_width) // 2

