"""Schema v2 do material de estudo — fonte única da verdade.

`StudyContent` é o que a LLM gera (passado ao Ollama como `format`). Alimenta as três áreas do app:
- Guia de estudo  → `study_guide` (visão geral + seções com pontos principais)
- Flashcards      → `flashcards` (frente = termo/conceito, verso = só o significado)
- Estudo inteligente → `questions`, cada uma com `difficulty` e `subtopic_id` para filtrar
O banco (app/db.py) grava cada item como linha; este JSON também fica salvo como backup.
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

SCHEMA_VERSION = "2.0"

NonEmpty = Annotated[str, Field(min_length=1)]
Difficulty = Literal["facil", "medio", "dificil"]


class SubTopic(BaseModel):
    id: int = Field(ge=1)
    name: NonEmpty = Field(description="Nome curto do tópico abordado no conteúdo.")


class GuideSection(BaseModel):
    title: NonEmpty
    summary: NonEmpty = Field(description="Explicação didática desta parte do conteúdo.")
    key_points: list[NonEmpty] = Field(min_length=1, description="Pontos principais para estudar.")


class StudyGuide(BaseModel):
    overview: NonEmpty = Field(description="Resumo geral do assunto em 2-4 frases.")
    sections: list[GuideSection] = Field(min_length=1)


class Flashcard(BaseModel):
    subtopic_id: int
    term: NonEmpty = Field(description="Frente: termo ou conceito do conteúdo.")
    meaning: NonEmpty = Field(description="Verso: somente o significado / o que é.")


class Question(BaseModel):
    subtopic_id: int
    difficulty: Difficulty
    question: NonEmpty
    options: list[NonEmpty] = Field(min_length=4, max_length=4, description="Exatamente 4 alternativas.")
    correct_index: int = Field(ge=0, le=3)
    explanation: NonEmpty


class StudyContent(BaseModel):
    """O que a LLM deve gerar."""
    subtopics: list[SubTopic] = Field(min_length=1, max_length=10)
    study_guide: StudyGuide
    flashcards: list[Flashcard] = Field(min_length=5)
    questions: list[Question] = Field(min_length=6)

    @model_validator(mode="after")
    def _refs_ok(self):
        ids = {s.id for s in self.subtopics}
        bad = [i.subtopic_id for i in [*self.flashcards, *self.questions] if i.subtopic_id not in ids]
        if bad:
            raise ValueError(f"subtopic_id inexistente: {sorted(set(bad))}; válidos: {sorted(ids)}")
        return self


class SourceInfo(BaseModel):
    source_id: int
    kind: str
    ref: str
    title: str


class Meta(BaseModel):
    schema_version: str = SCHEMA_VERSION
    llm_model: str
    generated_at: datetime
    generation_seconds: float


class StudyMaterial(StudyContent):
    """Backup salvo em data/study/{source_id}.json."""
    source: SourceInfo
    meta: Meta
