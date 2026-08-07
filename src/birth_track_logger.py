class BirthTrackLogger:
    """
    Menyimpan informasi kemunculan pertama
    setiap tracking ID.

    Modul ini hanya untuk investigasi.
    Tidak memengaruhi counting.
    """

    def __init__(self):
        self.birth_data = {}

    def record(
        self,
        track_id,
        frame_number,
        point,
        side=None,
        vehicle_type=None,
    ):
        """
        Menyimpan data hanya pada kemunculan pertama ID.
        """

        track_id = int(track_id)

        if track_id in self.birth_data:
            return

        self.birth_data[track_id] = {
            "track_id": track_id,
            "first_seen_frame": frame_number,
            "first_point": point,
            "first_side": side,
            "vehicle_type": vehicle_type,
        }

    def get(
        self,
        track_id,
    ):
        """
        Mengambil data kelahiran satu tracking ID.
        """

        return self.birth_data.get(
            int(track_id)
        )

    def has(
        self,
        track_id,
    ):
        return int(track_id) in self.birth_data

    def count(self):
        return len(self.birth_data)

    def remove(
        self,
        track_id,
    ):
        self.birth_data.pop(
            int(track_id),
            None,
        )

    def clear(self):
        self.birth_data.clear()


    def print_legacy_only_analysis(
        self,
        legacy_only_ids,
        legacy_events,
        title="LEGACY ONLY BIRTH ANALYSIS",
    ):
        """
        Menampilkan hubungan antara:
        - event Legacy Only;
        - data kelahiran tracking ID.

        Method ini hanya untuk investigasi.
        """

        print()
        print("=" * 60)
        print(title)
        print("=" * 60)

        if not legacy_only_ids:
            print("Tidak ada Legacy Only.")
            print("=" * 60)
            return

        summary = {
            "SIDE_A": 0,
            "SIDE_B": 0,
            "ON_GATE": 0,
            "UNKNOWN": 0,
        }

        for track_id in legacy_only_ids:

            legacy_event = legacy_events.get(
                track_id
            )

            birth_data = self.get(
                track_id
            )

            print(
                f"Track ID        : {track_id}"
            )

            if legacy_event is not None:
                print(
                    f"Jenis Legacy    : "
                    f"{legacy_event['vehicle_type']}"
                )

                print(
                    f"Frame dihitung  : "
                    f"{legacy_event['frame_number']}"
                )

                print(
                    f"Titik dihitung  : "
                    f"{legacy_event['point']}"
                )

            else:
                print(
                    "Event Legacy     : tidak ditemukan"
                )

            if birth_data is not None:

                first_side = (
                    birth_data["first_side"]
                    or "UNKNOWN"
                )

                if first_side not in summary:
                    first_side = "UNKNOWN"

                summary[first_side] += 1

                print(
                    f"Jenis awal      : "
                    f"{birth_data['vehicle_type']}"
                )

                print(
                    f"Frame pertama   : "
                    f"{birth_data['first_seen_frame']}"
                )

                print(
                    f"Titik pertama   : "
                    f"{birth_data['first_point']}"
                )

                print(
                    f"Sisi pertama    : "
                    f"{birth_data['first_side']}"
                )

                if (
                    legacy_event is not None
                    and birth_data[
                        "first_seen_frame"
                    ] is not None
                ):
                    frames_until_count = (
                        legacy_event[
                            "frame_number"
                        ]
                        - birth_data[
                            "first_seen_frame"
                        ]
                    )

                    print(
                        f"Jeda ke hitung  : "
                        f"{frames_until_count} frame"
                    )

            else:
                summary["UNKNOWN"] += 1

                print(
                    "Data kelahiran  : tidak ditemukan"
                )

            print("-" * 30)

        print()
        print("-" * 60)
        print("RINGKASAN SISI PERTAMA")
        print("-" * 60)

        print(
            f"SIDE_A          : "
            f"{summary['SIDE_A']}"
        )

        print(
            f"SIDE_B          : "
            f"{summary['SIDE_B']}"
        )

        print(
            f"ON_GATE         : "
            f"{summary['ON_GATE']}"
        )

        print(
            f"UNKNOWN         : "
            f"{summary['UNKNOWN']}"
        )

        print("=" * 60)