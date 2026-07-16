import csv
import os
from datetime import datetime


class CSVLogger:

    def __init__(
        self,
        file_path="output/traffic_log.csv"
    ):

        self.file_path = file_path

        # Buat folder output jika belum ada
        folder = os.path.dirname(file_path)

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        # Buat header jika file belum ada
        if not os.path.exists(file_path):
            self._create_file()


    def _create_file(self):

        with open(
            self.file_path,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "motor",
                "mobil",
                "bus",
                "truk",
                "ambulans",
                "total",
                "capacity",
                "vc_ratio",
                "status"
            ])


    def save(
        self,
        vehicle_data,
        traffic_data
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            self.file_path,
            mode="a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                timestamp,
                vehicle_data["motor"],
                vehicle_data["mobil"],
                vehicle_data["bus"],
                vehicle_data["truk"],
                vehicle_data["ambulans"],
                vehicle_data["total"],
                traffic_data["capacity"],
                f'{traffic_data["vc_ratio"]:.2f}',
                traffic_data["status"]
            ])

        print(
            f"CSV TERSIMPAN: {timestamp}"
        )