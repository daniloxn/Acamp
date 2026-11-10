"""Passo 3: transcreve um vídeo já baixado medindo tempo e pico de VRAM."""
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.download import download_audio
from app.gpu import vram_used_mb
from app.transcribe import run_transcription, transcript_path

info, _ = download_audio(sys.argv[1])
transcript_path(info.video_id).unlink(missing_ok=True)  # força transcrever de novo

baseline = vram_used_mb()
peak = baseline
stop = False


def monitor():
    global peak
    while not stop:
        peak = max(peak, vram_used_mb())
        time.sleep(0.5)


threading.Thread(target=monitor, daemon=True).start()
t = time.time()
data = run_transcription(info.video_id)
stop = True
elapsed = time.time() - t
time.sleep(1)

print()
print(f"Áudio: {data['duration']:.0f}s | tempo total: {elapsed:.1f}s | {len(data['segments'])} segmentos")
print(f"VRAM repouso: {baseline} MB | pico: {peak} MB (+{peak - baseline} MB) | após o processo: {vram_used_mb()} MB")
print(f"Prévia: {data['text'][:300]}...")
