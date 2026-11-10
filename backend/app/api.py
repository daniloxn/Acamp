"""API HTTP do app. Rodar: cd backend && uv run uvicorn app.api:app --host 0.0.0.0 --port 8000"""
import json
import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import db, worker
from app.config import DATA, ROOT
from app.extract import kind_for

UPLOAD_DIR = DATA / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DIST = ROOT / "frontend" / "dist"
YT = re.compile(r"(youtube\.com|youtu\.be)/", re.I)


@asynccontextmanager
async def lifespan(_):
    db.init_db()
    worker.start()
    yield


app = FastAPI(title="Acamp", lifespan=lifespan)


class Name(BaseModel):
    name: str


class Answer(BaseModel):
    student_id: int
    chosen_index: int


class Review(BaseModel):
    student_id: int
    result: str


class Position(BaseModel):
    mode: str
    position: str = ""


def _404(obj, what="registro"):
    if obj is None:
        raise HTTPException(404, f"{what} não encontrado")
    return obj


def _clean(name: str) -> str:
    name = " ".join(name.split())
    if not name:
        raise HTTPException(422, "nome vazio")
    return name


# ---------- organização ----------
@app.get("/api/students")
def students():
    return db.list_students()


@app.post("/api/students")
def create_student(body: Name):
    return db.get_or_create_student(_clean(body.name))


@app.get("/api/students/{sid}/subjects")
def subjects(sid: int):
    out = []
    for sub in db.list_subjects(sid):
        topics = [{**t.model_dump(), "stats": db.topic_stats(sid, t.id)} for t in db.list_topics(sub.id)]
        out.append({**sub.model_dump(), "topics": topics})
    return out


@app.post("/api/students/{sid}/subjects")
def create_subject(sid: int, body: Name):
    return db.get_or_create_subject(sid, _clean(body.name))


@app.get("/api/subjects/{subject_id}/topics")
def topics(subject_id: int):
    return db.list_topics(subject_id)


@app.post("/api/subjects/{subject_id}/topics")
def create_topic(subject_id: int, body: Name):
    _404(db.get_subject(subject_id), "matéria")
    return db.get_or_create_topic(subject_id, _clean(body.name))


@app.get("/api/topics/{topic_id}")
def topic(topic_id: int):
    t = _404(db.get_topic(topic_id), "assunto")
    return {**t.model_dump(), "subject": db.get_subject(t.subject_id)}


# ---------- fontes ----------
def _source_out(s: db.Source) -> dict:
    d = s.model_dump(exclude={"raw_text"})
    d["chars"] = len(s.raw_text or "")
    return d


@app.post("/api/topics/{topic_id}/sources")
async def add_source(topic_id: int, request: Request):
    _404(db.get_topic(topic_id), "assunto")
    if request.headers.get("content-type", "").startswith("multipart/"):
        form = await request.form()
        up = form.get("file")
        if not up or not getattr(up, "filename", None):
            raise HTTPException(422, "arquivo ausente")
        ext = Path(up.filename).suffix.lower()
        if ext not in (".pdf", ".docx", ".txt", ".md"):
            raise HTTPException(422, "use PDF, DOCX ou TXT")
        dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
        dest.write_bytes(await up.read())
        src = db.add_source(topic_id, kind_for(dest), str(dest), title=Path(up.filename).stem)
    else:
        body = await request.json()
        url = (body.get("url") or "").strip()
        if not YT.search(url):
            raise HTTPException(422, "link do YouTube inválido")
        src = db.add_source(topic_id, "youtube", url)
    worker.enqueue(src.id)
    return _source_out(db.get_source(src.id))


@app.get("/api/topics/{topic_id}/sources")
def sources(topic_id: int):
    return [_source_out(s) for s in db.list_sources(topic_id)]


@app.post("/api/sources/{source_id}/retry")
def retry(source_id: int):
    _404(db.get_source(source_id), "fonte")
    worker.enqueue(source_id)
    return _source_out(db.get_source(source_id))


@app.delete("/api/sources/{source_id}")
def delete(source_id: int):
    src = _404(db.get_source(source_id), "fonte")
    if src.status not in ("done", "error", "queued"):
        raise HTTPException(409, "fonte em processamento; aguarde terminar")
    db.delete_source(source_id)
    return {"ok": True}


# ---------- estudo ----------
def _ids(s: str | None) -> list[int] | None:
    return [int(x) for x in s.split(",") if x.strip()] if s else None


@app.get("/api/topics/{topic_id}/guide")
def guide(topic_id: int):
    srcs = {s.id: s for s in db.list_sources(topic_id)}
    return [{"source_id": g.source_id, "source_title": srcs[g.source_id].title,
             "source_kind": srcs[g.source_id].kind, "overview": g.overview,
             "sections": json.loads(g.sections_json)} for g in db.topic_guides(topic_id)]


@app.get("/api/topics/{topic_id}/subtopics")
def subtopics(topic_id: int):
    return db.topic_subtopics(topic_id)


@app.get("/api/topics/{topic_id}/flashcards")
def flashcards(topic_id: int, student_id: int, subtopics: str | None = None):
    cards = db.topic_flashcards(topic_id, _ids(subtopics))
    last = db.last_reviews(student_id, [c.id for c in cards])
    return [{**c.model_dump(), "last_result": last[c.id].result if c.id in last else None,
             "next_due": (lambda d: d.isoformat() if d.tzinfo else d.isoformat() + "Z")(last[c.id].next_due) if c.id in last else None} for c in cards]


@app.post("/api/flashcards/{fid}/review")
def review(fid: int, body: Review):
    if body.result not in ("errei", "dificil", "acertei"):
        raise HTTPException(422, "resultado inválido")
    db.record_review(body.student_id, fid, body.result)
    return {"ok": True}


@app.get("/api/topics/{topic_id}/questions")
def questions(topic_id: int, student_id: int, difficulty: str | None = None, subtopics: str | None = None,
              skip_correct: bool = False, limit: int = 10):
    diffs = [d for d in (difficulty or "").split(",") if d] or None
    qs = db.smart_questions(student_id, topic_id, diffs, _ids(subtopics), skip_correct, limit)
    return [{"id": q.id, "subtopic_id": q.subtopic_id, "difficulty": q.difficulty, "question": q.question,
             "options": json.loads(q.options_json)} for q in qs]  # sem a resposta!


@app.post("/api/questions/{qid}/answer")
def answer(qid: int, body: Answer):
    with db.session() as s:
        q = _404(s.get(db.QuestionRow, qid), "questão")
    ok = db.record_attempt(body.student_id, qid, body.chosen_index)
    return {"correct": ok, "correct_index": q.correct_index, "explanation": q.explanation}


@app.get("/api/students/{sid}/topics/{tid}/progress")
def progress(sid: int, tid: int):
    return db.topic_stats(sid, tid)


@app.put("/api/students/{sid}/topics/{tid}/progress")
def save_progress(sid: int, tid: int, body: Position):
    db.save_position(sid, tid, body.mode, body.position)
    return {"ok": True}


# ---------- frontend compilado ----------
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = DIST / path
        return FileResponse(f if path and f.is_file() else DIST / "index.html")
