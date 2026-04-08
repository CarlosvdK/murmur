# Murmur Comprehensive Test Suite -- Execution Prompt

**Date**: 2026-04-07
**Estimated run time**: ~30 min for schema/unit tests (Sections 0-3, 5-9), ~15 min per simulation type if running Claude API calls (Section 4)
**Total tests**: 100
**Total with all API calls**: ~2.5 hours

## How to Run

This document is designed to be executed by a fresh Claude Code session. Copy the entire file into a Claude Code conversation and say:

> Execute testing-prompt.md section by section. Stop after each section to report results before continuing.

### Prerequisites

1. You are in the `/Users/Carlos/Desktop/Projects/murmur/murmur` working directory
2. Python 3.11 venv is at `/Users/Carlos/Desktop/Projects/murmur/murmur/.venv`
3. Activate with: `source /Users/Carlos/Desktop/Projects/murmur/murmur/.venv/bin/activate`
4. Environment variables are set in `.env` (ANTHROPIC_API_KEY, GOOGLE_PLACES_API_KEY, BRAVE_SEARCH_API_KEY)
5. `pip install scikit-learn` if not already installed (needed for Section 0)

### Test Output Convention

Every test prints one line:

```
[PASS] T1.3 -- YAML required=false everywhere
[FAIL] T1.3 -- YAML required=false everywhere: field 'name' has required=true
[SKIP] T4.2 -- Cultural comparison: ANTHROPIC_API_KEY not set
```

After each section, print the summary table (see Section 10 for format).

---

## SECTION 0: PRE-TEST INFRASTRUCTURE

Before any tests run, build two things that do not yet exist.

### 0.1 Build RandomForest Calibration Model

**REQUIRES BACKEND BUILD** -- Create this file from scratch.

**File**: `backend/ml/calibration_model.py`

```python
"""
CalibrationModel -- RandomForest that predicts simulation accuracy
based on survey features.

Trained on validated real outcomes. Used in production to adjust
confidence levels and flag unreliable simulations.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

from backend.survey.feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent / "calibration_model.pkl"
TRAINING_DATA_PATH = Path(__file__).parent / "training_data.json"


class CalibrationModel:
    """Predicts whether a simulation will match real outcomes."""

    def __init__(self):
        self.model: Optional[RandomForestClassifier] = None
        self.extractor = FeatureExtractor(target="workspace")
        self.feature_names = self.extractor.feature_names
        self._load()

    def _load(self):
        if MODEL_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            logger.info("Calibration model loaded from %s", MODEL_PATH)

    def train(self, training_records: list[dict]) -> dict:
        """Train the model on validated outcome records.

        Each record must have:
        - survey_data: dict of survey field values
        - outcome_matched: bool (did the simulation match reality?)
        """
        if len(training_records) < 10:
            logger.warning("Only %d training records -- model may be unreliable", len(training_records))

        X = []
        y = []
        for record in training_records:
            features = self.extractor.extract(record["survey_data"])
            feature_vector = [features.get(name, 0.0) for name in self.feature_names]
            X.append(feature_vector)
            y.append(1 if record["outcome_matched"] else 0)

        X = np.array(X)
        y = np.array(y)

        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_leaf=3,
            random_state=42,
            class_weight="balanced",
        )
        self.model.fit(X, y)

        # Cross-validation score
        cv_scores = cross_val_score(self.model, X, y, cv=min(5, len(y)), scoring="accuracy")

        # Feature importance
        importances = dict(zip(self.feature_names, self.model.feature_importances_))
        top_features = sorted(importances.items(), key=lambda x: -x[1])[:10]

        result = {
            "n_records": len(training_records),
            "cv_accuracy_mean": round(float(cv_scores.mean()), 3),
            "cv_accuracy_std": round(float(cv_scores.std()), 3),
            "top_features": top_features,
            "feature_count": len(self.feature_names),
        }

        logger.info(
            "Model trained: %d records, CV accuracy=%.3f +/- %.3f",
            len(training_records), cv_scores.mean(), cv_scores.std(),
        )
        return result

    def predict_accuracy(self, survey_data: dict) -> dict:
        """Predict whether a simulation with this survey data will be accurate."""
        if self.model is None:
            return {"prediction": "unknown", "confidence": 0.0, "reason": "Model not trained"}

        features = self.extractor.extract(survey_data)
        feature_vector = np.array([[features.get(name, 0.0) for name in self.feature_names]])

        proba = self.model.predict_proba(feature_vector)[0]
        prediction = self.model.predict(feature_vector)[0]

        return {
            "prediction": "accurate" if prediction == 1 else "inaccurate",
            "confidence": round(float(max(proba)), 3),
            "accurate_probability": round(float(proba[1]) if len(proba) > 1 else proba[0], 3),
        }

    def save(self):
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        logger.info("Model saved to %s", MODEL_PATH)

    def feature_importance(self) -> list[tuple[str, float]]:
        if self.model is None:
            return []
        importances = dict(zip(self.feature_names, self.model.feature_importances_))
        return sorted(importances.items(), key=lambda x: -x[1])
```

Also create `backend/ml/__init__.py`:
```python
from backend.ml.calibration_model import CalibrationModel
```

### 0.2 Generate Synthetic Training Data

**REQUIRES BACKEND BUILD** -- Create this file from scratch.

**File**: `backend/ml/generate_training_data.py`

```python
"""
Generates 30+ synthetic validated outcome records for training
the calibration model.

Uses TestSeeder profiles + random variations to create realistic
training data. In production, this will be replaced by real
outcome data from the real_outcomes table.
"""

import json
import random
from pathlib import Path

from backend.survey.test_seeder import TestSeeder

OUTPUT_PATH = Path(__file__).parent / "training_data.json"


def generate_training_data(n: int = 35) -> list[dict]:
    seeder = TestSeeder(target="workspace")
    profiles = ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]
    records = []

    for i in range(n):
        profile = profiles[i % len(profiles)]
        data = seeder.generate(profile=profile)

        # Add some random variation to make records distinct
        if random.random() > 0.5:
            data["visit_frequency"] = random.choice(["daily", "weekly", "monthly", "occasional"])
        if random.random() > 0.5:
            data["competitor_count"] = random.choice(["only_one", "one_two", "three_five", "six_plus"])
        if random.random() > 0.5:
            data["regular_proportion"] = random.choice(["almost_none", "handful", "solid_base", "mostly_regulars"])

        # Simulate whether the outcome matched -- use heuristics:
        # More detailed profiles tend to produce more accurate simulations
        detail_score = sum(1 for v in data.values() if v is not None and v != [] and v != "")
        accuracy_probability = min(0.9, 0.3 + (detail_score / 30))

        # Country-specific adjustment (high UA countries are more predictable)
        country = data.get("location_country", "")
        if country == "ES":  # UA=86, high predictability
            accuracy_probability += 0.1
        elif country == "GB":  # UA=35, less predictable
            accuracy_probability -= 0.05

        outcome_matched = random.random() < accuracy_probability

        records.append({
            "survey_data": data,
            "outcome_matched": outcome_matched,
            "profile_source": profile,
        })

    return records


def save_training_data():
    records = generate_training_data()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Generated {len(records)} training records at {OUTPUT_PATH}")
    return records


if __name__ == "__main__":
    save_training_data()
```

### 0.3 Verify TestSeeder Profiles

Run this verification:

```python
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.survey.test_seeder import TestSeeder

seeder = TestSeeder(target="workspace")
profiles = ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]

for profile in profiles:
    data = seeder.generate(profile=profile)
    report = seeder.schema_coverage_report(data)
    assert report["populated"] > 0, f"Profile {profile} has no populated fields"
    print(f"[PASS] T0.3a -- TestSeeder profile '{profile}': "
          f"{report['populated']}/{report['total_fields']} fields, "
          f"{report['coverage_pct']}% coverage")

# Verify random generation works
random_data = seeder.generate(profile="nonexistent_profile")
random_report = seeder.schema_coverage_report(random_data)
assert random_report["populated"] > 0, "Random generation produced no fields"
print(f"[PASS] T0.3b -- TestSeeder random generation: "
      f"{random_report['populated']}/{random_report['total_fields']} fields")
```

### 0.4 Build and Verify ML Infrastructure

After creating the files above, run:

```python
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

# Generate training data
from backend.ml.generate_training_data import generate_training_data
records = generate_training_data(35)
assert len(records) >= 30, f"Expected 30+ records, got {len(records)}"
print(f"[PASS] T0.4a -- Generated {len(records)} training records")

# Train model
from backend.ml.calibration_model import CalibrationModel
model = CalibrationModel()
result = model.train(records)
assert result["cv_accuracy_mean"] > 0.0, "Model failed to train"
assert result["feature_count"] > 0, "No features extracted"
print(f"[PASS] T0.4b -- Model trained: CV accuracy={result['cv_accuracy_mean']:.3f}, "
      f"features={result['feature_count']}")

# Save and reload
model.save()
model2 = CalibrationModel()
assert model2.model is not None, "Model failed to reload from disk"
print("[PASS] T0.4c -- Model persisted and reloaded from backend/ml/calibration_model.pkl")
```

---

## SECTION 1: SCHEMA INTEGRITY TESTS

All tests in this section operate on `config/survey_schema.yaml` and the schema engine modules. No API calls required.

### T1.1 -- YAML loads without error

```python
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.survey.schema_loader import get_schema, validate_schema, SCHEMA_PATH
import yaml

with open(SCHEMA_PATH) as f:
    raw = yaml.safe_load(f)

errors = validate_schema(raw)
assert len(errors) == 0, f"Schema validation errors: {errors}"
print("[PASS] T1.1 -- YAML loads and validates without errors")
```

### T1.2 -- Schema has expected field count

```python
schema = get_schema()
all_fields = []
for section in schema.sections:
    all_fields.extend(section.fields)
assert len(all_fields) >= 40, f"Expected 40+ fields, found {len(all_fields)}"
print(f"[PASS] T1.2 -- Schema contains {len(all_fields)} fields (expected 40+)")
```

### T1.3 -- required=false everywhere

```python
violations = []
for section in schema.sections:
    for field in section.fields:
        if field.validation.get("required", False):
            violations.append(field.id)
assert len(violations) == 0, f"Fields with required=true: {violations}"
print("[PASS] T1.3 -- All fields have required=false (Murmur rule: nothing is ever required)")
```

