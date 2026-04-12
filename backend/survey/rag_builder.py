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

    # Add new market and competition context (not yet in schema)
    if workspace_data.get("business_not_role"):
        val = workspace_data["business_not_role"]
        if isinstance(val, list):
            sections.setdefault("CUSTOMER PROFILE", []).append(
                f"Business is explicitly NOT: {', '.join(val)}. Personas should not be motivated by these reasons."
            )

    if workspace_data.get("is_online_only"):
        sections.setdefault("BUSINESS IDENTITY", []).append(
            "This is an online-only business with no physical location."
        )

    if workspace_data.get("customer_discovery"):
        val = workspace_data["customer_discovery"]
        if isinstance(val, list) and val:
            sections.setdefault("MARKET CONTEXT", []).append(
                f"Customer discovery channels: {', '.join(val)}"
            )

    if workspace_data.get("nearby_anchors"):
        val = workspace_data["nearby_anchors"]
        if isinstance(val, list) and val:
            label = "Traffic drivers" if workspace_data.get("is_online_only") else "Nearby traffic drivers"
            sections.setdefault("MARKET CONTEXT", []).append(
                f"{label}: {', '.join(val)}"
            )

    if workspace_data.get("competitor_advantage"):
        val = workspace_data["competitor_advantage"]
        if isinstance(val, list) and val:
            sections.setdefault("MARKET CONTEXT", []).append(
                f"Competitor advantages (what they do better): {', '.join(val)}. "
                "Personas should be aware of these alternatives and may reference them."
            )

    if workspace_data.get("location_advantage"):
        sections.setdefault("MARKET CONTEXT", []).append(
            f"Location/market position: {workspace_data['location_advantage']}"
        )

    if workspace_data.get("prior_changes"):
        val = workspace_data["prior_changes"]
        if isinstance(val, list) and val:
            change_lines = []
            for ch in val:
                if isinstance(ch, dict) and ch.get("change"):
                    parts = [f"Change: {ch['change']}"]
                    if ch.get("year"):
                        parts.append(f"(in {ch['year']})")
                    if ch.get("outcome"):
                        parts.append(f"-- Outcome: {ch['outcome']}")
                    if ch.get("metrics"):
                        parts.append(f"-- Metrics: {ch['metrics']}")
                    change_lines.append(" ".join(parts))
            if change_lines:
                sections.setdefault("CHANGE HISTORY", []).append(
                    "REAL PAST CHANGES (use these to calibrate predictions -- "
                    "real outcomes from this business are more valuable than general research):"
                )
                sections["CHANGE HISTORY"].extend(change_lines)

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
