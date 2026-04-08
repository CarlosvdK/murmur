"""
RAGBuilder -- builds the workspace context document fed into every simulation.

Driven entirely by survey_schema.yaml. Adding a field to the schema with
rag.include=true automatically adds it to the RAG context.

Note: This only handles user-provided survey data. Context agents (Google
Places, news, weather etc.) still run separately and are appended by the
simulation orchestrator.
"""

from typing import Optional

from backend.survey.schema_loader import get_schema


def build_rag_context(workspace_data: dict, target: str = "workspace") -> str:
    """Builds the static portion of the simulation context from survey data.

    The simulation orchestrator appends live context from context agents.
    """
    schema = get_schema()
    fields = schema.fields_for_rag(target)

    # Group by RAG section
    sections: dict[str, list[str]] = {}
    for field in fields:
        value = _resolve_value(field, workspace_data)
        if not value:
            continue

        section = field.rag.section
        if section not in sections:
            sections[section] = []

        line = field.rag.template.format(
            value=value,
            label=_resolve_label(field, workspace_data),
        )
        sections[section].append(line)

    # Add Hofstede cultural profile if country known
    country = workspace_data.get("location_country")
    if country:
        try:
            from research.rag_library import get_country_profile
            profile = get_country_profile(country)
            if profile and profile.get("uncertainty_avoidance"):
                ua = profile["uncertainty_avoidance"]
                ind = profile["individualism"]
                pdi = profile["power_distance"]
                sections.setdefault("CULTURAL CONTEXT", []).extend([
                    f"Hofstede Uncertainty Avoidance: {ua}/100",
                    f"Hofstede Individualism: {ind}/100",
                    f"Hofstede Power Distance: {pdi}/100",
                    f"Cultural resistance to change: "
                    f"{'very high' if ua > 80 else 'high' if ua > 60 else 'moderate' if ua > 40 else 'low'}",
                    "(Source: Hofstede 2001; De Mooij & Hofstede 2010)",
                ])
        except ImportError:
            pass

    # Assemble document
    lines = ["WORKSPACE SURVEY CONTEXT", "=" * 40, f"Schema version: {schema.schema_id}", ""]
    for section_name, section_lines in sections.items():
        lines.append(f"\n{section_name}")
        lines.append("-" * len(section_name))
        lines.extend(section_lines)

    return "\n".join(lines)


def build_persona_context(workspace_data: dict, target: str = "workspace") -> str:
    """Builds the persona injection fragment from user survey data.

    Only includes fields marked persona.include=true, sorted by weight.
    """
    schema = get_schema()
    fields = schema.fields_for_persona(target)
    weight_order = {"high": 0, "medium": 1, "low": 2}

    fragments = []
    for field in sorted(fields, key=lambda f: weight_order.get(f.persona.weight, 3)):
        value = _resolve_value(field, workspace_data)
        if not value:
            continue
        fragment = field.persona.prompt_fragment.format(
            value=value,
            label=_resolve_label(field, workspace_data),
        )
        fragments.append(fragment.strip())

    return "\n".join(fragments)


def _resolve_value(field, data: dict) -> Optional[str]:
    value = data.get(field.id)
    if value is None and field.migration_alias:
        value = data.get(field.migration_alias)
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else None
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, dict):
        return str(value)
    return str(value) if value else None


def _resolve_label(field, data: dict) -> str:
    value = _resolve_value(field, data)
    if not value or not field.options:
        return value or ""
    for option in field.options:
        if "items" in option:
            for item in option["items"]:
                if item.get("value") == value:
                    return item.get("label", value)
        elif option.get("value") == value:
            return option.get("label", value)
    return value
