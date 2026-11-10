"""Extração de texto de documentos (sem GPU)."""
from pathlib import Path


def extract_text(path: str | Path) -> tuple[str, str]:
    """Retorna (título, texto)."""
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".pdf":
        import pymupdf
        with pymupdf.open(p) as doc:
            text = "\n".join(page.get_text() for page in doc)
            title = (doc.metadata or {}).get("title") or p.stem
    elif ext == ".docx":
        import docx
        d = docx.Document(str(p))
        text = "\n".join(par.text for par in d.paragraphs)
        title = d.core_properties.title or p.stem
    elif ext in (".txt", ".md"):
        text, title = p.read_text(encoding="utf-8", errors="replace"), p.stem
    else:
        raise ValueError(f"Formato não suportado: {ext}")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not text:
        raise ValueError("Documento sem texto extraível (PDF escaneado?)")
    return title, text


def kind_for(path: str | Path) -> str:
    return {".pdf": "pdf", ".docx": "docx"}.get(Path(path).suffix.lower(), "txt")
