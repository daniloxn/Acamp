"""Passo 1: valida que o CTranslate2 enxerga a RTX 5050 (sm_120) e roda float16."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from app.gpu import load_cuda_dlls, vram_used_mb

load_cuda_dlls()
import ctranslate2  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

print(f"ctranslate2 {ctranslate2.__version__}")
n = ctranslate2.get_cuda_device_count()
print(f"Dispositivos CUDA: {n}")
if n == 0:
    sys.exit("FALHA: nenhuma GPU CUDA detectada")

types = ctranslate2.get_supported_compute_types("cuda")
print(f"Compute types suportados: {sorted(types)}")
if "float16" not in types:
    sys.exit("FALHA: float16 não suportado")

print(f"VRAM antes: {vram_used_mb()} MB")
model = WhisperModel("tiny", device="cuda", compute_type="float16")
segments, info = model.transcribe(np.zeros(16000, dtype=np.float32), language="pt")
list(segments)  # força a execução do kernel na GPU
print(f"VRAM com tiny carregado: {vram_used_mb()} MB")
print("OK: Whisper rodou na GPU sem erro de kernel")