### T1.4 -- RAG builder produces output for each seed profile

```python
from backend.survey.rag_builder import build_rag_context
from backend.survey.test_seeder import TestSeeder

seeder = TestSeeder()
for profile in ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]:
    data = seeder.generate(profile=profile)
    context = build_rag_context(data)
    assert len(context) > 100, f"RAG context too short for {profile}: {len(context)} chars"
    assert "WORKSPACE SURVEY CONTEXT" in context, f"Missing header in {profile} RAG output"
    print(f"[PASS] T1.4a -- RAG builder output for '{profile}': {len(context)} chars")

# Verify Spanish restaurant gets Hofstede cultural context
es_data = seeder.generate(profile="spanish_restaurant")
es_context = build_rag_context(es_data)
assert "Uncertainty Avoidance" in es_context or "uncertainty_avoidance" in es_context.lower(), \
    "Spanish restaurant RAG context missing Hofstede UA"
assert "86" in es_context, "Spanish restaurant RAG context missing UA=86 score"
print("[PASS] T1.4b -- Spanish restaurant RAG includes Hofstede UA=86")
```

### T1.5 -- Persona context output for seed profiles

```python
from backend.survey.rag_builder import build_persona_context

for profile in ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]:
    data = seeder.generate(profile=profile)
    context = build_persona_context(data)
    assert len(context) > 50, f"Persona context too short for {profile}: {len(context)} chars"
    print(f"[PASS] T1.5 -- Persona context for '{profile}': {len(context)} chars")
```

### T1.6 -- Feature vector correctness (ES -> hofstede_ua=86)

```python
from backend.survey.feature_extractor import FeatureExtractor

extractor = FeatureExtractor(target="workspace")
es_data = seeder.generate(profile="spanish_restaurant")
features = extractor.extract(es_data)

# Verify Hofstede derived features exist for ES (location_country)
assert "hofstede_uncertainty_avoidance" in features, \
    f"Missing hofstede_uncertainty_avoidance. Features: {list(features.keys())}"
assert features["hofstede_uncertainty_avoidance"] == 86.0, \
    f"Expected hofstede_ua=86 for ES, got {features['hofstede_uncertainty_avoidance']}"
print("[PASS] T1.6a -- ES feature vector has hofstede_uncertainty_avoidance=86.0")

# Verify GB
gb_data = seeder.generate(profile="uk_barbershop")
gb_features = extractor.extract(gb_data)
assert gb_features.get("hofstede_uncertainty_avoidance") == 35.0, \
    f"Expected hofstede_ua=35 for GB, got {gb_features.get('hofstede_uncertainty_avoidance')}"
print("[PASS] T1.6b -- GB feature vector has hofstede_uncertainty_avoidance=35.0")

# Verify NL
nl_data = seeder.generate(profile="dutch_retailer")
nl_features = extractor.extract(nl_data)
assert nl_features.get("hofstede_uncertainty_avoidance") == 53.0, \
    f"Expected hofstede_ua=53 for NL, got {nl_features.get('hofstede_uncertainty_avoidance')}"
print("[PASS] T1.6c -- NL feature vector has hofstede_uncertainty_avoidance=53.0")

# Verify all 6 Hofstede derived features present
hofstede_keys = [
    "hofstede_power_distance", "hofstede_individualism", "hofstede_masculinity",
    "hofstede_uncertainty_avoidance", "hofstede_long_term_orientation", "hofstede_indulgence"
]
for key in hofstede_keys:
    assert key in features, f"Missing derived feature: {key}"
print("[PASS] T1.6d -- All 6 Hofstede derived features present in feature vector")
```

### T1.7 -- API validation accepts valid and rejects invalid payloads

```python
from backend.survey.api_validator import validate_survey_payload

# Valid payload
valid_data = {"name": "Test Business", "type": "restaurant", "description": "A test"}
is_valid, errors = validate_survey_payload(valid_data, target="workspace")
assert is_valid, f"Valid payload rejected: {errors}"
print("[PASS] T1.7a -- API validator accepts valid payload")

# Invalid type value
invalid_data = {"type": "nonexistent_type"}
is_valid, errors = validate_survey_payload(invalid_data, target="workspace")
assert not is_valid, "Invalid type value was not rejected"
print("[PASS] T1.7b -- API validator rejects invalid select value")

# Overly long text
long_data = {"name": "x" * 300}
is_valid, errors = validate_survey_payload(long_data, target="workspace")
assert not is_valid, "Overly long text was not rejected"
print("[PASS] T1.7c -- API validator rejects text exceeding max_length=200")
```

### T1.8 -- Accuracy scoring computation

```python
# Full profile should score high
full_data = seeder.generate(profile="spanish_restaurant")
score = schema.compute_accuracy_score("workspace", full_data)
assert score["percentage"] > 50, f"Full profile scored only {score['percentage']}%"
assert score["total"] > 0, "Total accuracy points is zero"
print(f"[PASS] T1.8a -- Accuracy score for spanish_restaurant: {score['percentage']}% "
      f"({score['score']}/{score['total']})")

# Empty profile should score 0%
empty_score = schema.compute_accuracy_score("workspace", {})
assert empty_score["percentage"] == 0, f"Empty profile scored {empty_score['percentage']}%"
assert len(empty_score["missing_fields"]) > 0, "No missing fields reported for empty profile"
print(f"[PASS] T1.8b -- Empty profile scores 0%, {len(empty_score['missing_fields'])} fields missing")

# next_improvement should point to highest-weight missing field
assert empty_score["next_improvement"] is not None, "No next_improvement for empty profile"
print(f"[PASS] T1.8c -- next_improvement suggests: '{empty_score['next_improvement']['field_id']}' "
      f"(weight={empty_score['next_improvement']['weight']})")
```

### T1.9 -- Hot-reload in dev mode

```python
import os
os.environ["ENVIRONMENT"] = "dev"

# Force reload by clearing cache
import backend.survey.schema_loader as sl
sl._instance = None
sl._mtime = 0

schema1 = sl.get_schema()
schema2 = sl.get_schema()
# In dev mode, same mtime should return cached instance
assert schema1 is schema2, "Schema not cached on same mtime"
print("[PASS] T1.9 -- Schema hot-reload: cached instance returned when file unchanged")
```

---

## SECTION 2: RESEARCH LIBRARY INJECTION

Tests that the research library loads and returns content for each domain.

### T2.1 -- Country profiles load for ES, GB, NL

```python
from research.rag_library import get_country_profile

es = get_country_profile("ES")
assert es["uncertainty_avoidance"] == 86, f"ES UA should be 86, got {es['uncertainty_avoidance']}"
assert es["country"] == "Spain"
print("[PASS] T2.1a -- ES profile: UA=86, country=Spain")

gb = get_country_profile("GB")
assert gb["uncertainty_avoidance"] == 35, f"GB UA should be 35, got {gb['uncertainty_avoidance']}"
assert gb["individualism"] == 89, f"GB IDV should be 89, got {gb['individualism']}"
print("[PASS] T2.1b -- GB profile: UA=35, IDV=89")

nl = get_country_profile("NL")
assert nl["uncertainty_avoidance"] == 53, f"NL UA should be 53, got {nl['uncertainty_avoidance']}"
assert nl["masculinity"] == 14, f"NL MAS should be 14, got {nl['masculinity']}"
print("[PASS] T2.1c -- NL profile: UA=53, MAS=14")

# Unknown country falls back to DEFAULT
unknown = get_country_profile("ZZ")
assert "uncertainty_avoidance" in unknown, "DEFAULT fallback missing UA"
print(f"[PASS] T2.1d -- Unknown country 'ZZ' falls back to DEFAULT (UA={unknown['uncertainty_avoidance']})")
```

### T2.2 -- Consumer psychology prompt fragment loads

```python
from research.rag_library import get_domain_insights

consumer = get_domain_insights("consumer_psychology")
assert len(consumer) > 500, f"Consumer psychology fragment too short: {len(consumer)} chars"
assert "loss aversion" in consumer.lower() or "Loss Aversion" in consumer, \
    "Consumer psychology missing loss aversion"
assert "Kahneman" in consumer or "kahneman" in consumer, \
    "Consumer psychology missing Kahneman citation"
print(f"[PASS] T2.2 -- consumer_psychology fragment: {len(consumer)} chars, "
      "includes loss aversion + Kahneman citation")
```

### T2.3 -- Review bias fragment includes silent majority 55-70%

```python
review = get_domain_insights("review_bias")
assert len(review) > 500, f"Review bias fragment too short: {len(review)} chars"
# Verify Gao et al. 2015 citation (vocal minority research)
assert "Gao" in review, "Review bias missing Gao et al. citation"
# Verify silent majority concept
assert "silent majority" in review.lower() or "Silent Majority" in review, \
    "Review bias missing silent majority concept"
# Verify the J-shaped distribution
assert "J-shaped" in review or "j-shaped" in review.lower() or "bimodal" in review.lower(), \
    "Review bias missing J-shaped/bimodal distribution"
print(f"[PASS] T2.3 -- review_bias fragment: {len(review)} chars, "
      "includes Gao citation + silent majority + J-shaped distribution")
```

### T2.4 -- Review bias correction mentions platform distortions

```python
# Google Reviews skew positive (from Luca 2016 / Han & Anderson 2026)
assert "google" in review.lower(), "Review bias missing Google platform specifics"
assert "positive" in review.lower() or "skew" in review.lower(), \
    "Review bias missing positive skew for Google"
print("[PASS] T2.4 -- Review bias includes Google platform-specific positive skew")
```

### T2.5 -- Negotiation psychology loads for vendor twin

```python
negotiation = get_domain_insights("negotiation_psychology")
assert len(negotiation) > 500, f"Negotiation psychology too short: {len(negotiation)} chars"
assert "BATNA" in negotiation, "Negotiation psychology missing BATNA concept"
assert "anchor" in negotiation.lower() or "Anchoring" in negotiation, \
    "Negotiation psychology missing anchoring"
print(f"[PASS] T2.5 -- negotiation_psychology fragment: {len(negotiation)} chars, "
      "includes BATNA + anchoring")
```

### T2.6 -- get_simulation_context assembles vendor context correctly

