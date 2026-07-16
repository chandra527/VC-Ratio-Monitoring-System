import os
import sqlite3
from datetime import datetime


class DatabaseLogger:

    def __init__(
        self,
        database_path="output/traffic_data.db"
    ):

        self.database_path = database_path

        folder = os.path.dirname(database_path)

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        self._create_table()


    def _connect(self):

        return sqlite3.connect(
            self.database_path
        )


    def _create_table(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS traffic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                motor INTEGER NOT NULL,
                mobil INTEGER NOT NULL,
                bus INTEGER NOT NULL,
                truk INTEGER NOT NULL,
                ambulans INTEGER NOT NULL,
                total INTEGER NOT NULL,
                capacity INTEGER NOT NULL,
                vc_ratio REAL NOT NULL,
                status TEXT NOT NULL
            )
            """
        )

        connection.commit()
        connection.close()


    def save(
        self,
        vehicle_data,
        traffic_data
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                vehicle_data["motor"],
                vehicle_data["mobil"],
                vehicle_data["bus"],
                vehicle_data["truk"],
                vehicle_data["ambulans"],
                vehicle_data["total"],
                traffic_data["capacity"],
                traffic_data["vc_ratio"],
                traffic_data["status"]
            )
        )

        connection.commit()
        connection.close()

        print(
            f"DATABASE TERSIMPAN: {timestamp}"
        )