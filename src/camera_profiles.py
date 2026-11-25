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
        "road_width_m": 10.0,
     
        #"virtual_gate_start": (804, 923),

        "virtual_gate_start": (1743, 679),

        "virtual_gate_end": (804, 923),

        # Konfigurasi speed line
        "speed_line_a_start": (975, 1222),

        "speed_line_a_end": (2156, 819),

        "speed_line_b_start": (680, 722),

        "speed_line_b_end": (1391, 571),

        "speed_distance_meters": 8,

        
        "direction_map": {
        "A_TO_B": "MENJAUHI_KAMERA",
        "B_TO_A": "MENDEKATI_KAMERA",
        },

        "vc_directions": (
            "B_TO_A",
        ),

        "target_direction": "B_TO_A",

        # Target FPS pemrosesan YOLO (eksperimen)
        "target_processing_fps": 10.0,

        # Konfigurasi kapasitas jalan
        "road_base_capacity": 3400,
        "road_fc_width": 1.08,
        "road_fc_direction": 1.0,
        "road_fc_side_friction": 0.77,
        "road_fc_city_size": 0.94,
    },


    # ======================================
    # JL. JENDRAL URIP
    # ======================================

    "jendral_urip": {

        "name": "Kamera Jl. Jendral Urip",
        "road_width_m": 9.5,

        "virtual_gate_start": (1833, 702),

        "virtual_gate_end": (729, 467),

        # Line A = sisi dekat kamera
        "speed_line_a_start": (1583, 1022),

        "speed_line_a_end": (243, 627),

        # Line B = sisi jauh dari kamera
        "speed_line_b_start": (1999, 475),

        "speed_line_b_end": (1125, 343),

        "speed_distance_meters": 10,

        "direction_map": {
        "A_TO_B": "MENJAUHI_KAMERA",
        "B_TO_A": "MENDEKATI_KAMERA",
        },

        "vc_directions": (
            "A_TO_B",
            "B_TO_A",
        ),

        # Belum dikunci.
        # Akan ditentukan dari hasil runtime arah crossing.
        "target_direction": None,

        # Target FPS pemrosesan YOLO (eksperimen)
        "target_processing_fps": 10.0,

        # sudah ada penyesuaian dengan PKJI 2023.
        "road_base_capacity": 2800,
        "road_fc_width": 1.27,
        "road_fc_direction": 1.0,
        "road_fc_side_friction": 0.77,
        "road_fc_city_size": 0.94,
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