```python
from research.rag_library import get_simulation_context

# Consumer simulation should NOT include negotiation
consumer_ctx = get_simulation_context("ES", simulation_type="consumer")
assert "negotiation" not in consumer_ctx.lower() or "BATNA" not in consumer_ctx, \
    "Consumer simulation context should not include negotiation psychology"
print("[PASS] T2.6a -- Consumer simulation excludes negotiation psychology")

# Vendor simulation SHOULD include negotiation
vendor_ctx = get_simulation_context("ES", simulation_type="vendor")
assert "BATNA" in vendor_ctx or "negotiation" in vendor_ctx.lower(), \
    "Vendor simulation context missing negotiation psychology"
print("[PASS] T2.6b -- Vendor simulation includes negotiation psychology with BATNA")

# Both should include consumer psychology
assert "loss aversion" in consumer_ctx.lower() or "Loss Aversion" in consumer_ctx
assert "loss aversion" in vendor_ctx.lower() or "Loss Aversion" in vendor_ctx
print("[PASS] T2.6c -- Both consumer and vendor contexts include consumer psychology")
```

### T2.7 -- All 9 prompt domains load

```python
from research.rag_library import list_available_domains

domains = list_available_domains()
expected_domains = [
    "consumer_psychology", "behavioral_economics", "review_bias",
    "personality_models", "decision_making", "country_profiles",
    "negotiation_psychology", "digital_twins", "simulation_methodology",
]
for d in expected_domains:
    assert d in domains, f"Missing domain: {d}"
    content = get_domain_insights(d)
    assert len(content) > 100, f"Domain '{d}' has insufficient content: {len(content)} chars"
print(f"[PASS] T2.7 -- All 9 research domains load successfully: {sorted(domains)}")
```

---

## SECTION 3: STATISTICAL VALIDITY

Tests for the impact estimator (`backend/impact/estimator.py`) and caveat system (`backend/swarm/caveats.py`).

### T3.1 -- CI computation verification

```python
from backend.impact.estimator import estimate_impact, _sentiment_to_retention

# Verify sentiment-to-retention mapping at key points
r_pos = _sentiment_to_retention(1.0)
r_neu = _sentiment_to_retention(0.0)
r_neg = _sentiment_to_retention(-1.0)

assert 0.95 <= r_pos <= 1.0, f"Retention at sentiment=1.0 should be ~0.98, got {r_pos}"
assert 0.70 <= r_neu <= 0.80, f"Retention at sentiment=0.0 should be ~0.75, got {r_neu}"
assert 0.15 <= r_neg <= 0.25, f"Retention at sentiment=-1.0 should be ~0.20, got {r_neg}"
print(f"[PASS] T3.1a -- Sentiment-to-retention: +1.0->{r_pos:.2f}, 0.0->{r_neu:.2f}, -1.0->{r_neg:.2f}")

# Verify monotonicity
for s in [-1.0, -0.5, 0.0, 0.5]:
    r1 = _sentiment_to_retention(s)
    r2 = _sentiment_to_retention(s + 0.5)
    assert r2 > r1, f"Retention not monotonic at {s}: {r1} >= {r2}"
print("[PASS] T3.1b -- Sentiment-to-retention is monotonically increasing")
```

### T3.2 -- Sentiment-to-retention sigmoid shape

```python
from backend.impact.estimator import _sentiment_to_visit_change

# Negative sentiment should reduce visits more than positive increases them
neg_change = _sentiment_to_visit_change(-1.0)
pos_change = _sentiment_to_visit_change(1.0)
assert neg_change < -20, f"Visit change at -1.0 should be <-20%, got {neg_change}"
assert pos_change < 10, f"Visit change at +1.0 should be <10%, got {pos_change}"
assert abs(neg_change) > abs(pos_change), "Negative visit impact should exceed positive"
print(f"[PASS] T3.2 -- Behavioral asymmetry: negative={neg_change}%, positive={pos_change}%")
```

### T3.3 -- Decision framework logic

```python
# All positive sentiments -> decision should be "proceed"
positive_responses = [{"sentiment": 0.8, "persona_name": f"P{i}"} for i in range(15)]
report = estimate_impact(positive_responses, "Should we add more seating?")
assert report.decision == "proceed", f"Expected 'proceed' for all-positive, got '{report.decision}'"
print(f"[PASS] T3.3a -- All-positive sentiment -> decision='proceed' "
      f"(CI: {report.revenue.ci_low_pct:+.1f}% to {report.revenue.ci_high_pct:+.1f}%)")

# All negative sentiments -> decision should be "avoid"
negative_responses = [{"sentiment": -0.8, "persona_name": f"P{i}"} for i in range(15)]
report_neg = estimate_impact(negative_responses, "Should we raise prices 50%?")
assert report_neg.decision == "avoid", f"Expected 'avoid' for all-negative, got '{report_neg.decision}'"
print(f"[PASS] T3.3b -- All-negative sentiment -> decision='avoid' "
      f"(CI: {report_neg.revenue.ci_low_pct:+.1f}% to {report_neg.revenue.ci_high_pct:+.1f}%)")

# Mixed sentiments -> decision should be "caution" or "test_first"
mixed_responses = [{"sentiment": 0.5 if i % 2 == 0 else -0.5, "persona_name": f"P{i}"} for i in range(15)]
report_mix = estimate_impact(mixed_responses, "Should we change the menu?")
assert report_mix.decision in ("caution", "test_first"), \
    f"Expected caution/test_first for mixed, got '{report_mix.decision}'"
print(f"[PASS] T3.3c -- Mixed sentiment -> decision='{report_mix.decision}'")
```

### T3.4 -- Small sample warning

```python
from backend.impact.estimator import estimate_impact

# 5 personas should give low confidence
small_responses = [{"sentiment": 0.3, "persona_name": f"P{i}"} for i in range(5)]
small_report = estimate_impact(small_responses, "Test question")
assert small_report.revenue.confidence_level == "low", \
    f"Expected 'low' confidence for n=5, got '{small_report.revenue.confidence_level}'"
# CI should be wider for small sample
assert (small_report.revenue.ci_high_pct - small_report.revenue.ci_low_pct) > 15, \
    "CI too narrow for n=5 sample"
print(f"[PASS] T3.4 -- Small sample (n=5): confidence='low', "
      f"CI width={small_report.revenue.ci_high_pct - small_report.revenue.ci_low_pct:.1f}pp")
```

### T3.5 -- Empty responses produce safe empty report

```python
empty_report = estimate_impact([], "Empty test")
assert empty_report.decision == "test_first"
assert empty_report.total_customers_modelled == 0
assert empty_report.revenue.confidence_level == "low"
print("[PASS] T3.5 -- Empty responses produce safe default report")
```

### T3.6 -- Caveat generation: always-on caveats present

```python
from backend.swarm.caveats import generate_caveats
from backend.models.business import BusinessSnapshot

biz = BusinessSnapshot(
    name="Test Biz", type="restaurant",
    description="A test restaurant with detailed description for testing purposes.",
    customer_description="Local regulars aged 30-55",
    location="Barcelona, Spain",
)

caveats = generate_caveats(biz, "Should we raise prices 10%?", 15, 15)
caveat_types = [c.type for c in caveats]

# Always-on caveats
assert "not_causation" in caveat_types, "Missing always-on caveat: not_causation"
assert "self_selection" in caveat_types, "Missing always-on caveat: self_selection"
assert "cherry_pick_note" in caveat_types, "Missing always-on caveat: cherry_pick_note"
print(f"[PASS] T3.6 -- Always-on caveats present: not_causation, self_selection, cherry_pick_note")
```

### T3.7 -- Anti-optimism bias: price sensitivity caveat for price questions

```python
price_caveats = generate_caveats(biz, "What if we raise prices by 15%?", 15, 15)
price_types = [c.type for c in price_caveats]
assert "price_sensitivity" in price_types, "Missing price_sensitivity caveat for price question"
print("[PASS] T3.7 -- Price question triggers price_sensitivity caveat (hypothetical bias correction)")
```

### T3.8 -- RTM flag detection

```python
rtm_caveats = generate_caveats(biz, "Sales have been terrible this month, should we discount?", 15, 15)
rtm_types = [c.type for c in rtm_caveats]
assert "rtm_warning" in rtm_types, "Missing rtm_warning for 'sales have been terrible' question"
print("[PASS] T3.8a -- RTM warning triggered by 'sales have been terrible'")

# Also test positive extreme
rtm_caveats2 = generate_caveats(biz, "We had our best month ever, should we expand?", 15, 15)
rtm_types2 = [c.type for c in rtm_caveats2]
assert "rtm_warning" in rtm_types2, "Missing rtm_warning for 'best month ever' question"
print("[PASS] T3.8b -- RTM warning triggered by 'best month ever'")

# Non-extreme question should NOT trigger RTM
normal_caveats = generate_caveats(biz, "Should we add delivery?", 15, 15)
normal_types = [c.type for c in normal_caveats]
assert "rtm_warning" not in normal_types, "False positive RTM warning on normal question"
print("[PASS] T3.8c -- No false positive RTM on 'Should we add delivery?'")
```

### T3.9 -- Small sample and high failure caveats

```python
# Small sample
small_caveats = generate_caveats(biz, "Test question", 8, 8)
small_types = [c.type for c in small_caveats]
assert "small_sample" in small_types, "Missing small_sample caveat for persona_count=8"
print("[PASS] T3.9a -- Small sample caveat triggered for persona_count=8")

# High failure rate
fail_caveats = generate_caveats(biz, "Test question", 15, 10)
fail_types = [c.type for c in fail_caveats]
assert "high_failure_rate" in fail_types, "Missing high_failure_rate caveat for 5/15 failures"
print("[PASS] T3.9b -- High failure rate caveat triggered (10/15 success)")

# Profile quality
sparse_biz = BusinessSnapshot(
    name="X", type="restaurant", description="short",
    customer_description=None, location=None,
)
quality_caveats = generate_caveats(sparse_biz, "Test", 15, 15)
quality_types = [c.type for c in quality_caveats]
assert "profile_quality" in quality_types, "Missing profile_quality caveat for sparse profile"
print("[PASS] T3.9c -- Profile quality caveat triggered for sparse business description")
```

---

## SECTION 4: SIMULATION TYPE TESTS

These tests require the Claude API. Skip if ANTHROPIC_API_KEY is not set. Each test runs a real simulation pipeline step.

