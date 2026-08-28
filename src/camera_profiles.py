# ==========================================
# CAMERA PROFILES
# ==========================================
#
# Konfigurasi yang berbeda untuk setiap
# lokasi pemasangan kamera.
#
# Algoritma tetap sama.
# Kalibrasi/geometri mengikuti kamera.
# ==========================================


CAMERA_PROFILES = {

    # ======================================
    # JL. PATTIMURA
    # ======================================

    "pattimura": {

        "name": "Kamera Jl. Pattimura",

        "virtual_gate_start": (
            1550,
            570,
        ),

        "virtual_gate_end": (
            450,
            800,
        ),

        "target_direction": "B_TO_A",

        # Konfigurasi kapasitas jalan
        "road_base_capacity": 1650,
        "road_fc_width": 0.91,
        "road_fc_direction": 1.0,
        "road_fc_side_friction": 0.77,
        "road_fc_city_size": 0.94,
    },


    # ======================================
    # JL. JENDRAL URIP
    # ======================================

    "jendral_urip": {

        "name": "Kamera Jl. Jendral Urip",

        # Belum dikalibrasi.
        # Jangan menggunakan koordinat Pattimura.
        "virtual_gate_start": None,
        "virtual_gate_end": None,

        # Akan ditentukan setelah arah
        # lalu lintas dikonfirmasi.
        "target_direction": None,

        # Belum menggunakan parameter
        # kapasitas Pattimura.
        "road_base_capacity": None,
        "road_fc_width": None,
        "road_fc_direction": None,
        "road_fc_side_friction": None,
        "road_fc_city_size": None,
    },
}

def get_camera_profile(camera_code):

    profile = CAMERA_PROFILES.get(
        camera_code
    )

    if profile is None:
        raise ValueError(
            "Camera profile tidak ditemukan: "
            f"{camera_code}"
        )

    return profile