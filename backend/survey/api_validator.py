"""
APIValidator -- validates incoming survey payloads against the schema.

Nothing is required -- validation only checks format/type when present.
"""

from backend.survey.schema_loader import get_schema


def validate_survey_payload(data: dict, target: str, section_id: str = None) -> tuple[bool, list[str]]:
    schema = get_schema()
    errors = []

    fields = schema.fields_for_target(target)
    if section_id:
        fields = [f for f in fields if f.section_id == section_id]

    for field in fields:
        value = data.get(field.id)
        if value is None:
            continue

        v = field.validation

        if field.type in ("text", "textarea"):
            if v.get("max_length") and len(str(value)) > v["max_length"]:
                errors.append(f"{field.label}: maximum {v['max_length']} characters")

        if field.type == "number":
            try:
                num = float(value)
                if v.get("min_value") is not None and num < v["min_value"]:
                    errors.append(f"{field.label}: minimum value is {v['min_value']}")
                if v.get("max_value") is not None and num > v["max_value"]:
                    errors.append(f"{field.label}: maximum value is {v['max_value']}")
            except (TypeError, ValueError):
                errors.append(f"{field.label}: must be a number")

        if field.type == "select" and value is not None:
            valid = _extract_option_values(field)
            if valid and value not in valid:
                errors.append(f"{field.label}: '{value}' is not a valid option")

        if field.type in ("chips", "multi_select"):
            if not isinstance(value, list):
                errors.append(f"{field.label}: must be a list")
            else:
                valid = _extract_option_values(field)
                if valid:
                    invalid = [v for v in value if v not in valid]
                    if invalid:
                        errors.append(f"{field.label}: invalid values: {', '.join(invalid)}")

        if field.type == "url" and value:
            if not str(value).startswith(("http://", "https://")):
                errors.append(f"{field.label}: must be a valid URL")

    return len(errors) == 0, errors


def _extract_option_values(field) -> list:
    values = []
    for opt in field.options:
        if "items" in opt:
            values.extend(i["value"] for i in opt["items"])
        elif "value" in opt:
            values.append(opt["value"])
    return values
