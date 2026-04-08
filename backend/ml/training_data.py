"""
Training Data Generator

Creates training data for the calibration model from:
1. Known A/B test outcomes (docs/known_ab_tests.md)
2. Synthetic variations based on research
3. Eventually: real user-reported outcomes from real_outcomes table

Each record has: feature vector + was_prediction_correct (binary)

The feature vector comes from FeatureExtractor which reads
survey_schema.yaml, so new survey fields automatically appear.
"""

import random
import numpy as np
from backend.survey.feature_extractor import FeatureExtractor
from backend.survey.test_seeder import TestSeeder


def generate_training_data(n_records: int = 100) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Generate synthetic training records for the calibration model.

    Returns:
        X: Feature matrix (n_records, n_features)
        y: Binary labels (1=correct prediction, 0=incorrect)
        feature_names: List of feature names
    """
    extractor = FeatureExtractor()
    seeder = TestSeeder()

    # Base profiles with known outcomes
    profiles = _known_profiles()

    records_X = []
    records_y = []

    for _ in range(n_records):
        # Pick a random base profile and add noise
        base = random.choice(profiles)
        data = {**base["survey_data"]}

        # Add random noise to simulate variation
        data = _add_noise(data)

        # Extract features
        features = extractor.extract(data)
        feature_vec = [features.get(name, 0.0) for name in extractor.feature_names]

        # Determine correctness probability based on profile completeness and type
        correct_prob = _correctness_probability(data, base)
        was_correct = 1 if random.random() < correct_prob else 0

        records_X.append(feature_vec)
        records_y.append(was_correct)

    X = np.array(records_X)
    y = np.array(records_y)
    return X, y, extractor.feature_names


def _known_profiles() -> list[dict]:
    """Known business profiles from backtest cases and research."""
    return [
        {
            "name": "spanish_restaurant_price_raise",
            "survey_data": {
                "name": "La Tasca de Miguel",
                "type": "restaurant",
                "location_country": "ES",
                "location_city": "Barcelona",
                "years_open": "3-10",
                "business_role": "habit",
                "visit_frequency": "weekly",
                "customer_value_drivers": ["atmosphere", "personal_touch", "quality"],
                "regular_proportion": "solid_base",
                "area_demographics": ["business"],
                "competitor_count": "three_five",
                "area_feel": "community",
                "customer_description": "Local office workers, regulars, price conscious",
            },
            "base_accuracy": 0.70,  # High UA country, price question = harder to predict
        },
        {
            "name": "uk_barbershop_hours",
            "survey_data": {
                "name": "Sharp & Sons",
                "type": "barbershop",
                "location_country": "GB",
                "location_city": "Manchester",
                "years_open": "1-3",
                "business_role": "treat",
                "visit_frequency": "monthly",
                "customer_value_drivers": ["personal_touch", "consistency"],
                "regular_proportion": "mostly_regulars",
                "area_demographics": ["residential"],
                "competitor_count": "one_two",
                "area_feel": "community",
            },
            "base_accuracy": 0.80,  # Low UA, simple question = easier to predict
        },
        {
            "name": "dutch_retailer_loyalty",
            "survey_data": {
                "name": "De Winkel",
                "type": "clothing",
                "location_country": "NL",
                "location_city": "Amsterdam",
                "years_open": "10+",
                "business_role": "destination",
                "visit_frequency": "occasional",
                "customer_value_drivers": ["quality", "specific_product"],
                "area_demographics": ["shopping", "tourist"],
                "competitor_count": "six_plus",
                "area_feel": "destination",
            },
            "base_accuracy": 0.65,  # High competition, tourist mix = harder
        },
        {
            "name": "german_cafe_renovation",
            "survey_data": {
                "name": "Kaffee Haus",
                "type": "cafe",
                "location_country": "DE",
                "location_city": "Berlin",
                "years_open": "3-10",
                "business_role": "habit",
                "visit_frequency": "daily",
                "customer_value_drivers": ["consistency", "atmosphere"],
                "regular_proportion": "mostly_regulars",
                "area_demographics": ["residential", "student"],
                "competitor_count": "three_five",
            },
            "base_accuracy": 0.75,
        },
        {
            "name": "italian_restaurant_menu",
            "survey_data": {
                "name": "Trattoria da Marco",
                "type": "restaurant",
                "location_country": "IT",
                "location_city": "Rome",
                "years_open": "10+",
                "business_role": "social",
                "visit_frequency": "weekly",
                "customer_value_drivers": ["social", "atmosphere", "quality"],
                "regular_proportion": "solid_base",
                "area_demographics": ["tourist", "residential"],
                "competitor_count": "six_plus",
            },
            "base_accuracy": 0.60,  # Tourist mix + high competition = hardest
        },
        {
            "name": "french_bakery_price",
            "survey_data": {
                "name": "Boulangerie Dupont",
                "type": "bakery",
                "location_country": "FR",
                "location_city": "Lyon",
                "years_open": "10+",
                "business_role": "daily_need",
                "visit_frequency": "daily",
                "customer_value_drivers": ["specific_product", "consistency"],
                "regular_proportion": "mostly_regulars",
                "area_demographics": ["residential"],
                "competitor_count": "one_two",
            },
            "base_accuracy": 0.55,  # Very high UA (86), daily habit, price = very hard
        },
        {
            "name": "swedish_gym_hours",
            "survey_data": {
                "name": "FitNord",
                "type": "gym",
                "location_country": "SE",
                "location_city": "Stockholm",
                "years_open": "1-3",
                "business_role": "convenience",
                "visit_frequency": "weekly",
                "customer_value_drivers": ["convenience", "quality"],
                "area_demographics": ["business", "residential"],
                "competitor_count": "three_five",
            },
            "base_accuracy": 0.85,  # Very low UA (29), simple = easiest
        },
        {
            "name": "portuguese_bar_service",
            "survey_data": {
                "name": "O Cantinho",
                "type": "bar",
                "location_country": "PT",
                "location_city": "Lisbon",
                "years_open": "3-10",
                "business_role": "social",
                "visit_frequency": "weekly",
                "customer_value_drivers": ["social", "atmosphere"],
                "regular_proportion": "solid_base",
                "area_demographics": ["tourist", "residential"],
                "competitor_count": "six_plus",
            },
            "base_accuracy": 0.50,  # Highest UA (99), tourist mix = very hard
        },
    ]


def _add_noise(data: dict) -> dict:
    """Add realistic noise to a survey profile for training variation."""
    noised = {**data}

    # Randomly drop some fields (simulates incomplete surveys)
    drop_fields = ["customer_description", "area_feel", "regular_proportion",
                    "customer_value_drivers", "years_open"]
    for field in drop_fields:
        if field in noised and random.random() < 0.3:
            del noised[field]

    # Randomly swap some categorical values
    if "visit_frequency" in noised and random.random() < 0.2:
        noised["visit_frequency"] = random.choice(["daily", "weekly", "monthly", "occasional"])

    if "competitor_count" in noised and random.random() < 0.2:
        noised["competitor_count"] = random.choice(["only_one", "one_two", "three_five", "six_plus"])

    return noised


def _correctness_probability(data: dict, base: dict) -> float:
    """Estimate how likely the prediction is correct given the data.

    Based on research:
    - More data = more accurate (Park et al. 2024)
    - High UA countries = harder to predict (Hofstede 2001)
    - More competition = harder (basic market theory)
    - More complete surveys = more accurate
    """
    prob = base["base_accuracy"]

    # Completeness bonus: each filled field adds accuracy
    filled = sum(1 for v in data.values() if v is not None and v != "" and v != [])
    completeness_bonus = min(0.15, filled * 0.01)
    prob += completeness_bonus

    # Missing key fields penalty
    if "customer_description" not in data:
        prob -= 0.05
    if "visit_frequency" not in data:
        prob -= 0.03
    if "customer_value_drivers" not in data:
        prob -= 0.04

    # Clamp
    return max(0.3, min(0.95, prob))


def load_real_outcomes() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load training data from real validated outcomes in the database.

    Returns empty arrays if no outcomes exist yet.
    """
    try:
        from backend.db.client import get_supabase
        db = get_supabase()
        outcomes = db.table("real_outcomes").select("*").execute()

        if not outcomes.data:
            return np.array([]), np.array([]), []

        # For each outcome, load the simulation's business data
        # and extract features
        extractor = FeatureExtractor()
        records_X = []
        records_y = []

        for outcome in outcomes.data:
            sim_id = outcome["simulation_id"]
            sim = db.table("simulations").select("business_id, business_snapshot").eq("id", sim_id).maybe_single().execute()
            if not sim.data:
                continue

            snapshot = sim.data.get("business_snapshot", {})
            features = extractor.extract(snapshot)
            feature_vec = [features.get(name, 0.0) for name in extractor.feature_names]
            records_X.append(feature_vec)
            records_y.append(1 if outcome.get("outcome_matched") else 0)

        if not records_X:
            return np.array([]), np.array([]), []

        return np.array(records_X), np.array(records_y), extractor.feature_names

    except Exception as e:
        logger.warning("Could not load real outcomes: %s", e)
        return np.array([]), np.array([]), []
