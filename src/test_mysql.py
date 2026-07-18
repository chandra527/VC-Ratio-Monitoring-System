from database_logger import DatabaseLogger


database_logger = DatabaseLogger()

vehicle_data = {
    "motor": 7,
    "mobil": 4,
    "bus": 1,
    "truk": 2,
    "ambulans": 0,
    "total": 14
}

traffic_data = {
    "capacity": 600,
    "vc_ratio": 0.0233,
    "status": "LANCAR"
}

database_logger.save(
    vehicle_data,
    traffic_data
)