import threading

from flask import Flask, Response


app = Flask(__name__)

_latest_frame = None
_frame_condition = threading.Condition()
_frame_version = 0


def update_stream_frame(jpeg_bytes):
    """
    Menyimpan frame JPEG terbaru dan memberi tahu
    client stream bahwa frame baru tersedia.
    """
    global _latest_frame
    global _frame_version

    with _frame_condition:
        _latest_frame = jpeg_bytes
        _frame_version += 1

        _frame_condition.notify_all()


def generate_stream():
    """
    Mengirim frame hanya ketika frame baru tersedia.
    """
    last_version = -1

    while True:

        with _frame_condition:

            _frame_condition.wait_for(
                lambda: (
                    _latest_frame is not None
                    and _frame_version != last_version
                )
            )

            frame = _latest_frame
            last_version = _frame_version

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame
            + b"\r\n"
        )


@app.get("/stream")
def stream():
    return Response(
        generate_stream(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        ),
    )


def run_stream_server(
    host="127.0.0.1",
    port=5001,
):
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True,
        use_reloader=False,
    )