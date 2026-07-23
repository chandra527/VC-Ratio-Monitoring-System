from pathlib import Path
import argparse
import time

import cv2


DEFAULT_INPUT = Path("data/pak_kasih.dav")
DEFAULT_OUTPUT = Path("data/benchmark_10menit.mp4")


def format_timestamp(total_seconds: float) -> str:
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Memotong video DAV dengan melewati frame secara manual "
            "dan menyimpan hasil sebagai MP4."
        )
    )

    parser.add_argument(
        "--start-minute",
        type=float,
        default=0,
        help="Waktu awal dalam menit. Contoh: 20 atau 12.5",
    )

    parser.add_argument(
        "--duration-minute",
        type=float,
        default=10,
        help="Durasi hasil potongan dalam menit. Default: 10",
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Lokasi video sumber",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Lokasi video hasil",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if not args.input.exists():
        print(f"Video sumber tidak ditemukan: {args.input}")
        return

    if args.start_minute < 0:
        print("--start-minute tidak boleh negatif.")
        return

    if args.duration_minute <= 0:
        print("--duration-minute harus lebih dari 0.")
        return

    video = cv2.VideoCapture(str(args.input))

    if not video.isOpened():
        print(f"Video gagal dibuka: {args.input}")
        return

    fps = video.get(cv2.CAP_PROP_FPS)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0 or width <= 0 or height <= 0:
        print("Metadata FPS atau resolusi video tidak valid.")
        video.release()
        return

    start_seconds = args.start_minute * 60
    duration_seconds = args.duration_minute * 60

    start_frame = int(start_seconds * fps)
    output_frame_count = int(duration_seconds * fps)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        str(args.output),
        fourcc,
        fps,
        (width, height),
    )

    if not writer.isOpened():
        print(f"Gagal membuat video output: {args.output}")
        video.release()
        return

    print("=" * 60)
    print("CROP VIDEO")
    print("=" * 60)
    print(f"Input          : {args.input}")
    print(f"Output         : {args.output}")
    print(f"Resolusi       : {width} x {height}")
    print(f"FPS            : {fps:.2f}")
    print(f"Mulai          : {format_timestamp(start_seconds)}")
    print(f"Durasi         : {format_timestamp(duration_seconds)}")
    print(f"Frame dilewati : {start_frame:,}")
    print(f"Frame disimpan : {output_frame_count:,}")
    print("=" * 60)

    started_at = time.perf_counter()

    skipped_frames = 0
    last_skip_report = 0

    print("\nMelewati frame menuju waktu mulai...")

    while skipped_frames < start_frame:
        success, _frame = video.read()

        if not success:
            print(
                "\nVideo selesai sebelum mencapai waktu mulai "
                "yang diminta."
            )
            writer.release()
            video.release()

            if args.output.exists():
                args.output.unlink()

            return

        skipped_frames += 1

        if skipped_frames - last_skip_report >= 5000:
            progress = (skipped_frames / start_frame) * 100
            print(
                f"Skip: {skipped_frames:,}/{start_frame:,} "
                f"({progress:.1f}%)"
            )
            last_skip_report = skipped_frames

    print("\nMulai menyimpan video hasil...")

    saved_frames = 0
    last_save_report = 0

    while saved_frames < output_frame_count:
        success, frame = video.read()

        if not success:
            print(
                "\nVideo sumber selesai sebelum durasi potongan terpenuhi."
            )
            break

        writer.write(frame)
        saved_frames += 1

        if saved_frames - last_save_report >= 2500:
            progress = (saved_frames / output_frame_count) * 100
            print(
                f"Simpan: {saved_frames:,}/{output_frame_count:,} "
                f"({progress:.1f}%)"
            )
            last_save_report = saved_frames

    writer.release()
    video.release()

    elapsed_seconds = time.perf_counter() - started_at
    actual_duration = saved_frames / fps if fps > 0 else 0

    print()
    print("=" * 60)
    print("CROP SELESAI")
    print("=" * 60)
    print(f"Output          : {args.output.resolve()}")
    print(f"Frame tersimpan : {saved_frames:,}")
    print(f"Durasi hasil    : {format_timestamp(actual_duration)}")
    print(f"Waktu proses    : {elapsed_seconds:.2f} detik")

    if args.output.exists():
        output_size_mb = args.output.stat().st_size / (1024 * 1024)
        print(f"Ukuran hasil    : {output_size_mb:.2f} MB")

    print("=" * 60)


if __name__ == "__main__":
    main()