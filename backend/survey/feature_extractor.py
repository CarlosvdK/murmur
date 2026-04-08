"""
FeatureExtractor -- converts survey data into ML features.

Driven by survey_schema.yaml. Adding ml.include=true to a field
automatically adds it as a feature.
"""

from typing import Any, Optional

from backend.survey.schema_loader import get_schema, FieldDefinition


class FeatureExtractor:

    def __init__(self, target: str = "workspace"):
        self.schema = get_schema()
        self.target = target
        self._ml_fields = self.schema.fields_for_ml(target)
        self._feature_names = self._build_feature_names()

    def _build_feature_names(self) -> list[str]:
        names = []
        for field in self._ml_fields:
            if field.ml.encoding == "onehot":
                for opt in self._flat_options(field):
                    names.append(f"{field.id}__{opt}")
            else:
                names.append(field.id)
            for derived in field.ml.derived_features:
                names.append(derived.id)
        return names

    def extract(self, data: dict) -> dict[str, float]:
        features: dict[str, float] = {}

        for field in self._ml_fields:
            value = data.get(field.id)
            if value is None and field.migration_alias:
                value = data.get(field.migration_alias)

            if field.ml.encoding == "onehot":
                for opt in self._flat_options(field):
                    feat_name = f"{field.id}__{opt}"
                    if isinstance(value, list):
                        features[feat_name] = 1.0 if opt in value else 0.0
                    else:
                        features[feat_name] = 1.0 if value == opt else 0.0

            elif field.ml.feature_type == "numerical":
                features[field.id] = float(value) if value is not None else 0.0

            elif field.ml.feature_type == "binary":
                features[field.id] = 1.0 if value in [True, "Yes", "yes", 1] else 0.0

            elif field.ml.feature_type == "ordinal":
                features[field.id] = self._encode_ordinal(field, value)

            for derived in field.ml.derived_features:
                features[derived.id] = self._compute_derived(derived, value)

        return features

    @property
    def feature_names(self) -> list[str]:
        return self._feature_names

    def _flat_options(self, field: FieldDefinition) -> list[str]:
        values = []
        for opt in field.options:
            if "items" in opt:
                values.extend(i["value"] for i in opt["items"])
            elif "value" in opt:
                values.append(opt["value"])
        return values

    def _compute_derived(self, derived, source_value: Any) -> float:
        compute = derived.compute
        if "hofstede[{value}]" in compute:
            country = str(source_value) if source_value else ""
            try:
                from research.rag_library import get_country_profile
                profile = get_country_profile(country)
                if profile:
                    key = compute.split(".")[-1]
                    return float(profile.get(key, 50))
            except ImportError:
                pass
            return 50.0
        return 0.0

    def _encode_ordinal(self, field: FieldDefinition, value: Any) -> float:
        opts = self._flat_options(field)
        if not opts or value not in opts:
            return 0.5
        idx = opts.index(value)
        return idx / (len(opts) - 1) if len(opts) > 1 else 0.5
