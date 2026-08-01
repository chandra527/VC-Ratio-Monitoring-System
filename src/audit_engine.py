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

    def compare(self):
        """
        Membandingkan tracking ID kedua algoritma.

        Return:
            matched:
                Terhitung oleh kedua algoritma.

            legacy_only:
                Terhitung counter lama,
                tetapi tidak oleh Virtual Gate.

            virtual_only:
                Terhitung Virtual Gate,
                tetapi tidak oleh counter lama.
        """

        legacy_ids = set(
            self.legacy_events.keys()
        )

        virtual_ids = set(
            self.virtual_gate_events.keys()
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
            "legacy_count": len(legacy_ids),
            "virtual_count": len(virtual_ids),
            "matched_count": len(matched_ids),

            "matched_ids": sorted(
                matched_ids
            ),

            "legacy_only_ids": sorted(
                legacy_only_ids
            ),

            "virtual_only_ids": sorted(
                virtual_only_ids
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

    def print_report(self):
        """
        Menampilkan laporan perbandingan
        ke terminal.
        """

        result = self.compare()

        print()
        print("=" * 60)
        print("AUDIT COUNTER REPORT")
        print("=" * 60)

        print(
            f"Legacy Count     : "
            f"{result['legacy_count']}"
        )

        print(
            f"Virtual Count    : "
            f"{result['virtual_count']}"
        )

        print(
            f"Matched          : "
            f"{result['matched_count']}"
        )

        print(
            f"Legacy Only      : "
            f"{result['legacy_only_ids']}"
        )

        print(
            f"Virtual Only     : "
            f"{result['virtual_only_ids']}"
        )

        print("=" * 60)

    def clear(self):
        """
        Menghapus seluruh data audit.
        """

        self.legacy_events.clear()
        self.virtual_gate_events.clear()