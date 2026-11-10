"""Banco SQLite: aluno → matéria → assunto → fontes → itens de estudo + progresso."""
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlmodel import Field, Session, SQLModel, create_engine, select

from app.config import DATA
from app.schema import StudyContent

ENGINE = create_engine(f"sqlite:///{DATA / 'estudo.db'}", connect_args={"check_same_thread": False})


def now() -> datetime:
    return datetime.now(timezone.utc)


# ---------- organização ----------
class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime = Field(default_factory=now)


class Subject(SQLModel, table=True):  # matéria
    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    name: str


class Topic(SQLModel, table=True):  # assunto criado pelo aluno
    id: int | None = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="subject.id", index=True)
    name: str
    created_at: datetime = Field(default_factory=now)


class Source(SQLModel, table=True):  # vídeo / pdf / docx / txt
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    kind: str  # youtube | pdf | docx | txt
    ref: str  # url ou caminho do arquivo
    title: str = ""
    status: str = "queued"  # queued|downloading|transcribing|extracting|generating|done|error
    error: str | None = None
    raw_text: str | None = None  # texto tratado (transcrição ou documento)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)


# ---------- conteúdo gerado ----------
class StudyGuideRow(SQLModel, table=True):
    __tablename__ = "study_guide"
    source_id: int = Field(foreign_key="source.id", primary_key=True)
    overview: str
    sections_json: str


class SubTopicRow(SQLModel, table=True):
    """Subtópico do ASSUNTO, compartilhado entre todas as fontes dele."""
    __tablename__ = "subtopic"
    id: int | None = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", index=True)
    name: str
    norm: str = Field(index=True)  # nome normalizado, para unificar


def normalize(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", name.lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


class FlashcardRow(SQLModel, table=True):
    __tablename__ = "flashcard"
    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="source.id", index=True)
    subtopic_id: int = Field(foreign_key="subtopic.id", index=True)
    term: str
    meaning: str


class QuestionRow(SQLModel, table=True):
    __tablename__ = "question"
    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="source.id", index=True)
    subtopic_id: int = Field(foreign_key="subtopic.id", index=True)
    difficulty: str = Field(index=True)
    question: str
    options_json: str
    correct_index: int
    explanation: str


