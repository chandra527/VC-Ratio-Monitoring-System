import threading

from flask import Flask, Response


app = Flask(__name__)

_latest_frame = None
_frame_lock = threading.Lock()


def update_stream_frame(jpeg_bytes):
    """
    Menyimpan frame JPEG terbaru untuk ditampilkan
    melalui web stream.
    """
    global _latest_frame

    with _frame_lock:
        _latest_frame = jpeg_bytes


def generate_stream():
    """
    Mengirim frame terbaru sebagai MJPEG stream.
    """
    while True:

        with _frame_lock:
            frame = _latest_frame

        if frame is None:
            continue

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