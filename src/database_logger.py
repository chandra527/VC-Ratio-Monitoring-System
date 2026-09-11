import os
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

from config import ACTIVE_CAMERA_CODE


load_dotenv()


class DatabaseLogger:

    def __init__(self):

        self.database_config = {
            "host": os.getenv(
                "MYSQL_HOST",
                "localhost"
            ),
            "port": int(
                os.getenv(
                    "MYSQL_PORT",
                    "3306"
                )
            ),
            "database": os.getenv(
                "MYSQL_DATABASE"
            ),
            "user": os.getenv(
                "MYSQL_USER"
            ),
            "password": os.getenv(
                "MYSQL_PASSWORD"
            )
        }

        self._validate_config()
        self._create_table()


    def _validate_config(self):

        required_config = {
            "database": self.database_config[
                "database"
            ],
            "user": self.database_config[
                "user"
            ],
            "password": self.database_config[
                "password"
            ]
        }

        missing_config = [
            key
            for key, value
            in required_config.items()
            if not value
        ]

        if missing_config:

            raise ValueError(
                "Konfigurasi MySQL belum lengkap: "
                + ", ".join(missing_config)
            )


    def _connect(self):

        return mysql.connector.connect(
            **self.database_config
        )


    def _get_camera_id(
        self,
        cursor
    ):

        cursor.execute(
            """
            SELECT id
            FROM cameras
            WHERE code = %s
            AND is_active = 1
            LIMIT 1
            """,
            (
                ACTIVE_CAMERA_CODE,
            )
        )

        camera_row = cursor.fetchone()

        if camera_row is None:

            raise RuntimeError(
                "Kamera aktif tidak ditemukan "
                "di database: "
                f"{ACTIVE_CAMERA_CODE}"
            )

        return camera_row[0]


    def _create_table(self):

        connection = None
        cursor = None

        try:

            connection = self._connect()
            cursor = connection.cursor()

            # ==========================================
            # TRAFFIC LOGS
            # ==========================================

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS traffic_logs (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    motor INT NOT NULL,
                    mobil INT NOT NULL,
                    bus INT NOT NULL,
                    truk INT NOT NULL,
                    ambulans INT NOT NULL,
                    total INT NOT NULL,
                    capacity INT NOT NULL,
                    vc_ratio DECIMAL(10, 4) NOT NULL,
                    status VARCHAR(50) NOT NULL
                )
                """
            )

            # ==========================================
            # BENCHMARK RESULTS
            # ==========================================

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    tested_at DATETIME NOT NULL,
                    model_name VARCHAR(100) NOT NULL,
                    video_name VARCHAR(255) NOT NULL,
                    device VARCHAR(50) NOT NULL,
                    run_status VARCHAR(30) NOT NULL,
                    processed_frames INT NOT NULL,
                    source_fps DECIMAL(10, 2) NOT NULL,
                    processing_seconds DECIMAL(12, 2) NOT NULL,
                    average_fps DECIMAL(10, 2) NOT NULL,
                    motor INT NOT NULL,
                    mobil INT NOT NULL,
                    bus INT NOT NULL,
                    truk INT NOT NULL,
                    ambulans INT NOT NULL,
                    total INT NOT NULL,
                    vc_ratio DECIMAL(10, 4) NOT NULL,
                    traffic_status VARCHAR(50) NOT NULL,
                    notes VARCHAR(500)
                )
                """
            )

            # ==========================================
            # VEHICLE SPEED LOGS
            # ==========================================

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vehicle_logs (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,

                    camera_id BIGINT NOT NULL,

                    track_id BIGINT NOT NULL,

                    vehicle_type VARCHAR(30) NOT NULL,

                    direction VARCHAR(20) NOT NULL,

                    physical_direction VARCHAR(50) NOT NULL,

                    speed_kmh DECIMAL(10, 2) NOT NULL,

                    frame_number BIGINT NOT NULL,

                    detected_at DATETIME NOT NULL,

                    INDEX idx_vehicle_camera_time (
                        camera_id,
                        detected_at
                    ),

                    INDEX idx_vehicle_track (
                        track_id
                    ),

                    INDEX idx_vehicle_direction (
                        direction
                    )
                )
                """
            )

            connection.commit()

            print(
                "MYSQL: tabel traffic_logs, "
                "benchmark_results dan "
                "vehicle_logs siap."
            )

        except Error as error:

            print(
                "MYSQL: gagal membuat tabel: "
                f"{error}"
            )

            raise

        finally:

            if cursor is not None:
                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.close()


    def save(
        self,
        vehicle_data,
        vc_data
    ):

        timestamp = datetime.now()

        connection = None
        cursor = None

        try:

            connection = self._connect()
            cursor = connection.cursor()

            camera_id = self._get_camera_id(
                cursor
            )

            cursor.execute(
                """
                INSERT INTO traffic_logs (
                    camera_id,
                    timestamp,
                    motor,
                    mobil,
                    bus,
                    truk,
                    ambulans,
                    total,
                    volume,
                    capacity,
                    vc_ratio,
                    status
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                (
                    camera_id,
                    timestamp,
                    int(vehicle_data["motor"]),
                    int(vehicle_data["mobil"]),
                    int(vehicle_data["bus"]),
                    int(vehicle_data["truk"]),
                    int(vehicle_data["ambulans"]),
                    int(vehicle_data["total"]),
                    float(vc_data["volume"]),
                    float(vc_data["capacity"]),
                    float(vc_data["vc_ratio"]),
                    str(vc_data["status"])
                )
            )

            connection.commit()

            print(
                "MYSQL TERSIMPAN: "
                f"{timestamp:%Y-%m-%d %H:%M:%S} "
                f"| Kamera={ACTIVE_CAMERA_CODE} "
                f"| camera_id={camera_id}"
            )

        except (
            Error,
            RuntimeError
        ) as error:

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.rollback()

            print(
                "MYSQL: gagal menyimpan data: "
                f"{error}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.close()


    def save_vehicle_speed(
        self,
        track_id,
        vehicle_type,
        direction,
        physical_direction,
        speed_kmh,
        frame_number,
    ):

        detected_at = datetime.now()

        connection = None
        cursor = None

        try:

            connection = self._connect()
            cursor = connection.cursor()

            camera_id = self._get_camera_id(
                cursor
            )

            cursor.execute(
                """
                INSERT INTO vehicle_logs (
                    camera_id,
                    track_id,
                    vehicle_type,
                    direction,
                    physical_direction,
                    speed_kmh,
                    frame_number,
                    detected_at
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                (
                    camera_id,
                    int(track_id),
                    str(vehicle_type),
                    str(direction),
                    str(physical_direction),
                    float(speed_kmh),
                    int(frame_number),
                    detected_at
                )
            )

            connection.commit()

            print(
                "MYSQL SPEED TERSIMPAN | "
                f"Kamera={ACTIVE_CAMERA_CODE} | "
                f"ID #{track_id} | "
                f"Jenis={vehicle_type} | "
                f"Arah={direction} | "
                f"Fisik={physical_direction} | "
                f"Speed={speed_kmh:.2f} km/jam"
            )

        except (
            Error,
            RuntimeError
        ) as error:

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.rollback()

            print(
                "MYSQL: gagal menyimpan "
                "speed kendaraan: "
                f"{error}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.close()


    def save_benchmark(
        self,
        model_name,
        video_name,
        device,
        run_status,
        processed_frames,
        source_fps,
        processing_seconds,
        average_fps,
        vehicle_data,
        vc_data,
        notes,
    ):

        tested_at = datetime.now()

        connection = None
        cursor = None

        try:

            connection = self._connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO benchmark_results (
                    tested_at,
                    model_name,
                    video_name,
                    device,
                    run_status,
                    processed_frames,
                    source_fps,
                    processing_seconds,
                    average_fps,
                    motor,
                    mobil,
                    bus,
                    truk,
                    ambulans,
                    total,
                    vc_ratio,
                    traffic_status,
                    notes
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                )
                """,
                (
                    tested_at,
                    str(model_name),
                    str(video_name),
                    str(device),
                    str(run_status),
                    int(processed_frames),
                    float(source_fps),
                    float(processing_seconds),
                    float(average_fps),
                    int(vehicle_data["motor"]),
                    int(vehicle_data["mobil"]),
                    int(vehicle_data["bus"]),
                    int(vehicle_data["truk"]),
                    int(vehicle_data["ambulans"]),
                    int(vehicle_data["total"]),
                    float(vc_data["vc_ratio"]),
                    str(vc_data["status"]),
                    notes
                )
            )

            connection.commit()

            print(
                "MYSQL BENCHMARK TERSIMPAN: "
                f"{model_name} | "
                f"{average_fps:.2f} FPS"
            )

        except Error as error:

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.rollback()

            print(
                "MYSQL: gagal menyimpan benchmark: "
                f"{error}"
            )

        finally:

            if cursor is not None:
                cursor.close()

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.close()