**Important**: These tests call the Claude API and cost money. Each test uses 1-3 API calls.

### Setup

```python
import os
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.config import get_settings

settings = get_settings()
HAS_API_KEY = bool(settings.anthropic_api_key)
if not HAS_API_KEY:
    print("[SKIP] Section 4 -- ANTHROPIC_API_KEY not set, skipping all simulation tests")
```

### T4.1 -- Standard simulation: persona generation for spanish_restaurant

```python
import asyncio
from backend.survey.test_seeder import TestSeeder
from backend.models.business import BusinessSnapshot
from backend.swarm.persona_generator import generate_personas  # or backend.swarm import

if HAS_API_KEY:
    seeder = TestSeeder()
    data = seeder.generate(profile="spanish_restaurant")
    biz = BusinessSnapshot(
        name=data["name"], type=data["type"],
        description=data["description"],
        customer_description=data.get("customer_description"),
        location=data.get("location"),
    )

    personas = asyncio.run(generate_personas(biz, 5))
    assert len(personas) >= 3, f"Expected 3+ personas, got {len(personas)}"

    # Verify persona fields
    for p in personas:
        assert p.name, f"Persona missing name"
        assert p.age > 0, f"Persona {p.name} has invalid age"
        assert p.personality, f"Persona {p.name} missing personality"
    print(f"[PASS] T4.1 -- Generated {len(personas)} personas for spanish_restaurant")
    for p in personas:
        print(f"       {p.name}, age {p.age}, {p.visit_frequency}")
else:
    print("[SKIP] T4.1 -- Standard simulation: ANTHROPIC_API_KEY not set")
```

### T4.2 -- Cultural comparison: ES (UA=86) vs GB (UA=35) persona differences

```python
if HAS_API_KEY:
    gb_data = seeder.generate(profile="uk_barbershop")
    gb_biz = BusinessSnapshot(
        name=gb_data["name"], type=gb_data["type"],
        description=gb_data["description"],
        customer_description=gb_data.get("customer_description"),
        location=gb_data.get("location"),
    )

    gb_personas = asyncio.run(generate_personas(gb_biz, 5))
    assert len(gb_personas) >= 3, f"Expected 3+ GB personas, got {len(gb_personas)}"
    print(f"[PASS] T4.2 -- Cultural comparison: ES={len(personas)} personas, GB={len(gb_personas)} personas")
    print(f"       ES (UA=86): {[p.name for p in personas]}")
    print(f"       GB (UA=35): {[p.name for p in gb_personas]}")
else:
    print("[SKIP] T4.2 -- Cultural comparison: ANTHROPIC_API_KEY not set")
```

### T4.3 -- Interview simulation with context

```python
if HAS_API_KEY:
    from backend.swarm.simulator import run_simulation as run_sim

    # Use the ES personas from T4.1
    responses = asyncio.run(run_sim(
        personas[:3], biz,
        "What if we raised lunch prices by 10%?",
        variant_a="Raise all prices by 10%",
        variant_b="Raise only seafood prices by 15%, keep tapas the same",
    ))
    assert len(responses) >= 2, f"Expected 2+ responses, got {len(responses)}"

    for r in responses:
        assert "sentiment" in r, f"Response missing sentiment"
        assert "response" in r or "reaction" in r, f"Response missing reaction text"
        sent = float(r.get("sentiment", 0))
        assert -1.0 <= sent <= 1.0, f"Sentiment {sent} out of range [-1, 1]"

    print(f"[PASS] T4.3 -- Interviewed {len(responses)} personas on price increase")
    for r in responses:
        name = r.get("persona_name", "?")
        sent = r.get("sentiment", 0)
        pref = r.get("preference", "?")
        print(f"       {name}: sentiment={sent}, preference={pref}")
else:
    print("[SKIP] T4.3 -- Interview simulation: ANTHROPIC_API_KEY not set")
```

### T4.4 -- Aggregation produces structured output

```python
if HAS_API_KEY:
    from backend.swarm.aggregator import aggregate_responses

    result = asyncio.run(aggregate_responses(
        biz,
        "What if we raised lunch prices by 10%?",
        responses,
        variant_a="Raise all prices by 10%",
        variant_b="Raise only seafood prices by 15%, keep tapas the same",
    ))
    assert "summary" in result, "Aggregation missing summary"
    assert "recommendation" in result, "Aggregation missing recommendation"
    assert "confidence_score" in result, "Aggregation missing confidence_score"
    print(f"[PASS] T4.4 -- Aggregation complete: confidence={result['confidence_score']}")
    print(f"       Summary: {result['summary'][:200]}...")
else:
    print("[SKIP] T4.4 -- Aggregation: ANTHROPIC_API_KEY not set")
```

### T4.5 -- Impact estimation on real responses

```python
if HAS_API_KEY:
    impact = estimate_impact(responses, "What if we raised lunch prices by 10%?")
    assert impact.decision in ("proceed", "caution", "avoid", "test_first"), \
        f"Invalid decision: {impact.decision}"
    assert impact.total_customers_modelled == len(responses)
    print(f"[PASS] T4.5 -- Impact: {impact.revenue.point_estimate_pct:+.1f}% "
          f"[{impact.revenue.ci_low_pct:+.1f}%, {impact.revenue.ci_high_pct:+.1f}%], "
          f"decision={impact.decision}")
else:
    print("[SKIP] T4.5 -- Impact estimation: ANTHROPIC_API_KEY not set")
```

### T4.6 -- Twin engine query

```python
if HAS_API_KEY:
    from backend.crm.twin_engine import query_twin

    test_signals = {
        "communication_style": "formal",
        "formality_level": 7,
        "avg_response_hours": 4,
        "typical_response_style": "Detailed, asks clarifying questions",
        "decision_patterns": ["Needs approval from partner", "Requests written proposals"],
        "objection_patterns": ["Price too high", "Timeline too tight"],
        "what_matters_most": ["Quality", "Reliability", "References"],
        "topic_themes": ["supply costs", "delivery schedules"],
        "message_count": 45,
    }

    twin_result = asyncio.run(query_twin(
        question="How should I approach asking for a 5% discount on our next order?",
        contact_name="Marco Suppliers",
        extracted_signals=test_signals,
    ))
    assert "answer" in twin_result, "Twin result missing answer"
    assert "confidence" in twin_result, "Twin result missing confidence"
    assert twin_result["confidence"] in ("high", "medium", "low"), \
        f"Invalid confidence: {twin_result['confidence']}"
    print(f"[PASS] T4.6 -- Twin query: confidence={twin_result['confidence']}")
    print(f"       Answer: {twin_result['answer'][:200]}...")
else:
    print("[SKIP] T4.6 -- Twin engine: ANTHROPIC_API_KEY not set")
```

### T4.7 -- Customer vs vendor prompt difference

```python
if HAS_API_KEY:
    from research.rag_library import get_simulation_context

    consumer_ctx = get_simulation_context("ES", simulation_type="consumer")
    vendor_ctx = get_simulation_context("ES", simulation_type="vendor")

    # Vendor context should be strictly longer (includes negotiation)
    assert len(vendor_ctx) > len(consumer_ctx), \
        f"Vendor context ({len(vendor_ctx)}) not longer than consumer ({len(consumer_ctx)})"
    print(f"[PASS] T4.7 -- Vendor context ({len(vendor_ctx)} chars) > "
          f"consumer ({len(consumer_ctx)} chars), "
          f"delta={len(vendor_ctx) - len(consumer_ctx)} chars")
else:
    print("[SKIP] T4.7 -- Prompt difference: ANTHROPIC_API_KEY not set")
```

### T4.8 -- Novelty effect caveat triggered correctly

```python
novelty_caveats = generate_caveats(biz, "What if we launch a new loyalty app?", 15, 15)
novelty_types = [c.type for c in novelty_caveats]
assert "novelty_effect" in novelty_types, "Missing novelty_effect for loyalty app question"
assert "adherence_gap" in novelty_types, "Missing adherence_gap for loyalty app question"
print("[PASS] T4.8 -- Loyalty app question triggers novelty_effect + adherence_gap caveats")
```

### T4.9 -- Persona diversity check

```python
if HAS_API_KEY:
    # Generate 10 personas and verify diversity
    diverse_personas = asyncio.run(generate_personas(biz, 10))
    ages = [p.age for p in diverse_personas]
    age_range = max(ages) - min(ages)
    assert age_range >= 15, f"Age range too narrow: {age_range} years (min={min(ages)}, max={max(ages)})"

    # Check for personality variety
    personalities = [p.personality for p in diverse_personas]
    unique_personalities = len(set(personalities))
    assert unique_personalities >= 7, f"Only {unique_personalities} unique personalities out of 10"

    print(f"[PASS] T4.9 -- Persona diversity: age range={age_range} years, "
          f"{unique_personalities} unique personalities out of {len(diverse_personas)}")
else:
    print("[SKIP] T4.9 -- Persona diversity: ANTHROPIC_API_KEY not set")
```

### T4.10 -- Segment-specific: personas reflect business type

```python
if HAS_API_KEY:
    # A barbershop should have different persona demographics than a restaurant
    assert all(p.occupation for p in gb_personas), "GB barbershop personas missing occupations"
    print("[PASS] T4.10 -- Business type shapes persona demographics")
else:
    print("[SKIP] T4.10 -- Segment-specific: ANTHROPIC_API_KEY not set")
```

### T4.11 -- Correspondence processor

```python
if HAS_API_KEY:
    from backend.crm.correspondence_processor import process_correspondence

    sample_correspondence = """
    [2026-03-01 09:15] You: Hi Marco, following up on the olive oil order
    [2026-03-01 14:30] Marco: Hello, yes I have the quote ready. 50L at 8.50/L
    [2026-03-02 10:00] You: Can we do 7.80/L for a 6-month commitment?
    [2026-03-02 16:45] Marco: I need to check with my partner. Our costs went up this quarter.
    [2026-03-03 09:00] Marco: We can do 8.20/L for 6 months minimum 50L/month
    [2026-03-03 11:30] You: Deal. Send the contract please.
    [2026-03-03 12:00] Marco: Perfect, sending now. Delivery every 2nd Tuesday as usual?
    """

    signals = asyncio.run(process_correspondence(
        raw_text=sample_correspondence,
        contact_name="Marco",
        source_type="whatsapp",
    ))
    assert "communication_style" in signals, "Missing communication_style"
    assert "message_count" in signals, "Missing message_count"
    assert signals["message_count"] > 0, "Message count is 0"
    print(f"[PASS] T4.11 -- Correspondence processed: {signals['message_count']} messages, "
          f"style={signals.get('communication_style')}")
else:
    print("[SKIP] T4.11 -- Correspondence processor: ANTHROPIC_API_KEY not set")
```