# ---------- progresso ----------
class QuestionAttempt(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    question_id: int = Field(foreign_key="question.id", index=True)
    chosen_index: int
    correct: bool
    answered_at: datetime = Field(default_factory=now)


class FlashcardReview(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id", index=True)
    flashcard_id: int = Field(foreign_key="flashcard.id", index=True)
    result: str  # errei | dificil | acertei
    reviewed_at: datetime = Field(default_factory=now)
    next_due: datetime


class TopicProgress(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    topic_id: int = Field(foreign_key="topic.id", primary_key=True)
    last_mode: str  # guia | flashcards | estudo_inteligente
    last_position: str = ""  # ex.: id da seção / do card / da questão
    updated_at: datetime = Field(default_factory=now)


def init_db() -> None:
    SQLModel.metadata.create_all(ENGINE)


def session() -> Session:
    return Session(ENGINE, expire_on_commit=False)


# ---------- organização ----------
def get_or_create_student(name: str) -> Student:
    with session() as s:
        st = s.exec(select(Student).where(Student.name == name)).first()
        if not st:
            st = Student(name=name); s.add(st); s.commit(); s.refresh(st)
        return st


def get_or_create_subject(student_id: int, name: str) -> Subject:
    with session() as s:
        sub = s.exec(select(Subject).where(Subject.student_id == student_id,
                                           func.lower(Subject.name) == name.lower())).first()
        if not sub:
            sub = Subject(student_id=student_id, name=name); s.add(sub); s.commit(); s.refresh(sub)
        return sub


def list_topics(subject_id: int) -> list[Topic]:
    with session() as s:
        return list(s.exec(select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.name)))


def get_or_create_topic(subject_id: int, name: str) -> Topic:
    """O aluno escolhe um assunto existente ou cria um novo."""
    with session() as s:
        t = s.exec(select(Topic).where(Topic.subject_id == subject_id,
                                       func.lower(Topic.name) == name.lower())).first()
        if not t:
            t = Topic(subject_id=subject_id, name=name); s.add(t); s.commit(); s.refresh(t)
        return t


def add_source(topic_id: int, kind: str, ref: str, title: str = "") -> Source:
    with session() as s:
        src = Source(topic_id=topic_id, kind=kind, ref=ref, title=title)
        s.add(src); s.commit(); s.refresh(src)
        return src


def get_source(source_id: int) -> Source:
    with session() as s:
        return s.get(Source, source_id)


def update_source(source_id: int, **fields) -> None:
    with session() as s:
        src = s.get(Source, source_id)
        for k, v in fields.items():
            setattr(src, k, v)
        src.updated_at = now()
        s.add(src); s.commit()


def save_content(source_id: int, content: StudyContent) -> None:
    """Grava os itens gerados como linhas (substitui o conteúdo anterior da fonte)."""
    with session() as s:
        topic_id = s.get(Source, source_id).topic_id
        for model in (QuestionRow, FlashcardRow, StudyGuideRow):
            for row in s.exec(select(model).where(model.source_id == source_id)):
                s.delete(row)
        s.flush()
        existing = {r.norm: r for r in s.exec(select(SubTopicRow).where(SubTopicRow.topic_id == topic_id))}
        s.add(StudyGuideRow(source_id=source_id, overview=content.study_guide.overview,
                            sections_json=json.dumps([x.model_dump() for x in content.study_guide.sections],
                                                     ensure_ascii=False)))
        idmap = {}
        for st in content.subtopics:
            row = existing.get(normalize(st.name))
            if not row:  # subtópico novo no assunto
                row = SubTopicRow(topic_id=topic_id, name=st.name, norm=normalize(st.name))
                s.add(row); s.flush()
                existing[row.norm] = row
            idmap[st.id] = row.id
        for f in content.flashcards:
            s.add(FlashcardRow(source_id=source_id, subtopic_id=idmap[f.subtopic_id],
                               term=f.term, meaning=f.meaning))
        for q in content.questions:
            s.add(QuestionRow(source_id=source_id, subtopic_id=idmap[q.subtopic_id], difficulty=q.difficulty,
                              question=q.question, options_json=json.dumps(q.options, ensure_ascii=False),
                              correct_index=q.correct_index, explanation=q.explanation))
        s.flush()
        # remove subtópicos que ficaram sem nenhum item (ex.: fonte regerada)
        used = select(FlashcardRow.subtopic_id).union(select(QuestionRow.subtopic_id))
        for row in s.exec(select(SubTopicRow).where(SubTopicRow.topic_id == topic_id,
                                                    SubTopicRow.id.not_in(used))):
            s.delete(row)
        s.commit()


def list_students() -> list[Student]:
    with session() as s:
        return list(s.exec(select(Student).order_by(Student.name)))


def list_subjects(student_id: int) -> list[Subject]:
    with session() as s:
        return list(s.exec(select(Subject).where(Subject.student_id == student_id).order_by(Subject.name)))


def get_topic(topic_id: int) -> Topic | None:
    with session() as s:
        return s.get(Topic, topic_id)


def get_subject(subject_id: int) -> Subject | None:
    with session() as s:
        return s.get(Subject, subject_id)


def list_sources(topic_id: int | None = None, pending_only: bool = False) -> list[Source]:
    with session() as s:
        q = select(Source).order_by(Source.created_at)
        if topic_id is not None:
            q = q.where(Source.topic_id == topic_id)
        if pending_only:
            q = q.where(Source.status.not_in(["done", "error"]))
        return list(s.exec(q))


def delete_source(source_id: int) -> None:
    with session() as s:
        qids = select(QuestionRow.id).where(QuestionRow.source_id == source_id)
        fids = select(FlashcardRow.id).where(FlashcardRow.source_id == source_id)
        for row in s.exec(select(QuestionAttempt).where(QuestionAttempt.question_id.in_(qids))):
            s.delete(row)
        for row in s.exec(select(FlashcardReview).where(FlashcardReview.flashcard_id.in_(fids))):
            s.delete(row)
        for model in (QuestionRow, FlashcardRow, StudyGuideRow):
            for row in s.exec(select(model).where(model.source_id == source_id)):
                s.delete(row)
        src = s.get(Source, source_id)
        topic_id = src.topic_id
        s.delete(src)
        s.flush()
        used = select(FlashcardRow.subtopic_id).union(select(QuestionRow.subtopic_id))
        for row in s.exec(select(SubTopicRow).where(SubTopicRow.topic_id == topic_id,
                                                    SubTopicRow.id.not_in(used))):
            s.delete(row)
        s.commit()


def topic_stats(student_id: int, topic_id: int) -> dict:
    p = get_progress(student_id, topic_id)
    with session() as s:
        n_src = s.exec(select(func.count()).select_from(Source).where(Source.topic_id == topic_id)).one()
        n_fc = s.exec(select(func.count()).select_from(FlashcardRow).join(Source)
                      .where(Source.topic_id == topic_id)).one()
    return {**p, "sources": n_src, "flashcards": n_fc}


def last_answers(student_id: int, question_ids: list[int]) -> dict[int, QuestionAttempt]:
    with session() as s:
        rows = s.exec(select(QuestionAttempt).where(QuestionAttempt.student_id == student_id,
                                                    QuestionAttempt.question_id.in_(question_ids))
                      .order_by(QuestionAttempt.answered_at))
        return {r.question_id: r for r in rows}


def last_reviews(student_id: int, flashcard_ids: list[int]) -> dict[int, FlashcardReview]:
    with session() as s:
        rows = s.exec(select(FlashcardReview).where(FlashcardReview.student_id == student_id,
                                                    FlashcardReview.flashcard_id.in_(flashcard_ids))
                      .order_by(FlashcardReview.reviewed_at))
        return {r.flashcard_id: r for r in rows}


# ---------- consultas de estudo ----------
def topic_subtopics(topic_id: int) -> list[SubTopicRow]:
    with session() as s:
        return list(s.exec(select(SubTopicRow).where(SubTopicRow.topic_id == topic_id).order_by(SubTopicRow.id)))


def smart_questions(student_id: int, topic_id: int, difficulties: list[str] | None = None,
                    subtopic_ids: list[int] | None = None, skip_answered_correctly: bool = False,
                    limit: int = 20) -> list[QuestionRow]:
    """Estudo inteligente: filtra por nível e tópicos; opcionalmente esconde as já acertadas."""
    with session() as s:
        q = select(QuestionRow).join(Source).where(Source.topic_id == topic_id)
        if difficulties:
            q = q.where(QuestionRow.difficulty.in_(difficulties))
        if subtopic_ids:
            q = q.where(QuestionRow.subtopic_id.in_(subtopic_ids))
        if skip_answered_correctly:
            done = select(QuestionAttempt.question_id).where(QuestionAttempt.student_id == student_id,
                                                             QuestionAttempt.correct == True)  # noqa: E712
            q = q.where(QuestionRow.id.not_in(done))
        return list(s.exec(q.order_by(func.random()).limit(limit)))


def topic_flashcards(topic_id: int, subtopic_ids: list[int] | None = None) -> list[FlashcardRow]:
    with session() as s:
        q = select(FlashcardRow).join(Source).where(Source.topic_id == topic_id)
        if subtopic_ids:
            q = q.where(FlashcardRow.subtopic_id.in_(subtopic_ids))
        return list(s.exec(q))


def topic_guides(topic_id: int) -> list[StudyGuideRow]:
    with session() as s:
        return list(s.exec(select(StudyGuideRow).join(Source).where(Source.topic_id == topic_id)))


# ---------- progresso ----------
def record_attempt(student_id: int, question_id: int, chosen_index: int) -> bool:
    with session() as s:
        q = s.get(QuestionRow, question_id)
        ok = chosen_index == q.correct_index
        s.add(QuestionAttempt(student_id=student_id, question_id=question_id, chosen_index=chosen_index, correct=ok))
        s.commit()
        return ok


_INTERVAL = {"errei": timedelta(minutes=10), "dificil": timedelta(days=1), "acertei": timedelta(days=3)}


def record_review(student_id: int, flashcard_id: int, result: str) -> None:
    with session() as s:
        s.add(FlashcardReview(student_id=student_id, flashcard_id=flashcard_id, result=result,
                              next_due=now() + _INTERVAL[result]))
        s.commit()


def save_position(student_id: int, topic_id: int, mode: str, position: str = "") -> None:
    with session() as s:
        p = s.get(TopicProgress, (student_id, topic_id)) or TopicProgress(
            student_id=student_id, topic_id=topic_id, last_mode=mode)
        p.last_mode, p.last_position, p.updated_at = mode, position, now()
        s.add(p); s.commit()


def get_progress(student_id: int, topic_id: int) -> dict:
    with session() as s:
        qids = select(QuestionRow.id).join(Source).where(Source.topic_id == topic_id)
        total = s.exec(select(func.count()).select_from(qids.subquery())).one()
        attempts = list(s.exec(select(QuestionAttempt).where(QuestionAttempt.student_id == student_id,
                                                             QuestionAttempt.question_id.in_(qids))
                               .order_by(QuestionAttempt.answered_at)))
        last = {}
        for a in attempts:
            last[a.question_id] = a.correct  # última tentativa vale
        pos = s.get(TopicProgress, (student_id, topic_id))
        return {
            "questions_total": total,
            "questions_answered": len(last),
            "questions_correct": sum(last.values()),
            "wrong_question_ids": sorted(k for k, v in last.items() if not v),
            "last_mode": pos.last_mode if pos else None,
            "last_position": pos.last_position if pos else None,
            "updated_at": pos.updated_at.isoformat() if pos else None,
        }
