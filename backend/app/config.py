from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
AUDIO_DIR = DATA / "audio"
TRANSCRIPT_DIR = DATA / "transcripts"
STUDY_DIR = DATA / "study"
SCHEMA_DIR = ROOT / "backend" / "schema"

WHISPER_MODEL = "medium"
WHISPER_COMPUTE = "float16"
WHISPER_LANG = "pt"

OLLAMA_MODEL = "qwen3:8b"
# 16k de contexto não cabe nos ~5,7GB livres (o desktop usa ~2,4GB) → 20% iria para a CPU.
# Com 8k o qwen3:8b fica 100% na GPU.
OLLAMA_CTX = 8192

for d in (AUDIO_DIR, TRANSCRIPT_DIR, STUDY_DIR, SCHEMA_DIR):
    d.mkdir(parents=True, exist_ok=True)
