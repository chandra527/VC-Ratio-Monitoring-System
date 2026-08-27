class AuditEngine:
    """
    Mencatat dan membandingkan event dari:

    1. Counter lama (legacy)
    2. Virtual Gate

    AuditEngine tidak menambah jumlah kendaraan
    dan tidak memengaruhi dashboard.
    """

    LEGACY = "legacy"
    VIRTUAL_GATE = "virtual_gate"

    def __init__(self):
        # Event disimpan berdasarkan tracking ID.
        self.legacy_events = {}
        self.virtual_gate_events = {}

    def record_event(
        self,
        algorithm,
        track_id,
        vehicle_type=None,
        direction=None,
        frame_number=None,
        point=None,
    ):
        """
        Mencatat satu event kendaraan.

        Satu tracking ID hanya disimpan satu kali
        untuk setiap algoritma.
        """

        event = {
            "algorithm": algorithm,
            "track_id": int(track_id),
            "vehicle_type": vehicle_type,
            "direction": direction,
            "frame_number": frame_number,
            "point": point,
        }

        if algorithm == self.LEGACY:
            self.legacy_events.setdefault(
                int(track_id),
                event,
            )

        elif algorithm == self.VIRTUAL_GATE:
            self.virtual_gate_events.setdefault(
                int(track_id),
                event,
            )

        else:
            raise ValueError(
                f"Algoritma audit tidak dikenal: "
                f"{algorithm}"
            )

    def record_legacy(
        self,
        track_id,
        vehicle_type=None,
        direction=None,
        frame_number=None,
        point=None,
    ):
        """
        Mencatat event dari counter lama.
        """

        self.record_event(
            algorithm=self.LEGACY,
            track_id=track_id,
            vehicle_type=vehicle_type,
            direction=direction,
            frame_number=frame_number,
            point=point,
        )

    def record_virtual_gate(
        self,
        track_id,
        vehicle_type=None,
        direction=None,
        frame_number=None,
        point=None,
    ):
        """
        Mencatat event dari Virtual Gate.
        """

        self.record_event(
            algorithm=self.VIRTUAL_GATE,
            track_id=track_id,
            vehicle_type=vehicle_type,
            direction=direction,
            frame_number=frame_number,
            point=point,
        )

    def compare(
        self,
        direction_filter=None,
    ):
        """
        Membandingkan event counter lama dan Virtual Gate
        pada arah yang sama.

        Default:
            B_TO_A

        Karena counter lama saat ini hanya menghitung
        kendaraan arah B_TO_A.
        """
        if direction_filter is None:
            raise ValueError(
                "direction_filter wajib ditentukan."
            )

        legacy_events_filtered = {
            track_id: event
            for track_id, event
            in self.legacy_events.items()
            if event["direction"] == direction_filter
        }

        virtual_events_filtered = {
            track_id: event
            for track_id, event
            in self.virtual_gate_events.items()
            if event["direction"] == direction_filter
        }

        legacy_ids = set(
            legacy_events_filtered.keys()
        )

        virtual_ids = set(
            virtual_events_filtered.keys()
        )

        matched_ids = (
            legacy_ids & virtual_ids
        )

        legacy_only_ids = (
            legacy_ids - virtual_ids
        )

        virtual_only_ids = (
            virtual_ids - legacy_ids
        )

        return {
            "direction_filter": direction_filter,

            "legacy_count": len(
                legacy_ids
            ),

            "virtual_count": len(
                virtual_ids
            ),

            "matched_count": len(
                matched_ids
            ),

            "matched_ids": sorted(
                matched_ids
            ),

            "legacy_only_ids": sorted(
                legacy_only_ids
            ),

            "virtual_only_ids": sorted(
                virtual_only_ids
            ),

            "legacy_events": (
                legacy_events_filtered
            ),

            "virtual_events": (
                virtual_events_filtered
            ),
        }

    def get_event(
        self,
        algorithm,
        track_id,
    ):
        """
        Mengambil rincian event berdasarkan
        algoritma dan tracking ID.
        """

        track_id = int(track_id)

        if algorithm == self.LEGACY:
            return self.legacy_events.get(
                track_id
            )

        if algorithm == self.VIRTUAL_GATE:
            return (
                self.virtual_gate_events.get(
                    track_id
                )
            )

        return None

    def print_report(
        self,
        direction_filter=None,
    ):
        """
        Menampilkan laporan perbandingan
        untuk arah tertentu.
        """

        if direction_filter is None:
            raise ValueError(
                "direction_filter wajib ditentukan."
            )

        result = self.compare(
            direction_filter=direction_filter
        )

        print()
        print("=" * 60)
        print("AUDIT COUNTER REPORT")
        print("=" * 60)

        print(
            f"Arah dibandingkan : "
            f"{result['direction_filter']}"
        )

        print(
            f"Legacy Count      : "
            f"{result['legacy_count']}"
        )

        print(
            f"Virtual Count     : "
            f"{result['virtual_count']}"
        )

        print(
            f"Matched           : "
            f"{result['matched_count']}"
        )

        self._print_event_section(
            title="LEGACY ONLY",
            track_ids=result[
                "legacy_only_ids"
            ],
            events=result[
                "legacy_events"
            ],
        )

        self._print_event_section(
            title="VIRTUAL ONLY",
            track_ids=result[
                "virtual_only_ids"
            ],
            events=result[
                "virtual_events"
            ],
        )

        print("=" * 60)


    def _print_event_section(
        self,
        title,
        track_ids,
        events,
    ):
        """
        Menampilkan detail event yang hanya ditemukan
        oleh salah satu algoritma.
        """

        print()
        print("-" * 60)
        print(title)
        print("-" * 60)

        if not track_ids:
            print("Tidak ada.")
            return

        for track_id in track_ids:

            event = events.get(track_id)

            if event is None:
                continue

            print(
                f"Track ID       : "
                f"{event['track_id']}"
            )

            print(
                f"Jenis          : "
                f"{event['vehicle_type']}"
            )

            print(
                f"Arah           : "
                f"{event['direction']}"
            )

            print(
                f"Frame          : "
                f"{event['frame_number']}"
            )

            print(
                f"Titik          : "
                f"{event['point']}"
            )

            print("-" * 30)

    def print_virtual_direction_summary(self):
        """
        Menampilkan jumlah Virtual Gate
        untuk setiap arah.
        """

        a_to_b_count = sum(
            1
            for event
            in self.virtual_gate_events.values()
            if event["direction"] == "A_TO_B"
        )

        b_to_a_count = sum(
            1
            for event
            in self.virtual_gate_events.values()
            if event["direction"] == "B_TO_A"
        )

        print()
        print("=" * 60)
        print("VIRTUAL GATE DIRECTION SUMMARY")
        print("=" * 60)

        print(
            f"A_TO_B : {a_to_b_count}"
        )

        print(
            f"B_TO_A : {b_to_a_count}"
        )

        print(
            f"Total  : "
            f"{a_to_b_count + b_to_a_count}"
        )

        print("=" * 60)

    def clear(self):
        """
        Menghapus seluruh data audit.
        """

        self.legacy_events.clear()
        self.virtual_gate_events.clear()