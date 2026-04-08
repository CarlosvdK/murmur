"""
SchemaLoader -- reads survey_schema.yaml at startup and provides
typed access to field definitions.

In development: hot-reloads when file changes.
In production: cached at startup.

Usage:
    from backend.survey.schema_loader import get_schema
    schema = get_schema()
    rag_fields = schema.fields_for_rag("workspace")
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field as dc_field

import yaml

SCHEMA_PATH = Path(__file__).parent.parent.parent / "config" / "survey_schema.yaml"


@dataclass
class StorageConfig:
    strategy: str
    table: str
    column: Optional[str] = None
    jsonb_key: Optional[str] = None


@dataclass
class RAGConfig:
    include: bool
    weight: str
    section: str
    template: str


@dataclass
class PersonaConfig:
    include: bool
    weight: str
    prompt_fragment: str
    influence_description: str


@dataclass
class DerivedFeature:
    id: str
    label: str
    compute: str
    feature_type: str


@dataclass
class MLConfig:
    include: bool
    feature_type: Optional[str] = None
    encoding: Optional[str] = None
    importance_hint: Optional[str] = None
    derived_features: list = dc_field(default_factory=list)


@dataclass
class AccuracyConfig:
    weight: int
    category: str
    unlocks: Optional[str] = None


@dataclass
class FieldDefinition:
    id: str
    label: str
    type: str
    section_id: str
    survey_target: str
    storage: StorageConfig
    rag: RAGConfig
    persona: PersonaConfig
    ml: MLConfig
    accuracy: AccuracyConfig
    options: list
    validation: dict
    migration_alias: Optional[str] = None


@dataclass
class SectionDefinition:
    id: str
    label: str
    survey_target: str
    fields: list


class SurveySchema:

    def __init__(self, raw: dict):
        self.version = raw.get("version", "1.0")
        self.schema_id = raw.get("schema_id", "murmur_survey_v1")
        self._sections: list[SectionDefinition] = []
        self._by_id: dict[str, FieldDefinition] = {}
        self._by_target: dict[str, list] = {}

        for s in raw.get("sections", []):
            section = SectionDefinition(
                id=s.get("id") or s.get("section_id", "unknown"),
                label=s.get("label", s.get("id") or s.get("section_id", "Unknown")),
                survey_target=s.get("survey_target", "workspace"),
                fields=[],
            )
            target = s["survey_target"]

            for f in s.get("fields", []):
                ml_raw = f.get("ml", {})
                raw_derived = ml_raw.get("derived_features", [])
                derived = []
                for d in raw_derived:
                    if isinstance(d, dict):
                        derived.append(DerivedFeature(**d))
                    elif isinstance(d, str):
                        # Simple string format: just the feature id
                        derived.append(DerivedFeature(
                            id=d, label=d.replace("_", " ").title(),
                            compute=f"hofstede[{{value}}].{d.replace('hofstede_', '')}" if d.startswith("hofstede_") else d,
                            feature_type="numerical",
                        ))

                rag_raw = f.get("rag", {})
                persona_raw = f.get("persona", {})

                fd = FieldDefinition(
                    id=f["id"],
                    label=f["label"],
                    type=f["type"],
                    section_id=section.id,
                    survey_target=target,
                    migration_alias=f.get("migration_alias"),
                    storage=StorageConfig(**f.get("storage", {"strategy": "jsonb", "table": "businesses"})),
                    rag=RAGConfig(
                        include=rag_raw.get("include", False),
                        weight=rag_raw.get("weight", "low"),
                        section=rag_raw.get("section", "GENERAL"),
                        template=rag_raw.get("template", "{value}"),
                    ),
                    persona=PersonaConfig(
                        include=persona_raw.get("include", False),
                        weight=persona_raw.get("weight", "low"),
                        prompt_fragment=persona_raw.get("prompt_fragment", ""),
                        influence_description=persona_raw.get("influence_description", ""),
                    ),
                    ml=MLConfig(
                        include=ml_raw.get("include", False),
                        feature_type=ml_raw.get("feature_type"),
                        encoding=ml_raw.get("encoding"),
                        importance_hint=ml_raw.get("importance_hint"),
                        derived_features=derived,
                    ),
                    accuracy=AccuracyConfig(
                        **f.get("accuracy", {"weight": 0, "category": "bonus"})
                    ),
                    options=f.get("options", []),
                    validation=f.get("validation", {}),
                )

                section.fields.append(fd)
                self._by_id[fd.id] = fd
                if fd.migration_alias:
                    self._by_id[fd.migration_alias] = fd
                self._by_target.setdefault(target, []).append(fd)

            self._sections.append(section)

    def get_field(self, field_id: str) -> Optional[FieldDefinition]:
        return self._by_id.get(field_id)

    def fields_for_target(self, target: str) -> list[FieldDefinition]:
        return self._by_target.get(target, [])

    def fields_for_rag(self, target: str) -> list[FieldDefinition]:
        weight_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            [f for f in self.fields_for_target(target) if f.rag.include and f.rag.weight != "exclude"],
            key=lambda f: weight_order.get(f.rag.weight, 3),
        )

    def fields_for_persona(self, target: str) -> list[FieldDefinition]:
        return [f for f in self.fields_for_target(target) if f.persona.include]

    def fields_for_ml(self, target: str) -> list[FieldDefinition]:
        return [f for f in self.fields_for_target(target) if f.ml.include]

    def all_feature_ids(self, target: str) -> list[str]:
        ids = []
        for f in self.fields_for_ml(target):
            ids.append(f.id)
            for d in f.ml.derived_features:
                ids.append(d.id)
        return ids

    def total_accuracy_points(self, target: str) -> int:
        return sum(f.accuracy.weight for f in self.fields_for_target(target))

    def compute_accuracy_score(self, target: str, data: dict) -> dict:
        total = self.total_accuracy_points(target)
        earned = 0
        missing = []

        for f in self.fields_for_target(target):
            value = data.get(f.id) or data.get(f.migration_alias) if f.migration_alias else data.get(f.id)
            if value and value != [] and value != "":
                earned += f.accuracy.weight
            else:
                missing.append({
                    "field_id": f.id, "label": f.label,
                    "weight": f.accuracy.weight, "category": f.accuracy.category,
                    "unlocks": f.accuracy.unlocks,
                })

        missing.sort(key=lambda x: -x["weight"])
        percentage = round((earned / total) * 100) if total else 0

        return {
            "score": earned, "total": total, "percentage": percentage,
            "next_improvement": missing[0] if missing else None,
            "missing_fields": missing,
        }

    @property
    def sections(self) -> list[SectionDefinition]:
        return self._sections


_instance: Optional[SurveySchema] = None
_mtime: float = 0


def get_schema() -> SurveySchema:
    global _instance, _mtime
    is_dev = os.getenv("ENVIRONMENT", "dev") == "dev"

    if not SCHEMA_PATH.exists():
        return SurveySchema({"sections": []})

    current = SCHEMA_PATH.stat().st_mtime
    if _instance is None or (is_dev and current > _mtime):
        with open(SCHEMA_PATH) as f:
            raw = yaml.safe_load(f)
        _instance = SurveySchema(raw)
        _mtime = current

    return _instance


def validate_schema(raw: dict) -> list[str]:
    """Validates schema YAML structure. Returns list of errors (empty = valid)."""
    errors = []
    required_keys = ["id", "label", "type", "storage", "rag", "persona", "ml", "accuracy"]
    seen_ids = set()

    for section in raw.get("sections", []):
        if "id" not in section:
            errors.append("Section missing id")
        if "survey_target" not in section:
            errors.append(f"Section {section.get('id')} missing survey_target")

        for field in section.get("fields", []):
            for key in required_keys:
                if key not in field:
                    errors.append(f"Field {field.get('id', '?')} missing required key: {key}")

            fid = field.get("id", "")
            if fid in seen_ids:
                errors.append(f"Duplicate field id: {fid}")
            seen_ids.add(fid)

            if field.get("validation", {}).get("required", False):
                errors.append(f"Field {fid} has required=true. Nothing in Murmur is ever required.")

    return errors