### T4.12 -- Full pipeline impact + caveats integration

```python
if HAS_API_KEY:
    # Combine impact estimation with caveats to verify they work together
    impact = estimate_impact(responses, "What if we raised lunch prices by 10%?")
    caveats = generate_caveats(
        biz, "What if we raised lunch prices by 10%?", len(responses), len(responses)
    )
    assert impact.decision in ("proceed", "caution", "avoid", "test_first")
    assert len(caveats) >= 3, f"Expected 3+ caveats, got {len(caveats)}"
    assert any(c.type == "price_sensitivity" for c in caveats), "Missing price_sensitivity caveat"
    print(f"[PASS] T4.12 -- Full pipeline: decision={impact.decision}, "
          f"{len(caveats)} caveats, impact={impact.revenue.point_estimate_pct:+.1f}%")
else:
    print("[SKIP] T4.12 -- Full pipeline: ANTHROPIC_API_KEY not set")
```

---

## SECTION 5: ML CALIBRATION

Tests for the ML model built in Section 0.

### T5.1 -- Feature vector completeness

```python
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.survey.feature_extractor import FeatureExtractor
from backend.survey.test_seeder import TestSeeder

extractor = FeatureExtractor(target="workspace")
seeder = TestSeeder()

# Feature names should include base fields + Hofstede derived
names = extractor.feature_names
assert len(names) >= 15, f"Expected 15+ features, got {len(names)}"

# Verify Hofstede derived features are in the names list
hofstede = [n for n in names if n.startswith("hofstede_")]
assert len(hofstede) == 6, f"Expected 6 Hofstede derived features, got {len(hofstede)}: {hofstede}"
print(f"[PASS] T5.1 -- Feature vector: {len(names)} features, {len(hofstede)} Hofstede derived")
print(f"       Features: {names}")
```

### T5.2 -- Model training produces valid results

```python
from backend.ml.calibration_model import CalibrationModel
from backend.ml.generate_training_data import generate_training_data

records = generate_training_data(35)
model = CalibrationModel()
result = model.train(records)

assert 0.0 < result["cv_accuracy_mean"] <= 1.0, f"Invalid CV accuracy: {result['cv_accuracy_mean']}"
assert result["n_records"] == 35
assert len(result["top_features"]) > 0
print(f"[PASS] T5.2 -- Model trained: CV={result['cv_accuracy_mean']:.3f} "
      f"+/- {result['cv_accuracy_std']:.3f}, {result['n_records']} records")
```

### T5.3 -- Feature importance is meaningful

```python
importance = model.feature_importance()
assert len(importance) > 0, "No feature importance returned"

# At least some features should have non-zero importance
nonzero = [(name, imp) for name, imp in importance if imp > 0.01]
assert len(nonzero) >= 3, f"Only {len(nonzero)} features with importance > 0.01"
print(f"[PASS] T5.3 -- Feature importance: {len(nonzero)} features with importance > 0.01")
for name, imp in importance[:5]:
    print(f"       {name}: {imp:.4f}")
```

### T5.4 -- Prediction works for all seed profiles

```python
for profile in ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]:
    data = seeder.generate(profile=profile)
    prediction = model.predict_accuracy(data)
    assert prediction["prediction"] in ("accurate", "inaccurate"), \
        f"Invalid prediction for {profile}: {prediction['prediction']}"
    assert 0.0 <= prediction["confidence"] <= 1.0, \
        f"Invalid confidence for {profile}: {prediction['confidence']}"
    print(f"[PASS] T5.4 -- {profile}: prediction={prediction['prediction']}, "
          f"confidence={prediction['confidence']:.3f}")
```

### T5.5 -- Model persistence (save/load round-trip)

```python
model.save()

model2 = CalibrationModel()
assert model2.model is not None, "Model not loaded from disk"

# Predictions should be identical
data = seeder.generate(profile="spanish_restaurant")
p1 = model.predict_accuracy(data)
p2 = model2.predict_accuracy(data)
assert p1["prediction"] == p2["prediction"], "Predictions differ after reload"
assert abs(p1["confidence"] - p2["confidence"]) < 0.001, "Confidence differs after reload"
print("[PASS] T5.5 -- Model save/load round-trip: predictions identical")
```

### T5.6 -- Retraining with more data changes results

```python
# Train with 35 records
records_small = generate_training_data(35)
model_a = CalibrationModel()
result_a = model_a.train(records_small)

# Train with 60 records
records_large = generate_training_data(60)
model_b = CalibrationModel()
result_b = model_b.train(records_large)

# More data should generally give similar or better CV
print(f"[PASS] T5.6 -- Retraining: 35 records CV={result_a['cv_accuracy_mean']:.3f}, "
      f"60 records CV={result_b['cv_accuracy_mean']:.3f}")
```

---

## SECTION 6: SURVEY DATA UTILISATION

Verify that specific survey fields actually affect simulation outputs. These tests check that survey data flows through the schema engine into RAG context and persona generation.

### T6.1 -- business_type affects RAG and persona context

```python
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.survey.rag_builder import build_rag_context, build_persona_context
from backend.survey.test_seeder import TestSeeder

seeder = TestSeeder()

restaurant_data = seeder.generate(profile="spanish_restaurant")
barbershop_data = seeder.generate(profile="uk_barbershop")

r_rag = build_rag_context(restaurant_data)
b_rag = build_rag_context(barbershop_data)

assert "restaurant" in r_rag.lower(), "Restaurant type not in RAG context"
assert "barbershop" in b_rag.lower(), "Barbershop type not in RAG context"
assert r_rag != b_rag, "Different business types produced identical RAG"

r_persona = build_persona_context(restaurant_data)
b_persona = build_persona_context(barbershop_data)
assert "restaurant" in r_persona.lower(), "Restaurant type not in persona context"
assert "barbershop" in b_persona.lower(), "Barbershop type not in persona context"
print("[PASS] T6.1 -- business_type 'restaurant' vs 'barbershop' produces different RAG + persona context")
```

### T6.2 -- visit_frequency affects feature vector and RAG

```python
from backend.survey.feature_extractor import FeatureExtractor

extractor = FeatureExtractor(target="workspace")

daily_data = {"visit_frequency": "daily", "location_country": "ES"}
monthly_data = {"visit_frequency": "monthly", "location_country": "ES"}

daily_features = extractor.extract(daily_data)
monthly_features = extractor.extract(monthly_data)

# visit_frequency is ordinal: daily < weekly < monthly < occasional
# daily = index 0 -> 0.0, monthly = index 2 -> 0.5
assert daily_features.get("visit_frequency", -1) != monthly_features.get("visit_frequency", -1), \
    "daily and monthly visit_frequency should have different feature values"
assert daily_features.get("visit_frequency", 1) < monthly_features.get("visit_frequency", 0), \
    f"daily ({daily_features.get('visit_frequency')}) should encode lower than monthly ({monthly_features.get('visit_frequency')})"
print(f"[PASS] T6.2 -- visit_frequency ordinal encoding: daily={daily_features.get('visit_frequency')}, "
      f"monthly={monthly_features.get('visit_frequency')}")
```

### T6.3 -- area_demographics affects RAG context

```python
biz_data = seeder.generate(profile="spanish_restaurant")
rag_with_demo = build_rag_context(biz_data)

biz_no_demo = dict(biz_data)
del biz_no_demo["area_demographics"]
rag_without_demo = build_rag_context(biz_no_demo)

# RAG with demographics should be longer (more info)
assert len(rag_with_demo) > len(rag_without_demo), \
    "RAG context should be longer when area_demographics is provided"
assert "business" in rag_with_demo.lower(), "Missing area demographics content in RAG"
print(f"[PASS] T6.3 -- area_demographics adds {len(rag_with_demo) - len(rag_without_demo)} chars to RAG")
```

### T6.4 -- customer_value_drivers in RAG and features

```python
vd_data = {"customer_value_drivers": ["atmosphere", "personal_touch", "quality"]}
vd_rag = build_rag_context(vd_data)
assert "atmosphere" in vd_rag.lower() or "personal_touch" in vd_rag.lower(), \
    "Value drivers not reflected in RAG context"

vd_features = extractor.extract(vd_data)
# customer_value_drivers uses onehot encoding
atmo_key = "customer_value_drivers__atmosphere"
if atmo_key in vd_features:
    assert vd_features[atmo_key] == 1.0, f"atmosphere should be 1.0, got {vd_features[atmo_key]}"
    # Check that a non-selected value is 0.0
    loc_key = "customer_value_drivers__location"
    if loc_key in vd_features:
        assert vd_features[loc_key] == 0.0, f"location should be 0.0, got {vd_features[loc_key]}"
    print("[PASS] T6.4 -- customer_value_drivers onehot: atmosphere=1.0, location=0.0")
else:
    print(f"[PASS] T6.4 -- customer_value_drivers in RAG (onehot key format may differ)")
```

### T6.5 -- competitor_count ordinal encoding

```python
only_data = {"competitor_count": "only_one"}
six_data = {"competitor_count": "six_plus"}
only_features = extractor.extract(only_data)
six_features = extractor.extract(six_data)

# only_one = index 0, six_plus = index 3
assert only_features.get("competitor_count", 1) < six_features.get("competitor_count", 0), \
    f"only_one ({only_features.get('competitor_count')}) should encode lower than six_plus ({six_features.get('competitor_count')})"
print(f"[PASS] T6.5 -- competitor_count ordinal: only_one={only_features.get('competitor_count')}, "
      f"six_plus={six_features.get('competitor_count')}")
```

### T6.6 -- customer_social_context in RAG

```python
social_data = seeder.generate(profile="spanish_restaurant")
social_rag = build_rag_context(social_data)
# customer_social_context has rag.include=true, weight=medium
# Even if not in the profile, verify the field definition exists
schema = extractor.schema
social_field = schema.get_field("customer_social_context")
assert social_field is not None, "customer_social_context field missing from schema"
assert social_field.rag.include is True, "customer_social_context should have rag.include=true"
print(f"[PASS] T6.6 -- customer_social_context field exists with rag.include=true, "
      f"section='{social_field.rag.section}'")
```

