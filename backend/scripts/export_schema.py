"""Passo 4: exporta o JSON Schema (contrato com o frontend)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import SCHEMA_DIR
from app.schema import StudyContent, StudyMaterial

for name, model in [("study_material", StudyMaterial), ("study_content_llm", StudyContent)]:
    out = SCHEMA_DIR / f"{name}.schema.json"
    out.write_text(json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {out.relative_to(SCHEMA_DIR.parents[1])}")
