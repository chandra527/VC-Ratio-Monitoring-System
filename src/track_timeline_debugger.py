class TrackTimelineDebugger:
    """
    Menyimpan timeline pergerakan satu atau beberapa Track ID
    terhadap Virtual Gate.

    Modul ini hanya untuk investigasi dan tidak memengaruhi
    counting maupun tracking.
    """

    def __init__(self):
        self.timelines = {}

    def record(
        self,
        track_id,
        frame_number,
        point,
        signed_distance,
        side,
    ):
        track_id = int(track_id)

        if track_id not in self.timelines:
            self.timelines[track_id] = []

        self.timelines[track_id].append(
            {
                "frame_number": frame_number,
                "point": point,
                "signed_distance": signed_distance,
                "side": side,
            }
        )

    def get_timeline(self, track_id):
        return self.timelines.get(
            int(track_id),
            [],
        )

    def clear(self):
        self.timelines.clear()

    def print_timeline(
        self,
        track_id,
        title="TRACK TIMELINE DEBUG",
    ):
        track_id = int(track_id)

        timeline = self.get_timeline(
            track_id
        )

        print()
        print("=" * 60)
        print(title)
        print("=" * 60)
        print(f"Track ID : {track_id}")
        print("-" * 60)

        if not timeline:
            print("Timeline tidak ditemukan.")
            print("=" * 60)
            return

        previous_side = None

        for record in timeline:

            current_side = record["side"]

            side_transition = (
                f"{previous_side} -> {current_side}"
                if previous_side is not None
                else f"START -> {current_side}"
            )

            print(
                f"Frame           : "
                f"{record['frame_number']}"
            )

            print(
                f"Point           : "
                f"{record['point']}"
            )

            print(
                f"Signed distance : "
                f"{record['signed_distance']:.2f}"
            )

            print(
                f"Side            : "
                f"{current_side}"
            )

            print(
                f"Transition      : "
                f"{side_transition}"
            )

            print("-" * 30)

            previous_side = current_side

        print("=" * 60)