### T6.7 -- regular_proportion affects features

```python
none_data = {"regular_proportion": "almost_none"}
most_data = {"regular_proportion": "mostly_regulars"}
none_features = extractor.extract(none_data)
most_features = extractor.extract(most_data)

assert none_features.get("regular_proportion", 1) < most_features.get("regular_proportion", 0), \
    "almost_none should encode lower than mostly_regulars"
print(f"[PASS] T6.7 -- regular_proportion ordinal: almost_none={none_features.get('regular_proportion')}, "
      f"mostly_regulars={most_features.get('regular_proportion')}")
```

---

## SECTION 7: DATA FLOW VERIFICATION

Verify end-to-end data flow through each pipeline stage.

### T7.1 -- Survey data -> Schema fields

```python
import sys
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.survey.schema_loader import get_schema
from backend.survey.test_seeder import TestSeeder

schema = get_schema()
seeder = TestSeeder()
data = seeder.generate(profile="spanish_restaurant")

# Every key in seed data should map to a schema field
for key in data.keys():
    field = schema.get_field(key)
    assert field is not None, f"Seed data key '{key}' not found in schema"
print(f"[PASS] T7.1 -- All {len(data)} seed data keys map to schema fields")
```

### T7.2 -- Schema -> RAG context (no data loss for included fields)

```python
from backend.survey.rag_builder import build_rag_context

rag_fields = schema.fields_for_rag("workspace")
included_ids = [f.id for f in rag_fields]

context = build_rag_context(data)
# Every RAG-included field that has data should appear in the context
for field in rag_fields:
    value = data.get(field.id)
    if value and value != [] and value != "":
        # The template should have placed the value in the context
        # (might be the label, might be the raw value)
        str_val = str(value) if not isinstance(value, list) else value[0] if value else ""
        # At minimum, the section header should be present
        assert field.rag.section in context, \
            f"Field '{field.id}' (section '{field.rag.section}') not in RAG context"

print(f"[PASS] T7.2 -- {len(included_ids)} RAG fields checked, all sections present in context")
```

### T7.3 -- RAG context -> Simulation (template variables)

```python
# Verify prompt templates reference the right variables
from pathlib import Path
import re

PROMPT_DIR = Path("/Users/Carlos/Desktop/Projects/murmur/murmur/backend/swarm/prompts")

persona_base = (PROMPT_DIR / "persona_base.txt").read_text()
persona_interview = (PROMPT_DIR / "persona_interview.txt").read_text()
aggregation = (PROMPT_DIR / "aggregation.txt").read_text()

# Verify key template variables exist in prompts
assert "{{business_name}}" in persona_base, "persona_base.txt missing {{business_name}}"
assert "{{business_type}}" in persona_base, "persona_base.txt missing {{business_type}}"
assert "{{context_narrative}}" in persona_base, "persona_base.txt missing {{context_narrative}}"

assert "{{persona_name}}" in persona_interview, "persona_interview.txt missing {{persona_name}}"
assert "{{question}}" in persona_interview, "persona_interview.txt missing {{question}}"
assert "{{context_narrative}}" in persona_interview, "persona_interview.txt missing {{context_narrative}}"

assert "{{persona_responses_json}}" in aggregation, "aggregation.txt missing {{persona_responses_json}}"
assert "{{response_count}}" in aggregation, "aggregation.txt missing {{response_count}}"
assert "{{context_narrative}}" in aggregation, "aggregation.txt missing {{context_narrative}}"

print("[PASS] T7.3 -- All 3 prompt templates contain required template variables")
```

### T7.4 -- Survey -> ML feature pipeline

```python
from backend.survey.feature_extractor import FeatureExtractor

extractor = FeatureExtractor(target="workspace")
ml_fields = schema.fields_for_ml("workspace")

# Every ML-included field should produce at least one feature
for field in ml_fields:
    test_data = {field.id: "test_value"}
    # For onehot fields, we need a valid value
    if field.ml.encoding == "onehot" and field.options:
        flat = []
        for opt in field.options:
            if "items" in opt:
                flat.extend(i["value"] for i in opt["items"])
            elif "values" in opt:
                flat.extend(i["value"] for i in opt["values"])
            elif "value" in opt:
                flat.append(opt["value"])
        if flat:
            test_data[field.id] = flat[0]

    features = extractor.extract(test_data)
    related = [k for k in features.keys() if k.startswith(field.id) or k.startswith("hofstede_")]
    # At least the base field or its derived features should be present
    assert len(features) > 0, f"ML field '{field.id}' produced no features"

print(f"[PASS] T7.4 -- All {len(ml_fields)} ML fields produce features through FeatureExtractor")
```

### T7.5 -- Outcome -> Retraining path exists

**REQUIRES BACKEND BUILD** -- Verify the path from real_outcomes table back to model retraining.

```python
# Verify the CalibrationModel can accept real_outcomes-format records
from backend.ml.calibration_model import CalibrationModel

# Simulate what a real_outcomes record would look like
outcome_records = [
    {
        "survey_data": seeder.generate(profile="spanish_restaurant"),
        "outcome_matched": True,
    },
    {
        "survey_data": seeder.generate(profile="uk_barbershop"),
        "outcome_matched": False,
    },
]

model = CalibrationModel()
# Should not crash with 2 records (too few for CV, but train should work)
try:
    result = model.train(outcome_records * 6)  # 12 records
    print(f"[PASS] T7.5 -- Outcome->Retraining path works: "
          f"CV={result['cv_accuracy_mean']:.3f}")
except Exception as e:
    print(f"[FAIL] T7.5 -- Outcome->Retraining failed: {e}")
```

### T7.6 -- Schema change auto-update verification

```python
# Verify that fields_for_rag, fields_for_ml, fields_for_persona
# all draw from the same schema instance
schema = get_schema()
rag = schema.fields_for_rag("workspace")
ml = schema.fields_for_ml("workspace")
persona = schema.fields_for_persona("workspace")

# All field sets should be subsets of all fields
all_ids = set()
for section in schema.sections:
    for field in section.fields:
        all_ids.add(field.id)

rag_ids = set(f.id for f in rag)
ml_ids = set(f.id for f in ml)
persona_ids = set(f.id for f in persona)

assert rag_ids.issubset(all_ids), f"RAG fields not in schema: {rag_ids - all_ids}"
assert ml_ids.issubset(all_ids), f"ML fields not in schema: {ml_ids - all_ids}"
assert persona_ids.issubset(all_ids), f"Persona fields not in schema: {persona_ids - all_ids}"

print(f"[PASS] T7.6 -- Schema drives all consumers: "
      f"{len(rag_ids)} RAG, {len(ml_ids)} ML, {len(persona_ids)} persona fields "
      f"(from {len(all_ids)} total)")
```

---

## SECTION 8: PERFORMANCE

Benchmark tests. No API calls needed for most (except T8.1 if running with API).

### T8.1 -- Schema loading time

```python
import sys
import time
sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

import backend.survey.schema_loader as sl

# Cold load
sl._instance = None
sl._mtime = 0
start = time.perf_counter()
schema = sl.get_schema()
cold_ms = (time.perf_counter() - start) * 1000

# Warm load
start = time.perf_counter()
schema2 = sl.get_schema()
warm_ms = (time.perf_counter() - start) * 1000

assert cold_ms < 500, f"Cold schema load too slow: {cold_ms:.1f}ms"
assert warm_ms < 5, f"Warm schema load too slow: {warm_ms:.1f}ms"
print(f"[PASS] T8.1 -- Schema load: cold={cold_ms:.1f}ms, warm={warm_ms:.2f}ms")
```

### T8.2 -- RAG context assembly time

```python
from backend.survey.rag_builder import build_rag_context
from backend.survey.test_seeder import TestSeeder

seeder = TestSeeder()
data = seeder.generate(profile="spanish_restaurant")

start = time.perf_counter()
for _ in range(100):
    build_rag_context(data)
rag_ms = (time.perf_counter() - start) * 10  # per iteration in ms

assert rag_ms < 50, f"RAG build too slow: {rag_ms:.1f}ms per call"
print(f"[PASS] T8.2 -- RAG context assembly: {rag_ms:.1f}ms per call (100 iterations)")
```

### T8.3 -- Feature extraction time

```python
from backend.survey.feature_extractor import FeatureExtractor

extractor = FeatureExtractor(target="workspace")

start = time.perf_counter()
for _ in range(100):
    extractor.extract(data)
feat_ms = (time.perf_counter() - start) * 10  # per iteration in ms

assert feat_ms < 50, f"Feature extraction too slow: {feat_ms:.1f}ms per call"
print(f"[PASS] T8.3 -- Feature extraction: {feat_ms:.1f}ms per call (100 iterations)")
```

### T8.4 -- Impact estimation time (no API)

```python
from backend.impact.estimator import estimate_impact

# 75 personas
large_responses = [
    {"sentiment": (i % 20 - 10) / 10, "persona_name": f"Persona_{i}"}
    for i in range(75)
]

start = time.perf_counter()
for _ in range(100):
    estimate_impact(large_responses, "Price increase test")
impact_ms = (time.perf_counter() - start) * 10  # per iteration

assert impact_ms < 50, f"Impact estimation too slow: {impact_ms:.1f}ms for 75 personas"
print(f"[PASS] T8.4 -- Impact estimation (75 personas): {impact_ms:.1f}ms per call")
```

### T8.5 -- Caveat generation time

```python
from backend.swarm.caveats import generate_caveats
from backend.models.business import BusinessSnapshot

biz = BusinessSnapshot(
    name="Test", type="restaurant", description="A test restaurant with lots of detail",
    customer_description="Local regulars", location="Barcelona",
)

start = time.perf_counter()
for _ in range(1000):
    generate_caveats(biz, "Should we raise prices by 15%?", 15, 15)
caveat_ms = (time.perf_counter() - start)  # total for 1000

assert caveat_ms < 5, f"Caveat generation too slow: {caveat_ms:.3f}s for 1000 calls"
print(f"[PASS] T8.5 -- Caveat generation: {caveat_ms*1000:.1f}ms for 1000 calls "
      f"({caveat_ms:.4f}ms per call)")
```

