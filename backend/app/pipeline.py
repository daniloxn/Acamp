"""Pipeline por fonte (Source do banco), com etapas ESTRITAMENTE sequenciais na GPU.

youtube: download → [GPU livre] → transcrição (subprocesso) → [GPU livre] → LLM → banco
pdf/docx/txt: extração (CPU) → [GPU livre] → LLM → banco
Whisper e LLM nunca rodam ao mesmo tempo. O status de cada etapa fica em Source.status.
"""
import sys
import threading
import time

from app import db
from app.download import download_audio
from app.extract import extract_text
from app.gpu import vram_used_mb, wait_vram_free
from app.llm import generate_study_content, loaded_models, save_backup, unload_all_models
from app.schema import SourceInfo
from app.transcribe import run_transcription

GPU_LOCK = threading.Lock()  # um único job na GPU por vez


def _log(sid: int, stage: str, msg: str = "") -> None:
    print(f"[{time.strftime('%H:%M:%S')}] #{sid} {stage:<12} {msg}", flush=True)


def _ensure_gpu_free(baseline: int) -> None:
    if loaded_models():
        unload_all_models()
    wait_vram_free(baseline)


def _stage(sid: int, status: str, msg: str = "") -> None:
    db.update_source(sid, status=status)
    _log(sid, status, msg)


def process(source_id: int) -> None:
    src = db.get_source(source_id)
    t0 = time.time()
    try:
        if src.kind == "youtube":
            _stage(source_id, "downloading", src.ref)
            info, _ = download_audio(src.ref)
            db.update_source(source_id, title=info.title)
            title = info.title
        else:
            _stage(source_id, "extracting", src.ref)
            title, text = extract_text(src.ref)
            db.update_source(source_id, title=src.title or title, raw_text=text)

        with GPU_LOCK:
            unload_all_models()
            time.sleep(1)
            baseline = vram_used_mb()
            if src.kind == "youtube":
                _stage(source_id, "transcribing")
                transcript = run_transcription(info.video_id)  # bloqueia até o processo sair
                text = transcript["text"]
                db.update_source(source_id, raw_text=text)
                _ensure_gpu_free(baseline)

            _stage(source_id, "generating", f"{len(text)} caracteres")
            tg = time.time()
            known = [s.name for s in db.topic_subtopics(src.topic_id)]
            content = generate_study_content(title, text, known)
            _ensure_gpu_free(baseline)

        db.save_content(source_id, content)
        save_backup(SourceInfo(source_id=source_id, kind=src.kind, ref=src.ref, title=title),
                    content, time.time() - tg)
        _stage(source_id, "done", f"{time.time() - t0:.0f}s")
    except Exception as e:
        db.update_source(source_id, status="error", error=str(e)[:2000])
        _log(source_id, "error", str(e))
        raise


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    db.init_db()
    process(int(sys.argv[1]))
