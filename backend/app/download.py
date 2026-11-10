"""Baixa apenas o áudio de um vídeo do YouTube com yt-dlp (com cache por video_id)."""
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import yt_dlp

from app.config import AUDIO_DIR


@dataclass
class AudioInfo:
    video_id: str
    title: str
    url: str
    duration: float
    audio_path: str


# YouTube exige resolver desafios JS; o Node já está instalado na máquina.
BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "js_runtimes": {"node": {}},
}

# Vídeos podem ter faixas dubladas por IA (ex.: en-US "dubbed-auto").
# Sempre preferir a faixa original para o Whisper transcrever o áudio real.
AUDIO_FORMAT = (
    "bestaudio[ext=m4a][format_note*=original]"
    "/bestaudio[format_note*=original]"
    "/bestaudio[ext=m4a]/bestaudio"
)


def _meta_path(video_id: str) -> Path:
    return AUDIO_DIR / f"{video_id}.meta.json"


def download_audio(url: str) -> tuple[AudioInfo, bool]:
    """Retorna (info, baixou_agora). Não baixa de novo se já existir em cache."""
    with yt_dlp.YoutubeDL(BASE_OPTS) as ydl:
        meta = ydl.extract_info(url, download=False)
    video_id = meta["id"]

    cached = _meta_path(video_id)
    if cached.exists():
        info = AudioInfo(**json.loads(cached.read_text(encoding="utf-8")))
        if Path(info.audio_path).exists():
            return info, False

    opts = {
        **BASE_OPTS,
        "format": AUDIO_FORMAT,
        "outtmpl": str(AUDIO_DIR / "%(id)s.%(ext)s"),
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        result = ydl.extract_info(url, download=True)
        audio_path = ydl.prepare_filename(result)
        print(f"  formato escolhido: {result.get('format_id')} ({result.get('format_note')})")

    info = AudioInfo(
        video_id=video_id,
        title=result.get("title", ""),
        url=result.get("webpage_url", url),
        duration=float(result.get("duration") or 0),
        audio_path=audio_path,
    )
    cached.write_text(json.dumps(asdict(info), ensure_ascii=False, indent=2), encoding="utf-8")
    return info, True
