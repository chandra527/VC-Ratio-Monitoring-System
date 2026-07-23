from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class GPUInfo:
    index: int
    name: str
    total_vram_mb: float
    driver_version: str | None = None


@dataclass
class HardwareInfo:
    nvml_available: bool
    nvidia_gpu_available: bool
    gpu_count: int
    gpus: list[GPUInfo]

    torch_installed: bool
    torch_version: str | None
    torch_cuda_available: bool
    torch_cuda_version: str | None
    torch_device_count: int
    torch_device_name: str | None

    nvml_error: str | None = None
    torch_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _decode_nvml_text(value: str | bytes) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    return value


def detect_nvidia_gpu() -> tuple[
    bool,
    bool,
    int,
    list[GPUInfo],
    str | None,
]:
    """
    Mendeteksi GPU NVIDIA melalui NVML.

    Return:
        nvml_available
        nvidia_gpu_available
        gpu_count
        gpu_list
        error_message
    """
    try:
        import pynvml
    except ImportError:
        return (
            False,
            False,
            0,
            [],
            "Library nvidia-ml-py belum terinstal.",
        )

    nvml_initialized = False

    try:
        pynvml.nvmlInit()
        nvml_initialized = True

        gpu_count = pynvml.nvmlDeviceGetCount()
        driver_version = _decode_nvml_text(
            pynvml.nvmlSystemGetDriverVersion()
        )

        gpus: list[GPUInfo] = []

        for index in range(gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)

            gpu_name = _decode_nvml_text(
                pynvml.nvmlDeviceGetName(handle)
            )

            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            total_vram_mb = memory_info.total / (1024**2)

            gpus.append(
                GPUInfo(
                    index=index,
                    name=gpu_name,
                    total_vram_mb=round(total_vram_mb, 2),
                    driver_version=driver_version,
                )
            )

        return (
            True,
            gpu_count > 0,
            gpu_count,
            gpus,
            None,
        )

    except Exception as error:
        return (
            False,
            False,
            0,
            [],
            f"{type(error).__name__}: {error}",
        )

    finally:
        if nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass


def detect_torch_cuda() -> tuple[
    bool,
    str | None,
    bool,
    str | None,
    int,
    str | None,
    str | None,
]:
    """
    Memeriksa instalasi PyTorch dan dukungan CUDA-nya.

    Return:
        torch_installed
        torch_version
        torch_cuda_available
        torch_cuda_version
        torch_device_count
        torch_device_name
        error_message
    """
    try:
        import torch
    except ImportError:
        return (
            False,
            None,
            False,
            None,
            0,
            None,
            "PyTorch belum terinstal.",
        )

    try:
        torch_version = torch.__version__
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda
        device_count = torch.cuda.device_count() if cuda_available else 0

        device_name = None

        if cuda_available and device_count > 0:
            device_name = torch.cuda.get_device_name(0)

        return (
            True,
            torch_version,
            cuda_available,
            cuda_version,
            device_count,
            device_name,
            None,
        )

    except Exception as error:
        return (
            True,
            getattr(torch, "__version__", None),
            False,
            getattr(torch.version, "cuda", None),
            0,
            None,
            f"{type(error).__name__}: {error}",
        )


def get_hardware_info() -> HardwareInfo:
    (
        nvml_available,
        nvidia_gpu_available,
        gpu_count,
        gpus,
        nvml_error,
    ) = detect_nvidia_gpu()

    (
        torch_installed,
        torch_version,
        torch_cuda_available,
        torch_cuda_version,
        torch_device_count,
        torch_device_name,
        torch_error,
    ) = detect_torch_cuda()

    return HardwareInfo(
        nvml_available=nvml_available,
        nvidia_gpu_available=nvidia_gpu_available,
        gpu_count=gpu_count,
        gpus=gpus,
        torch_installed=torch_installed,
        torch_version=torch_version,
        torch_cuda_available=torch_cuda_available,
        torch_cuda_version=torch_cuda_version,
        torch_device_count=torch_device_count,
        torch_device_name=torch_device_name,
        nvml_error=nvml_error,
        torch_error=torch_error,
    )


def print_hardware_report(info: HardwareInfo) -> None:
    print("=" * 65)
    print("HARDWARE DETECTION REPORT")
    print("=" * 65)

    print("\n[NVIDIA / NVML]")
    print(f"NVML tersedia       : {'YA' if info.nvml_available else 'TIDAK'}")
    print(
        "GPU NVIDIA terdeteksi: "
        f"{'YA' if info.nvidia_gpu_available else 'TIDAK'}"
    )
    print(f"Jumlah GPU          : {info.gpu_count}")

    if info.gpus:
        for gpu in info.gpus:
            print()
            print(f"GPU #{gpu.index}")
            print(f"Nama                : {gpu.name}")
            print(f"Total VRAM          : {gpu.total_vram_mb:.2f} MB")
            print(f"Driver NVIDIA       : {gpu.driver_version}")

    if info.nvml_error:
        print(f"Informasi NVML      : {info.nvml_error}")

    print("\n[PYTORCH / CUDA]")
    print(
        f"PyTorch terinstal   : "
        f"{'YA' if info.torch_installed else 'TIDAK'}"
    )
    print(f"Versi PyTorch       : {info.torch_version or '-'}")
    print(
        f"CUDA Torch tersedia : "
        f"{'YA' if info.torch_cuda_available else 'TIDAK'}"
    )
    print(f"Versi CUDA Torch    : {info.torch_cuda_version or '-'}")
    print(f"Jumlah device Torch : {info.torch_device_count}")
    print(f"Device Torch utama  : {info.torch_device_name or '-'}")

    if info.torch_error:
        print(f"Informasi Torch     : {info.torch_error}")

    print("\n[KESIMPULAN]")

    if info.nvidia_gpu_available and info.torch_cuda_available:
        print("GPU NVIDIA dan PyTorch CUDA siap digunakan.")

    elif info.nvidia_gpu_available and not info.torch_cuda_available:
        print(
            "GPU NVIDIA terdeteksi, tetapi PyTorch belum dapat "
            "menggunakan CUDA."
        )
        print(
            "Kemungkinan PyTorch yang terinstal adalah versi CPU "
            "atau instalasi CUDA Torch belum sesuai."
        )

    elif not info.nvidia_gpu_available and info.torch_cuda_available:
        print(
            "PyTorch melaporkan CUDA tersedia, tetapi NVML tidak "
            "berhasil membaca GPU."
        )

    else:
        print(
            "CUDA belum tersedia. Aplikasi tetap dapat berjalan "
            "menggunakan CPU."
        )

    print("=" * 65)


def main() -> None:
    hardware_info = get_hardware_info()
    print_hardware_report(hardware_info)


if __name__ == "__main__":
    main()