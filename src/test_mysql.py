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

vc_data = {
    "volume": 240.00,
    "capacity": 1086.79,
    "vc_ratio": 0.2208,
    "status": "LANCAR"
}

database_logger.save(
    vehicle_data,
    vc_data
)