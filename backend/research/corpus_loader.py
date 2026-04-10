"""
Corpus Loader -- uploads scraped experiment data to Supabase.

Run after migration_004_experiment_corpus.sql has been applied.

Usage:
    python -m backend.research.corpus_loader
"""

import json
import logging
from pathlib import Path

from backend.db.client import get_supabase
from backend.research.quality_scorer import score_experiment

logger = logging.getLogger(__name__)

CORPUS_FILE = Path(__file__).parent.parent.parent / "research" / "corpus" / "combined_corpus.json"


def load_corpus_to_supabase():
    """Load all corpus records from JSON into the experiment_corpus table."""
    if not CORPUS_FILE.exists():
        logger.error("Corpus file not found: %s", CORPUS_FILE)
        return {"loaded": 0, "skipped": 0, "errors": 0}

    with open(CORPUS_FILE) as f:
        records = json.load(f)

    db = get_supabase()
    loaded = 0
    skipped = 0
    errors = 0

    for r in records:
        try:
            row = {
                "source_name": r.get("source_name", "Unknown")[:500],
                "source_url": r.get("source_url") or r.get("link"),
                "source_type": r.get("source_type", "academic_paper"),
                "publication_name": (r.get("publication_name") or r.get("venue", ""))[:200],
                "authors": r.get("authors", []),
                "published_year": r.get("published_year") or r.get("year"),
                "doi": r.get("doi"),
                "citation_count": r.get("citation_count") or r.get("citations"),
                "peer_reviewed": r.get("peer_reviewed", False),
                "business_type": r.get("business_type"),
                "business_size": r.get("business_size"),
                "business_name": r.get("business_name"),
                "country": r.get("country"),
                "experiment_type": r.get("experiment_type", "other"),
                "change_description": (r.get("change_description") or r.get("abstract", ""))[:1000],
                "change_magnitude": r.get("change_magnitude"),
                "had_control_group": r.get("had_control_group"),
                "sample_size": r.get("sample_size"),
                "duration_days": r.get("duration_days"),
                "was_randomised": r.get("was_randomised"),
                "primary_metric": r.get("primary_metric"),
                "direction": r.get("direction"),
                "effect_size_raw": r.get("effect_size_raw"),
                "effect_size_numeric": r.get("effect_size_numeric"),
                "statistical_significance": r.get("statistical_significance"),
                "p_value": r.get("p_value"),
                "customer_acceptance_rate": r.get("customer_acceptance_rate"),
                "customer_switch_rate": r.get("customer_switch_rate"),
                "economic_conditions": r.get("economic_conditions"),
                "competitive_context": r.get("competitive_context"),
                "cultural_context": r.get("cultural_context"),
                "murmur_simulation_type": r.get("murmur_simulation_type"),
                "applicable_survey_fields": r.get("applicable_survey_fields"),
                "quality_score": score_experiment(r),
                "abstract": (r.get("abstract") or r.get("snippet", ""))[:2000],
                "key_quotes": r.get("key_quotes"),
            }

            db.table("experiment_corpus").insert(row).execute()
            loaded += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                logger.warning("Failed to load record '%s': %s", r.get("source_name", "?")[:50], e)

    result = {"loaded": loaded, "skipped": skipped, "errors": errors, "total": len(records)}
    logger.info("Corpus loaded: %d/%d records (%d errors)", loaded, len(records), errors)
    return result


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    result = load_corpus_to_supabase()
    print(json.dumps(result, indent=2))
