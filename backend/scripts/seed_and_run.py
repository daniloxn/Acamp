"""Teste ponta a ponta v2: aluno → matéria → assunto → 2 fontes (vídeo + PDF) → banco → consultas."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pymupdf

from app import db
from app.config import DATA
from app.pipeline import process
from app.transcribe import load_transcript

db.init_db()
aluno = db.get_or_create_student("Aluno Teste")
bio = db.get_or_create_subject(aluno.id, "Biologia")
assunto = db.get_or_create_topic(bio.id, "Fotossíntese")  # existente ou novo

# PDF de teste feito a partir de outra aula em cache
pdf = DATA / "docs" / "fotossintese_resumo.pdf"
if not pdf.exists():
    pdf.parent.mkdir(exist_ok=True)
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_textbox(page.rect + (40, 40, -40, -40), load_transcript("y0T4gzHg_fs")["text"], fontsize=8)
    doc.set_metadata({"title": "Fotossíntese - resumo (PDF)"})
    doc.save(pdf)

sources = [db.add_source(assunto.id, "youtube", "https://www.youtube.com/watch?v=zSOE1uRloZg"),
           db.add_source(assunto.id, "pdf", str(pdf))]
for s in sources:
    process(s.id)
    print("status:", db.get_source(s.id).status)

subs = db.topic_subtopics(assunto.id)
print("\nSubtópicos do assunto:", [(s.id, s.name) for s in subs])
print("Guias:", len(db.topic_guides(assunto.id)), "| Flashcards:", len(db.topic_flashcards(assunto.id)))
fc = db.topic_flashcards(assunto.id)[0]
print(f"Flashcard: [{fc.term}] → {fc.meaning}")

allq = db.smart_questions(aluno.id, assunto.id, limit=999)
print("Questões por nível:", dict(collections.Counter(q.difficulty for q in allq)))
print("correct_index:", dict(collections.Counter(q.correct_index for q in allq)))

alvo = [subs[0].id, subs[1].id]
filt = db.smart_questions(aluno.id, assunto.id, difficulties=["dificil"], subtopic_ids=alvo)
assert all(q.difficulty == "dificil" and q.subtopic_id in alvo for q in filt)
print(f"Filtro (difícil, subtópicos {alvo}): {len(filt)} questões OK")

# progresso: responde 3 (uma errada), revisa card, salva posição
for i, q in enumerate(allq[:3]):
    db.record_attempt(aluno.id, q.id, q.correct_index if i else (q.correct_index + 1) % 4)
db.record_review(aluno.id, fc.id, "dificil")
db.save_position(aluno.id, assunto.id, "estudo_inteligente", f"question:{allq[2].id}")
print("Progresso:", json.dumps(db.get_progress(aluno.id, assunto.id), ensure_ascii=False))
rest = db.smart_questions(aluno.id, assunto.id, skip_answered_correctly=True, limit=999)
print(f"Sem as já acertadas: {len(rest)} de {len(allq)}")
