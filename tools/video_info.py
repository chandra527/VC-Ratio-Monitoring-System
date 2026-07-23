from pathlib import Path
import cv2


VIDEO_PATH = Path("data/pak_kasih.dav")


def format_duration(duration_seconds: float) -> str:
    """Mengubah durasi detik menjadi format HH:MM:SS."""

    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def count_frames_manually(video_path: Path) -> int:
    """
    Menghitung jumlah frame secara langsung.

    Digunakan sebagai fallback ketika metadata frame count
    pada video tidak valid.
    """

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise RuntimeError(f"Video gagal dibuka: {video_path}")

    total_frames = 0
    last_report = 0

    print()
    print("Metadata total frame tidak valid.")
    print("Menghitung frame secara manual...")
    print()

    while True:
        success, _frame = video.read()

        if not success:
            break

        total_frames += 1

        if total_frames - last_report >= 5000:
            print(f"Frame terbaca: {total_frames:,}")
            last_report = total_frames

    video.release()

    return total_frames


def main() -> None:
    if not VIDEO_PATH.exists():
        print(f"File tidak ditemukan: {VIDEO_PATH}")
        return

    video = cv2.VideoCapture(str(VIDEO_PATH))

    if not video.isOpened():
        print(f"Video gagal dibuka: {VIDEO_PATH}")
        return

    fps = video.get(cv2.CAP_PROP_FPS)
    metadata_frame_count = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video.release()

    metadata_is_valid = (
        fps > 0
        and metadata_frame_count > 0
        and metadata_frame_count < 1_000_000_000
    )

    if metadata_is_valid:
        total_frames = metadata_frame_count
        counting_method = "Metadata video"

    else:
        total_frames = count_frames_manually(VIDEO_PATH)
        counting_method = "Perhitungan frame manual"

    if fps > 0 and total_frames > 0:
        duration_seconds = total_frames / fps
        formatted_duration = format_duration(duration_seconds)
    else:
        duration_seconds = 0
        formatted_duration = "Tidak diketahui"

    file_size_mb = VIDEO_PATH.stat().st_size / (1024 * 1024)

    print()
    print("=" * 55)
    print("INFORMASI VIDEO")
    print("=" * 55)
    print(f"Nama file       : {VIDEO_PATH.name}")
    print(f"Lokasi          : {VIDEO_PATH.resolve()}")
    print(f"Ukuran file     : {file_size_mb:.2f} MB")
    print(f"Resolusi        : {width} x {height}")
    print(f"FPS             : {fps:.2f}")
    print(f"Total frame     : {total_frames:,}")
    print(f"Durasi detik    : {duration_seconds:.2f}")
    print(f"Durasi          : {formatted_duration}")
    print(f"Metode hitung   : {counting_method}")
    print("=" * 55)


if __name__ == "__main__":
    main()