import os
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


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
            "database": self.database_config["database"],
            "user": self.database_config["user"],
            "password": self.database_config["password"]
        }

        missing_config = [
            key
            for key, value in required_config.items()
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


    def _create_table(self):

        connection = None
        cursor = None

        try:

            connection = self._connect()
            cursor = connection.cursor()

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

            connection.commit()

            print(
                "MYSQL: tabel traffic_logs siap."
            )

        except Error as error:

            print(
                f"MYSQL: gagal membuat tabel: "
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
        traffic_data
    ):

        timestamp = datetime.now()

        connection = None
        cursor = None

        try:

            connection = self._connect()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO traffic_logs (
                    timestamp,
                    motor,
                    mobil,
                    bus,
                    truk,
                    ambulans,
                    total,
                    capacity,
                    vc_ratio,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                """,
                (
                    timestamp,
                    int(vehicle_data["motor"]),
                    int(vehicle_data["mobil"]),
                    int(vehicle_data["bus"]),
                    int(vehicle_data["truk"]),
                    int(vehicle_data["ambulans"]),
                    int(vehicle_data["total"]),
                    int(traffic_data["capacity"]),
                    float(traffic_data["vc_ratio"]),
                    str(traffic_data["status"])
                )
            )

            connection.commit()

            print(
                "MYSQL TERSIMPAN: "
                f"{timestamp:%Y-%m-%d %H:%M:%S}"
            )

        except Error as error:

            if (
                connection is not None
                and connection.is_connected()
            ):
                connection.rollback()

            print(
                f"MYSQL: gagal menyimpan data: "
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