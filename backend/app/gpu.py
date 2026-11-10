"""Utilitários de GPU: carregamento das DLLs CUDA (Windows) e controle de VRAM.

As DLLs do cuBLAS/cuDNN vêm dos pacotes pip `nvidia-*`; no Windows elas precisam
ser registradas antes de importar ctranslate2/faster_whisper.
"""
import os
import site
import subprocess
import time

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

_dlls_loaded = False


def load_cuda_dlls() -> None:
    global _dlls_loaded
    if _dlls_loaded:
        return
    for p in site.getsitepackages():
        nv = os.path.join(p, "nvidia")
        if not os.path.isdir(nv):
            continue
        for sub in os.listdir(nv):
            b = os.path.join(nv, sub, "bin")
            if os.path.isdir(b):
                try:
                    os.add_dll_directory(b)
                except OSError:
                    pass
                os.environ["PATH"] = b + os.pathsep + os.environ["PATH"]
    _dlls_loaded = True


def vram_used_mb() -> int:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    ).stdout
    return int(out.strip().splitlines()[0])


def wait_vram_free(baseline_mb: int, tolerance_mb: int = 400, timeout_s: float = 60) -> int:
    """Bloqueia até a VRAM usada voltar para perto do baseline (GPU liberada)."""
    deadline = time.time() + timeout_s
    used = vram_used_mb()
    while used > baseline_mb + tolerance_mb:
        if time.time() > deadline:
            raise TimeoutError(
                f"VRAM não liberou: {used} MB em uso (repouso {baseline_mb} MB)"
            )
        time.sleep(1)
        used = vram_used_mb()
    return used