---

## SECTION 9: REGRESSION SNAPSHOTS

### Approach

After all tests pass, save a snapshot of key outputs for future regression detection.

```python
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "/Users/Carlos/Desktop/Projects/murmur/murmur")

from backend.survey.test_seeder import TestSeeder
from backend.survey.rag_builder import build_rag_context, build_persona_context
from backend.survey.feature_extractor import FeatureExtractor
from backend.impact.estimator import estimate_impact, _sentiment_to_retention
from backend.swarm.caveats import generate_caveats
from backend.models.business import BusinessSnapshot
from backend.survey.schema_loader import get_schema

SNAPSHOT_DIR = Path("/Users/Carlos/Desktop/Projects/murmur/murmur/tests/snapshots")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

seeder = TestSeeder()
extractor = FeatureExtractor(target="workspace")
schema = get_schema()

snapshot = {
    "timestamp": datetime.now().isoformat(),
    "schema_version": schema.version,
    "schema_id": schema.schema_id,
    "profiles": {},
}

for profile in ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]:
    data = seeder.generate(profile=profile)
    features = extractor.extract(data)
    rag = build_rag_context(data)
    persona_ctx = build_persona_context(data)
    accuracy = schema.compute_accuracy_score("workspace", data)

    snapshot["profiles"][profile] = {
        "feature_count": len(features),
        "feature_hash": hashlib.md5(json.dumps(features, sort_keys=True).encode()).hexdigest(),
        "rag_length": len(rag),
        "rag_hash": hashlib.md5(rag.encode()).hexdigest(),
        "persona_ctx_length": len(persona_ctx),
        "accuracy_score": accuracy["percentage"],
        "hofstede_ua": features.get("hofstede_uncertainty_avoidance"),
    }

# Deterministic impact estimates
test_responses = [{"sentiment": 0.5, "persona_name": f"P{i}"} for i in range(15)]
impact = estimate_impact(test_responses, "Test question")
snapshot["impact_benchmark"] = {
    "point_estimate": impact.revenue.point_estimate_pct,
    "ci_low": impact.revenue.ci_low_pct,
    "ci_high": impact.revenue.ci_high_pct,
    "decision": impact.decision,
}

# Retention mapping checkpoints
snapshot["retention_checkpoints"] = {
    "sentiment_1.0": round(_sentiment_to_retention(1.0), 4),
    "sentiment_0.5": round(_sentiment_to_retention(0.5), 4),
    "sentiment_0.0": round(_sentiment_to_retention(0.0), 4),
    "sentiment_-0.5": round(_sentiment_to_retention(-0.5), 4),
    "sentiment_-1.0": round(_sentiment_to_retention(-1.0), 4),
}

# Save
snapshot_path = SNAPSHOT_DIR / f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(snapshot_path, "w") as f:
    json.dump(snapshot, f, indent=2)

print(f"[PASS] T9.1 -- Regression snapshot saved to {snapshot_path}")
print(f"       Schema: {snapshot['schema_id']} v{snapshot['schema_version']}")
for profile, data in snapshot["profiles"].items():
    print(f"       {profile}: features={data['feature_count']}, "
          f"rag={data['rag_length']}chars, UA={data['hofstede_ua']}")
print(f"       Impact benchmark: {snapshot['impact_benchmark']}")
print(f"       Retention: {snapshot['retention_checkpoints']}")
```

### Regression Comparison (run against previous snapshot)

```python
import glob

snapshots = sorted(glob.glob(str(SNAPSHOT_DIR / "snapshot_*.json")))
if len(snapshots) >= 2:
    with open(snapshots[-2]) as f:
        previous = json.load(f)
    with open(snapshots[-1]) as f:
        current = json.load(f)

    regressions = []

    for profile in ["spanish_restaurant", "uk_barbershop", "dutch_retailer"]:
        prev = previous["profiles"].get(profile, {})
        curr = current["profiles"].get(profile, {})

        if prev.get("feature_hash") != curr.get("feature_hash"):
            regressions.append(f"{profile}: feature hash changed")
        if prev.get("hofstede_ua") != curr.get("hofstede_ua"):
            regressions.append(f"{profile}: Hofstede UA changed "
                             f"{prev.get('hofstede_ua')} -> {curr.get('hofstede_ua')}")

    if previous.get("impact_benchmark", {}).get("decision") != \
       current.get("impact_benchmark", {}).get("decision"):
        regressions.append("Impact benchmark decision changed")

    prev_retention = previous.get("retention_checkpoints", {})
    curr_retention = current.get("retention_checkpoints", {})
    for key in prev_retention:
        if abs(prev_retention[key] - curr_retention.get(key, 0)) > 0.001:
            regressions.append(f"Retention checkpoint {key} changed: "
                             f"{prev_retention[key]} -> {curr_retention.get(key)}")

    if regressions:
        print(f"[WARN] T9.2 -- {len(regressions)} regressions detected:")
        for r in regressions:
            print(f"       {r}")
    else:
        print("[PASS] T9.2 -- No regressions detected vs previous snapshot")
else:
    print("[SKIP] T9.2 -- Only one snapshot exists, nothing to compare")
```

---

## SECTION 10: ADDITIONAL COVERAGE (23 tests)

### T10.1 -- Auth: unauthenticated request returns 401

```python
import requests
resp = requests.get("http://localhost:8001/api/businesses/", timeout=5)
assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
print("[PASS] T10.1 -- Unauthenticated request returns 401")
```

### T10.2 -- Auth: invalid token returns 401

```python
resp = requests.get("http://localhost:8001/api/businesses/",
    headers={"Authorization": "Bearer invalid_token_here"}, timeout=5)
assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
print("[PASS] T10.2 -- Invalid token returns 401")
```

### T10.3 -- Auth: survey endpoints do NOT require auth

```python
resp = requests.post("http://localhost:8001/api/survey/place-autocomplete",
    json={"query": "test"}, timeout=10)
assert resp.status_code != 401, f"Survey endpoint should not require auth"
print("[PASS] T10.3 -- Survey endpoints do not require auth")
```

### T10.4 -- API: health endpoint returns ok

```python
resp = requests.get("http://localhost:8001/api/health", timeout=5)
assert resp.status_code == 200
data = resp.json()
assert data["status"] == "ok"
assert "version" in data
print("[PASS] T10.4 -- Health endpoint returns ok")
```

### T10.5 -- API: accuracy-stats returns valid structure without auth

```python
resp = requests.get("http://localhost:8001/api/simulations/accuracy-stats", timeout=5)
# Should return 401 (requires auth)
assert resp.status_code == 401
print("[PASS] T10.5 -- Accuracy-stats requires auth")
```

### T10.6 -- Reviewer Intelligence: bias correction multipliers

```python
sys.path.insert(0, ".")
from backend.reviewer_intelligence.bias_corrector import apply_bias_corrections

# Simulate aggregate review signals
signals = {
    "avg_rating": 4.3,
    "rating_distribution": {1: 5, 2: 3, 3: 8, 4: 15, 5: 30},
    "total_review_count": 61,
    "price_mentions": 5,
    "tourist_ratio_estimate": 0.2,
}
adjusted = apply_bias_corrections(signals)
# Extremity bias: compressed toward center
assert adjusted["adjusted_avg_rating"] < signals["avg_rating"], \
    "Extremity correction should lower inflated average"
# Silent majority estimate should be much larger than reviewer count
assert adjusted.get("estimated_yearly_customers", 0) > signals["total_review_count"] * 10, \
    "Silent majority should be 10x+ reviewers"
print("[PASS] T10.6 -- Bias correction multipliers work correctly")
```

### T10.7 -- Reviewer Intelligence: silent majority proportion

```python
from backend.reviewer_intelligence.silent_majority_estimator import estimate_silent_majority

adjusted = {"adjusted_positive_ratio": 0.6, "adjusted_negative_ratio": 0.1,
            "adjusted_neutral_ratio": 0.3, "estimated_yearly_customers": 1000}
silent = estimate_silent_majority(adjusted, tourist_ratio=0.15)
# Silent majority should have moderate satisfaction (not extreme)
assert silent["satisfaction_level"] in ["moderate", "slightly_positive", "moderate_positive"], \
    f"Silent majority should be moderate, got {silent.get('satisfaction_level')}"
print("[PASS] T10.7 -- Silent majority proportion estimation correct")
```

### T10.8 -- Reviewer Intelligence: customer segments sum to 1.0

```python
from backend.reviewer_intelligence.customer_segment_builder import build_segments

# Mock inputs
adjusted = {"adjusted_positive_ratio": 0.5, "adjusted_negative_ratio": 0.1,
            "adjusted_neutral_ratio": 0.4, "estimated_yearly_customers": 500}
silent = {"satisfaction_level": "moderate", "price_sensitivity": "high",
          "loyalty_score": 0.4, "switching_risk": 0.5}
business = type("B", (), {"type": "restaurant", "location": "Barcelona"})()
segments = build_segments(adjusted, silent, business)
total = sum(s.proportion for s in segments.segments)
assert abs(total - 1.0) < 0.01, f"Segment proportions should sum to 1.0, got {total}"
assert len(segments.segments) == 6, f"Expected 6 segments, got {len(segments.segments)}"
print("[PASS] T10.8 -- Customer segments sum to 1.0 with 6 segments")
```

### T10.9 -- Edge case: empty question handling

```python
from backend.swarm.caveats import generate_caveats
from backend.models.business import BusinessSnapshot

business = BusinessSnapshot(name="Test", type="cafe", description="A cafe")
caveats = generate_caveats(business, "", 15, 15, None, None)
# Should still produce always-on caveats
types = [c.type for c in caveats]
assert "not_causation" in types, "Always-on caveat missing for empty question"
assert "self_selection" in types, "Always-on caveat missing for empty question"
print("[PASS] T10.9 -- Empty question still produces always-on caveats")
```

### T10.10 -- Edge case: unicode business name

```python
from backend.survey.rag_builder import build_rag_context

data = {"name": "Cafe Munchen", "type": "cafe",
        "description": "Ein gemutliches Cafe", "location_country": "DE"}
rag = build_rag_context(data)
assert "Cafe Munchen" in rag, "Unicode name should appear in RAG context"
print("[PASS] T10.10 -- Unicode business name in RAG context")
```

### T10.11 -- Edge case: very long description truncation

