import threading

from flask import Flask, Response, request


app = Flask(__name__)
@app.after_request
def add_cors_headers(response):
    allowed_origins = {
        "http://127.0.0.1:8000",
        "https://dishubptk-vc-ratio.ellokale.id",
    }

    origin = request.headers.get("Origin")

    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin

    return response

_latest_frame = None
_frame_condition = threading.Condition()
_frame_version = 0
_live_data = {}
_live_data_lock = threading.Lock()


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

def update_live_data(data):
    """
    Menyimpan data monitoring terbaru untuk API web.
    """
    global _live_data

    with _live_data_lock:
        _live_data = data.copy()

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

@app.get("/api/live")
def live_data():
    with _live_data_lock:
        data = _live_data.copy()

    return data


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