from __future__ import annotations

import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

import psutil


# Memastikan folder utama proyek bisa di-import ketika file ini
# dijalankan dengan: python .\tools\system_monitor.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.hardware import get_hardware_info  # noqa: E402


class SystemMonitor:
    """
    Memantau penggunaan CPU, RAM, GPU, dan VRAM
    dalam background thread.

    GPU dan VRAM akan bernilai None apabila NVIDIA/NVML
    tidak tersedia.
    """

    def __init__(
        self,
        interval: float = 0.5,
        gpu_index: int = 0,
    ) -> None:
        if interval <= 0:
            raise ValueError("Interval monitoring harus lebih dari 0.")

        if gpu_index < 0:
            raise ValueError("GPU index tidak boleh negatif.")

        self.interval = interval
        self.gpu_index = gpu_index

        self.samples: list[dict[str, Any]] = []

        self.started_at: str | None = None
        self.finished_at: str | None = None

        self._start_perf_counter: float | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

        self._pynvml: Any | None = None
        self._gpu_handle: Any | None = None
        self._nvml_initialized = False
        self._gpu_name: str | None = None
        self._gpu_total_vram_mb: float | None = None
        self._gpu_monitoring_available = False

        self.hardware_info = get_hardware_info()
        self._initialize_gpu_monitoring()

    def _initialize_gpu_monitoring(self) -> None:
        """
        Mengaktifkan NVML untuk monitoring GPU apabila tersedia.
        """
        if not self.hardware_info.nvidia_gpu_available:
            return

        if self.gpu_index >= self.hardware_info.gpu_count:
            print(
                f"Peringatan: GPU index {self.gpu_index} tidak tersedia. "
                "Monitoring GPU dinonaktifkan."
            )
            return

        try:
            import pynvml

            pynvml.nvmlInit()

            self._pynvml = pynvml
            self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(
                self.gpu_index
            )
            self._nvml_initialized = True
            self._gpu_monitoring_available = True

            gpu_name = pynvml.nvmlDeviceGetName(self._gpu_handle)

            if isinstance(gpu_name, bytes):
                gpu_name = gpu_name.decode(
                    "utf-8",
                    errors="replace",
                )

            memory_info = pynvml.nvmlDeviceGetMemoryInfo(
                self._gpu_handle
            )

            self._gpu_name = str(gpu_name)
            self._gpu_total_vram_mb = round(
                memory_info.total / (1024**2),
                2,
            )

        except Exception as error:
            self._gpu_monitoring_available = False
            self._gpu_handle = None

            print(
                "Peringatan: monitoring GPU tidak dapat diaktifkan."
            )
            print(f"Detail: {type(error).__name__}: {error}")

            self._shutdown_nvml()

    def _read_gpu_metrics(
        self,
    ) -> tuple[float | None, float | None]:
        """
        Mengambil GPU utilization dan VRAM yang sedang digunakan.
        """
        if (
            not self._gpu_monitoring_available
            or self._pynvml is None
            or self._gpu_handle is None
        ):
            return None, None

        try:
            utilization = self._pynvml.nvmlDeviceGetUtilizationRates(
                self._gpu_handle
            )
            memory_info = self._pynvml.nvmlDeviceGetMemoryInfo(
                self._gpu_handle
            )

            gpu_percent = float(utilization.gpu)
            vram_used_mb = memory_info.used / (1024**2)

            return (
                round(gpu_percent, 2),
                round(vram_used_mb, 2),
            )

        except Exception:
            return None, None

    def _collect_sample(self) -> dict[str, Any]:
        """
        Mengambil satu sampel penggunaan resource sistem.
        """
        if self._start_perf_counter is None:
            elapsed_seconds = 0.0
        else:
            elapsed_seconds = (
                time.perf_counter() - self._start_perf_counter
            )

        cpu_percent = psutil.cpu_percent(interval=None)
        virtual_memory = psutil.virtual_memory()

        ram_used_mb = virtual_memory.used / (1024**2)
        ram_percent = virtual_memory.percent

        gpu_percent, vram_used_mb = self._read_gpu_metrics()

        return {
            "elapsed_seconds": round(elapsed_seconds, 3),
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="milliseconds"
            ),
            "cpu_percent": round(cpu_percent, 2),
            "ram_percent": round(ram_percent, 2),
            "ram_used_mb": round(ram_used_mb, 2),
            "gpu_percent": gpu_percent,
            "vram_used_mb": vram_used_mb,
        }

    def _monitor_loop(self) -> None:
        """
        Loop monitoring yang berjalan dalam background thread.
        """
        # Pemanggilan awal untuk menyiapkan perhitungan CPU psutil.
        psutil.cpu_percent(interval=None)

        while not self._stop_event.is_set():
            sample = self._collect_sample()

            with self._lock:
                self.samples.append(sample)

            # Event.wait() membuat thread dapat berhenti segera,
            # tanpa harus menunggu time.sleep() selesai.
            self._stop_event.wait(self.interval)

    def start(self) -> None:
        """
        Memulai monitoring.
        """
        if self.is_running:
            raise RuntimeError("System monitor sudah berjalan.")

        with self._lock:
            self.samples.clear()

        self.started_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        self.finished_at = None

        self._start_perf_counter = time.perf_counter()
        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="SystemMonitorThread",
            daemon=True,
        )

        self._thread.start()

    def stop(self) -> None:
        """
        Menghentikan monitoring.
        """
        if not self.is_running:
            return

        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(
                timeout=max(2.0, self.interval * 3)
            )

        self.finished_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

    @property
    def is_running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    @staticmethod
    def _summarize_values(
        samples: list[dict[str, Any]],
        field_name: str,
    ) -> dict[str, float | None]:
        values = [
            float(sample[field_name])
            for sample in samples
            if sample.get(field_name) is not None
        ]

        if not values:
            return {
                "average": None,
                "maximum": None,
                "minimum": None,
            }

        return {
            "average": round(mean(values), 2),
            "maximum": round(max(values), 2),
            "minimum": round(min(values), 2),
        }

    def get_summary(self) -> dict[str, Any]:
        """
        Membuat ringkasan statistik dari seluruh sampel.
        """
        with self._lock:
            copied_samples = list(self.samples)

        duration_seconds = 0.0

        if copied_samples:
            duration_seconds = float(
                copied_samples[-1]["elapsed_seconds"]
            )

        return {
            "sample_count": len(copied_samples),
            "monitor_duration_seconds": round(
                duration_seconds,
                3,
            ),
            "sampling_interval_seconds": self.interval,
            "cpu_percent": self._summarize_values(
                copied_samples,
                "cpu_percent",
            ),
            "ram_percent": self._summarize_values(
                copied_samples,
                "ram_percent",
            ),
            "ram_used_mb": self._summarize_values(
                copied_samples,
                "ram_used_mb",
            ),
            "gpu_percent": self._summarize_values(
                copied_samples,
                "gpu_percent",
            ),
            "vram_used_mb": self._summarize_values(
                copied_samples,
                "vram_used_mb",
            ),
        }

    def to_dict(
        self,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Menggabungkan metadata, informasi hardware,
        summary, dan seluruh sampel.
        """
        with self._lock:
            copied_samples = list(self.samples)

        return {
            "metadata": metadata or {},
            "monitor": {
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "sampling_interval_seconds": self.interval,
                "gpu_index": self.gpu_index,
                "gpu_monitoring_available": (
                    self._gpu_monitoring_available
                ),
            },
            "hardware": self.hardware_info.to_dict(),
            "monitored_gpu": {
                "name": self._gpu_name,
                "total_vram_mb": self._gpu_total_vram_mb,
            },
            "summary": self.get_summary(),
            "samples": copied_samples,
        }

    def save_json(
        self,
        output_path: str | Path,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """
        Menyimpan seluruh hasil monitoring ke JSON.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self.to_dict(metadata=metadata)

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return path.resolve()

    def _shutdown_nvml(self) -> None:
        if (
            self._nvml_initialized
            and self._pynvml is not None
        ):
            try:
                self._pynvml.nvmlShutdown()
            except Exception:
                pass

        self._nvml_initialized = False

    def close(self) -> None:
        """
        Menghentikan monitor dan membersihkan NVML.
        """
        self.stop()
        self._shutdown_nvml()

    def __enter__(self) -> SystemMonitor:
        self.start()
        return self

    def __exit__(
        self,
        exception_type: Any,
        exception_value: Any,
        traceback: Any,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        self._shutdown_nvml()


def print_summary(summary: dict[str, Any]) -> None:
    def display(value: float | None, suffix: str = "") -> str:
        if value is None:
            return "-"

        return f"{value:.2f}{suffix}"

    print()
    print("=" * 65)
    print("SYSTEM MONITOR SUMMARY")
    print("=" * 65)
    print(f"Jumlah sampel : {summary['sample_count']}")
    print(
        "Durasi monitor: "
        f"{summary['monitor_duration_seconds']:.2f} detik"
    )
    print(
        "Interval      : "
        f"{summary['sampling_interval_seconds']:.2f} detik"
    )

    print()
    print("[CPU]")
    print(
        "Rata-rata     : "
        f"{display(summary['cpu_percent']['average'], '%')}"
    )
    print(
        "Maksimum      : "
        f"{display(summary['cpu_percent']['maximum'], '%')}"
    )

    print()
    print("[RAM]")
    print(
        "Rata-rata     : "
        f"{display(summary['ram_used_mb']['average'], ' MB')}"
    )
    print(
        "Maksimum      : "
        f"{display(summary['ram_used_mb']['maximum'], ' MB')}"
    )

    print()
    print("[GPU]")
    print(
        "Rata-rata     : "
        f"{display(summary['gpu_percent']['average'], '%')}"
    )
    print(
        "Maksimum      : "
        f"{display(summary['gpu_percent']['maximum'], '%')}"
    )

    print()
    print("[VRAM]")
    print(
        "Rata-rata     : "
        f"{display(summary['vram_used_mb']['average'], ' MB')}"
    )
    print(
        "Maksimum      : "
        f"{display(summary['vram_used_mb']['maximum'], ' MB')}"
    )
    print("=" * 65)


def main() -> None:
    """
    Pengujian mandiri system monitor selama 10 detik.
    """
    monitor = SystemMonitor(interval=0.5)

    print("=" * 65)
    print("SYSTEM MONITOR TEST")
    print("=" * 65)
    print("Monitoring berjalan selama 10 detik.")
    print("Silakan buka aplikasi lain untuk memberi beban pada CPU.")
    print()

    try:
        monitor.start()

        for remaining_seconds in range(10, 0, -1):
            print(
                f"\rSisa waktu: {remaining_seconds:2} detik",
                end="",
                flush=True,
            )
            time.sleep(1)

        monitor.stop()
        print("\rMonitoring selesai.             ")

        summary = monitor.get_summary()
        print_summary(summary)

        output_path = monitor.save_json(
            "benchmark/raw/system_monitor_test.json",
            metadata={
                "benchmark_id": "SYSTEM-MONITOR-TEST",
                "purpose": "Pengujian system_monitor.py",
            },
        )

        print(f"\nHasil JSON: {output_path}")

    finally:
        monitor.close()


if __name__ == "__main__":
    main()