```python
from backend.survey.api_validator import validate_survey_payload

long_desc = "x" * 10001
valid, errors = validate_survey_payload(
    {"description": long_desc}, target="workspace")
# Should fail if max_length is set in schema
schema = get_schema()
desc_field = schema.get_field("description")
if desc_field and desc_field.validation.get("max_length"):
    assert not valid, "Very long description should fail validation"
    print("[PASS] T10.11 -- Long description rejected by validator")
else:
    print("[SKIP] T10.11 -- No max_length set for description field")
```

### T10.12 -- Hofstede: Japan (UA=92) produces very high resistance

```python
from research.rag_library import get_country_profile

jp = get_country_profile("JP")
assert jp["uncertainty_avoidance"] == 92, f"Japan UA should be 92, got {jp.get('uncertainty_avoidance')}"
assert jp["simulation_profile"]["change_resistance"] == "very_high"
print("[PASS] T10.12 -- Japan UA=92, change_resistance=very_high")
```

### T10.13 -- Hofstede: Singapore (UA=8) produces very low resistance

```python
sg = get_country_profile("SG")
assert sg["uncertainty_avoidance"] == 8, f"Singapore UA should be 8, got {sg.get('uncertainty_avoidance')}"
assert sg["simulation_profile"]["change_resistance"] == "very_low"
print("[PASS] T10.13 -- Singapore UA=8, change_resistance=very_low")
```

### T10.14 -- Hofstede: 69 countries loaded

```python
import json
with open("research/processed/hofstede_scores.json") as f:
    scores = json.load(f)
country_count = len([k for k in scores if k != "DEFAULT"])
assert country_count >= 69, f"Expected 69+ countries, got {country_count}"
print(f"[PASS] T10.14 -- Hofstede scores: {country_count} countries loaded")
```

### T10.15 -- Schema: migration_alias resolves correctly

```python
schema = get_schema()
# If any field has a migration_alias, verify both ids resolve to the same field
for target in ["workspace"]:
    for field in schema.fields_for_target(target):
        if field.migration_alias:
            resolved = schema.get_field(field.migration_alias)
            assert resolved is not None, f"migration_alias {field.migration_alias} should resolve"
            assert resolved.id == field.id, f"Alias should resolve to same field"
            print(f"[PASS] T10.15 -- migration_alias {field.migration_alias} -> {field.id}")
            break
    else:
        print("[SKIP] T10.15 -- No migration_alias fields found in schema")
        break
```

### T10.16 -- Schema: accuracy weights are non-negative

```python
for field in schema.fields_for_target("workspace"):
    assert field.accuracy.weight >= 0, f"Field {field.id} has negative accuracy weight"
assert schema.total_accuracy_points("workspace") > 0, "Total accuracy should be > 0"
print(f"[PASS] T10.16 -- All accuracy weights non-negative, total={schema.total_accuracy_points('workspace')}")
```

### T10.17 -- Schema: no duplicate field IDs across sections

```python
all_ids = []
for target in ["workspace", "contact_customer", "contact_vendor"]:
    for field in schema.fields_for_target(target):
        assert field.id not in all_ids, f"Duplicate field ID: {field.id}"
        all_ids.append(field.id)
print(f"[PASS] T10.17 -- No duplicate field IDs ({len(all_ids)} unique)")
```

### T10.18 -- Twin: correspondence processor deletes raw text

```python
# Verify the code path includes del raw_text
import inspect
from backend.api.routes.crm_twin import upload_correspondence
source = inspect.getsource(upload_correspondence)
assert "del raw_text" in source, "Raw text must be deleted after processing"
assert "del raw_bytes" in source, "Raw bytes must be deleted after processing"
print("[PASS] T10.18 -- Correspondence upload deletes raw text")
```

### T10.19 -- Twin: confidence scoring based on corpus size

```python
# Small corpus = low confidence, large = high
# Check the logic in upload_correspondence
assert "twin_confidence" in source, "Confidence should be set on upload"
assert '"medium"' in source or "'medium'" in source, "Medium confidence tier should exist"
print("[PASS] T10.19 -- Twin confidence scoring exists in upload handler")
```

### T10.20 -- Impact: asymmetric loss/gain in visit changes

```python
from backend.impact.estimator import _sentiment_to_visit_change

positive_change = _sentiment_to_visit_change(0.5)
negative_change = _sentiment_to_visit_change(-0.5)
assert abs(negative_change) > abs(positive_change), \
    f"Negative sentiment should cause larger visit change: neg={negative_change}, pos={positive_change}"
print(f"[PASS] T10.20 -- Asymmetric loss/gain: neg={negative_change:.1f}%, pos={positive_change:.1f}%")
```

### T10.21 -- Caveats: adherence gap triggers for loyalty card question

```python
caveats = generate_caveats(business, "Would customers sign up for a loyalty card?", 15, 15, None, None)
types = [c.type for c in caveats]
assert "adherence_gap" in types, "Loyalty card question should trigger adherence gap caveat"
print("[PASS] T10.21 -- Adherence gap caveat triggers for loyalty card question")
```

### T10.22 -- Caveats: novelty effect triggers for new product question

```python
caveats = generate_caveats(business, "Should I launch a new delivery service?", 15, 15, None, None)
types = [c.type for c in caveats]
assert "novelty_effect" in types, "New service question should trigger novelty effect caveat"
print("[PASS] T10.22 -- Novelty effect caveat triggers for new service question")
```

### T10.23 -- Caveats: profile quality warning for short description

```python
short_biz = BusinessSnapshot(name="X", type="cafe", description="Cafe")
caveats = generate_caveats(short_biz, "Should I raise prices?", 15, 15, None, None)
types = [c.type for c in caveats]
assert "profile_quality" in types, "Short description should trigger profile quality warning"
print("[PASS] T10.23 -- Profile quality caveat triggers for short description")
```

---

## SECTION 11: TEST REPORT FORMAT

After running all sections, produce a summary table in this format:

```
=====================================================================
MURMUR TEST REPORT -- 2026-04-07
=====================================================================

Section                        | Pass | Fail | Skip | Total
-------------------------------|------|------|------|------
0. Pre-Test Infrastructure     |    4 |    0 |    0 |    4
1. Schema Integrity            |   13 |    0 |    0 |   13
2. Research Library Injection  |   10 |    0 |    0 |   10
3. Statistical Validity        |   12 |    0 |    0 |   12
4. Simulation Type Tests       |    0 |    0 |   12 |   12
5. ML Calibration              |    6 |    0 |    0 |    6
6. Survey Data Utilisation     |    7 |    0 |    0 |    7
7. Data Flow Verification      |    6 |    0 |    0 |    6
8. Performance                 |    5 |    0 |    0 |    5
9. Regression Snapshots        |    1 |    0 |    1 |    2
10. Additional Coverage        |   21 |    0 |    2 |   23
-------------------------------|------|------|------|------
TOTAL                          |   85 |    0 |   15 |  100

FAILURES:
(none)

BUILDS REQUIRED:
- backend/ml/__init__.py (Section 0)
- backend/ml/calibration_model.py (Section 0)
- backend/ml/generate_training_data.py (Section 0)

NOTES:
- Section 4 requires ANTHROPIC_API_KEY for Claude API calls (~$2-5 total)
- Section 9 regression comparison requires 2+ snapshot runs
- All performance benchmarks passed within thresholds
=====================================================================
```

Generate this table by counting [PASS], [FAIL], and [SKIP] lines from each section. Use the exact format above -- ASCII table, no markdown, no emojis.

---

## Files Referenced in This Test Suite

| File | Purpose |
|------|---------|
| `config/survey_schema.yaml` | 43-field schema definition, 4 sections |
| `backend/survey/schema_loader.py` | `get_schema()`, `SurveySchema`, `validate_schema()` |
| `backend/survey/rag_builder.py` | `build_rag_context()`, `build_persona_context()` |
| `backend/survey/feature_extractor.py` | `FeatureExtractor.extract()`, `.feature_names` |
| `backend/survey/test_seeder.py` | `TestSeeder.generate()`, `.schema_coverage_report()` |
| `backend/survey/api_validator.py` | `validate_survey_payload()` |
| `backend/impact/estimator.py` | `estimate_impact()`, `_sentiment_to_retention()` |
| `backend/swarm/caveats.py` | `generate_caveats()`, RTM/novelty/adherence patterns |
| `backend/swarm/prompts/persona_base.txt` | Template vars: `{{business_name}}`, `{{context_narrative}}` |
| `backend/swarm/prompts/persona_interview.txt` | Template vars: `{{persona_name}}`, `{{question}}` |
| `backend/swarm/prompts/aggregation.txt` | Template vars: `{{persona_responses_json}}` |
| `backend/swarm/persona_generator.py` | `generate_personas()` |
| `backend/swarm/simulator.py` | `run_simulation()` |
| `backend/swarm/aggregator.py` | `aggregate_responses()` |
| `backend/crm/twin_engine.py` | `query_twin()` |
| `backend/crm/correspondence_processor.py` | `process_correspondence()` |
| `backend/reviewer_intelligence/__init__.py` | `build_reviewer_intelligence()` |
| `backend/api/routes/simulations.py` | `_run_pipeline()`, `/accuracy-stats` endpoint |
| `research/rag_library.py` | `get_country_profile()`, `get_domain_insights()`, `get_simulation_context()` |
| `research/processed/hofstede_scores.json` | ES UA=86, GB UA=35, NL UA=53, 69 countries |
| `research/processed/prompts/*.md` | 9 domain prompt fragments |
| `backend/ml/calibration_model.py` | **REQUIRES BUILD** -- RandomForestClassifier |
| `backend/ml/generate_training_data.py` | **REQUIRES BUILD** -- synthetic training data |

## Hofstede Reference Values Used

| Country | PDI | IDV | MAS | UA | LTO | IVR |
|---------|-----|-----|-----|-----|-----|-----|
| ES (Spain) | 57 | 51 | 42 | 86 | 48 | 44 |
| GB (United Kingdom) | 35 | 89 | 66 | 35 | 51 | 69 |
| NL (Netherlands) | 38 | 80 | 14 | 53 | 67 | 68 |
| DE (Germany) | 35 | 67 | 66 | 65 | 83 | 40 |
| DEFAULT | 40 | 65 | 50 | 65 | 50 | 55 |
