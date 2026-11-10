"""Passo 2: baixa o áudio e confirma que a segunda chamada usa o cache."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.download import download_audio

url = sys.argv[1]
t = time.time()
info, fresh = download_audio(url)
size = Path(info.audio_path).stat().st_size / 1e6
print(f"[{'baixado' if fresh else 'cache'}] {info.video_id} | {info.title} | {info.duration:.0f}s | {size:.1f} MB | {time.time()-t:.1f}s")

t = time.time()
_, fresh2 = download_audio(url)
print(f"2ª chamada: {'baixou de novo (ERRO)' if fresh2 else 'usou cache (OK)'} em {time.time()-t:.1f}s")
