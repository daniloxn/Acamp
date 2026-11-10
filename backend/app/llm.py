"""Geração do material de estudo (schema v2) com Ollama local + validação + gravação atômica."""
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import ollama
from pydantic import ValidationError

from app.config import OLLAMA_CTX, OLLAMA_MODEL, STUDY_DIR
from app.schema import Meta, SourceInfo, StudyContent, StudyMaterial

# ~3,5 chars/token em PT → ~3,5k tokens de entrada, deixando ~4,5k do contexto de 8k para o JSON.
MAX_DIRECT_CHARS = 12_000
CHUNK_CHARS = 10_000

SYSTEM_PROMPT = """Você é um professor especialista em criar material de estudo em português do Brasil.
Você recebe o TEXTO de uma aula (transcrição de vídeo ou documento) e gera material de estudo estruturado.

Regras obrigatórias:
1. Use SOMENTE o conteúdo do texto. Não invente fatos. Corrija erros óbvios de reconhecimento de fala.
2. Tudo em português do Brasil, linguagem clara e didática.
3. subtopics: 3 a 6 tópicos que dividem o conteúdo, ids 1, 2, 3...
4. study_guide: overview = resumo geral em 2-4 frases; sections = uma seção por parte importante,
   com summary explicativo e key_points (os pontos principais para estudar).
5. flashcards: {n_cards} cards. term = um termo ou conceito citado (curto, ex.: "Clorofila");
   meaning = SOMENTE o significado / o que é, em 1-2 frases. Nada de perguntas na frente.
6. questions: {n_q} questões de múltipla escolha, EXATAMENTE {n_lvl} de cada difficulty:
   {n_lvl} "facil" (lembrar/definir), {n_lvl} "medio" (compreender/relacionar) e {n_lvl} "dificil" (aplicar/analisar).
   EXATAMENTE 4 alternativas, apenas UMA correta, correct_index 0-3 aponta para ela.
   explanation justifica a resposta. Cubra todos os subtópicos.
7. Todo subtopic_id de flashcards e questions deve ser um id existente em subtopics.
8. Responda APENAS com o JSON no schema fornecido."""


def _counts(chars: int) -> tuple[int, int]:
    # tamanho do conteúdo em ~minutos de fala (≈ 850 chars/min)
    minutes = max(chars / 850, 1)
    n_cards = int(min(max(minutes * 1.5, 8), 18))
    n_q = int(min(max(minutes, 6), 12)) // 3 * 3  # múltiplo de 3 (um terço por nível)
    return n_cards, n_q


def _chat(messages: list[dict], fmt: dict | None) -> str:
    resp = ollama.chat(
        model=OLLAMA_MODEL, messages=messages, format=fmt, think=False,
        keep_alive=0,  # descarrega o modelo da VRAM ao terminar
        options={"temperature": 0.2, "num_ctx": OLLAMA_CTX},
    )
    return resp.message.content


def _condense(text: str) -> str:
    parts = [text[i:i + CHUNK_CHARS] for i in range(0, len(text), CHUNK_CHARS)]
    notes = []
    for i, part in enumerate(parts, 1):
        print(f"  condensando parte {i}/{len(parts)}...", flush=True)
        notes.append(_chat([
            {"role": "system", "content": "Resuma em português do Brasil, em tópicos detalhados, TODOS os conceitos, definições, exemplos e números deste trecho de aula. Não invente nada."},
            {"role": "user", "content": part},
        ], fmt=None))
    return "\n\n".join(notes)


def _shuffle_options(content: StudyContent, rng: random.Random) -> None:
    """A LLM tende a pôr a correta sempre nas mesmas posições; embaralha mantendo a resposta."""
    for q in content.questions:
        correct = q.options[q.correct_index]
        rng.shuffle(q.options)
        q.correct_index = q.options.index(correct)


def _level_counts(content: StudyContent) -> dict[str, int]:
    counts = {"facil": 0, "medio": 0, "dificil": 0}
    for q in content.questions:
        counts[q.difficulty] += 1
    return counts


def _balance(content: StudyContent, n_lvl: int) -> None:
    """Corta o excesso: cada nível fica com no máximo o mesmo número do menor (e nunca mais que n_lvl)."""
    cap = min(max(min(_level_counts(content).values()), n_lvl - 1), n_lvl)
    seen = {"facil": 0, "medio": 0, "dificil": 0}
    kept = []
    for q in content.questions:
        if seen[q.difficulty] < cap:
            seen[q.difficulty] += 1
            kept.append(q)
    if len(kept) >= 6:
        content.questions = kept


def generate_study_content(title: str, text: str, existing_subtopics: list[str] = (),
                           max_attempts: int = 3) -> StudyContent:
    n_cards, n_q = _counts(len(text))
    if len(text) > MAX_DIRECT_CHARS:
        text = _condense(text)
    n_lvl = n_q // 3
    system = SYSTEM_PROMPT.format(n_cards=n_cards, n_q=n_q, n_lvl=n_lvl)
    if existing_subtopics:
        system += ("\n\nEste assunto JÁ TEM os subtópicos abaixo (de outras fontes). Quando o conteúdo tratar "
                   "do mesmo tema, REUTILIZE o nome EXATAMENTE igual; só crie um subtópico novo se for um tema "
                   "diferente de todos:\n" + "\n".join(f"- {n}" for n in existing_subtopics))
    user = f"Título: {title}\n\nTEXTO DA AULA:\n{text}"
    schema = StudyContent.model_json_schema()
    last_err = None
    for attempt in range(1, max_attempts + 1):
        extra = f"\n\nATENÇÃO: a tentativa anterior falhou na validação:\n{last_err}" if last_err else ""
        raw = _chat([{"role": "system", "content": system + extra}, {"role": "user", "content": user}], fmt=schema)
        try:
            content = StudyContent.model_validate_json(raw)
        except ValidationError as e:
            last_err = e
            print(f"  tentativa {attempt}: JSON inválido ({e.error_count()} erros), tentando de novo...", flush=True)
            continue
        counts = _level_counts(content)
        if min(counts.values()) < n_lvl - 1 and attempt < max_attempts:
            # desequilíbrio grande entre níveis: pede de novo (o último resultado válido é aceito)
            last_err = f"as questões vieram {counts}; precisa de EXATAMENTE {n_lvl} de cada nível."
            print(f"  tentativa {attempt}: níveis desequilibrados {counts}, tentando de novo...", flush=True)
            continue
        _balance(content, n_lvl)
        _shuffle_options(content, random.Random(title))
        return content
    raise RuntimeError(f"LLM não gerou JSON válido após {max_attempts} tentativas: {last_err}")


def save_backup(info: SourceInfo, content: StudyContent, seconds: float) -> Path:
    material = StudyMaterial(
        **content.model_dump(), source=info,
        meta=Meta(llm_model=f"ollama/{OLLAMA_MODEL}", generated_at=datetime.now(timezone.utc),
                  generation_seconds=round(seconds, 2)),
    )
    out = STUDY_DIR / f"source_{info.source_id}.json"
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(material.model_dump_json(indent=2), encoding="utf-8")
    StudyMaterial.model_validate_json(tmp.read_text(encoding="utf-8"))
    tmp.replace(out)
    return out


def loaded_models() -> list[str]:
    return [m.model for m in ollama.ps().models]


def unload_all_models() -> None:
    for name in loaded_models():
        ollama.generate(model=name, prompt="", keep_alive=0)
