"""Transcrição com faster-whisper na GPU.

Deve ser executado como PROCESSO SEPARADO (`python -m app.transcribe <video_id>`):
quando o processo termina, o Windows libera 100% da VRAM do Whisper, garantindo
que a etapa da LLM só comece com a GPU livre. Use `run_transcription()` do pipeline.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from app.config import (
    AUDIO_DIR, TRANSCRIPT_DIR, WHISPER_COMPUTE, WHISPER_LANG, WHISPER_MODEL,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]


def transcript_path(video_id: str) -> Path:
    return TRANSCRIPT_DIR / f"{video_id}.json"


def load_transcript(video_id: str) -> dict | None:
    p = transcript_path(video_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _transcribe_in_process(video_id: str) -> dict:
    from app.gpu import load_cuda_dlls
    load_cuda_dlls()
    from faster_whisper import WhisperModel

    meta = json.loads((AUDIO_DIR / f"{video_id}.meta.json").read_text(encoding="utf-8"))
    t0 = time.time()
    model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type=WHISPER_COMPUTE)
    segments, info = model.transcribe(
        meta["audio_path"],
        language=WHISPER_LANG,
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )
    segs = []
    for s in segments:
        text = s.text.strip()
        if text:
            segs.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": text})
            print(f"  [{s.start:6.1f}s] {text}", flush=True)

    data = {
        "video_id": video_id,
        "title": meta["title"],
        "url": meta["url"],
        "duration": round(info.duration, 2),
        "language": info.language,
        "model": f"faster-whisper/{WHISPER_MODEL}/{WHISPER_COMPUTE}",
        "processing_seconds": round(time.time() - t0, 2),
        "segments": segs,
        "text": " ".join(s["text"] for s in segs),
    }
    out = transcript_path(video_id)
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(out)
    return data


def run_transcription(video_id: str) -> dict:
    """Roda a transcrição em subprocesso e BLOQUEIA até ele terminar (VRAM liberada)."""
    cached = load_transcript(video_id)
    if cached:
        return cached
    proc = subprocess.run(
        [sys.executable, "-m", "app.transcribe", video_id],
        cwd=BACKEND_DIR,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Transcrição falhou (código {proc.returncode})")
    data = load_transcript(video_id)
    if not data:
        raise RuntimeError("Transcrição terminou mas o cache não foi gravado")
    return data


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    _transcribe_in_process(sys.argv[1])
