"""
Experiment Corpus Scraper

Scrapes academic databases, company case studies, and industry reports
to build a structured database of real business experiments with known outcomes.

Usage:
    python -m backend.research.corpus_scraper

Sources (in order of value):
1. Semantic Scholar API (free, no key)
2. SerpAPI Google Scholar (requires key)
3. Direct URL fetches for known high-value papers
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

from backend.research.quality_scorer import score_experiment

logger = logging.getLogger(__name__)

CORPUS_DIR = Path(__file__).parent.parent.parent / "research" / "corpus"
CORPUS_DIR.mkdir(exist_ok=True)
ERROR_LOG = Path(__file__).parent.parent.parent / "research" / "scrape_errors.log"

SERPAPI_KEY = "7f0e571e363f140b435022b57121a1b71f46d956e9ed5a1226f36df365f21d39"


# ============================================================
# SEMANTIC SCHOLAR API (free, no key)
# ============================================================

SEMANTIC_SCHOLAR_QUERIES = [
    "price increase customer reaction field experiment",
    "price change consumer behavior randomized experiment",
    "menu price elasticity restaurant field study",
    "loyalty programme launch customer retention experiment",
    "store renovation customer reaction sales empirical",
    "LLM simulate human behavior accuracy experiment",
    "generative agents consumer prediction validation",
    "hypothetical bias stated preference real behavior",
    "online review vocal minority silent majority empirical",
    "Hofstede cultural dimensions consumer behavior empirical",
    "loss aversion price increase consumer field experiment",
    "status quo bias business change consumer study",
    "A/B test winner rate empirical study",
    "restaurant price increase customer retention",
    "loyalty card introduction consumer behavior study",
    "opening hours change customer behavior study",
    "menu change customer reaction restaurant experiment",
    "digital twin consumer behavior prediction study",
]


async def search_semantic_scholar(query: str, limit: int = 10) -> list[dict]:
    """Search Semantic Scholar API for papers matching query."""
    results = []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": query,
                    "fields": "title,authors,year,citationCount,externalIds,abstract,tldr,venue,publicationTypes,isOpenAccess",
                    "limit": limit,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for paper in data.get("data", []):
                    citations = paper.get("citationCount", 0) or 0
                    year = paper.get("year") or 0
                    # Quality filter
                    if citations < 10 and year < 2023:
                        continue
                    results.append(_paper_to_record(paper, "semantic_scholar"))
            else:
                _log_error(f"Semantic Scholar search failed: {resp.status_code} for query: {query}")
    except Exception as e:
        _log_error(f"Semantic Scholar error: {e} for query: {query}")

    return results


def _paper_to_record(paper: dict, source: str) -> dict:
    """Convert a Semantic Scholar paper to an experiment_corpus record."""
    authors = [a.get("name", "") for a in (paper.get("authors") or [])]
    ext_ids = paper.get("externalIds") or {}
    tldr = paper.get("tldr") or {}

    return {
        "source_name": paper.get("title", ""),
        "source_url": f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
        "source_type": "academic_paper",
        "publication_name": paper.get("venue", ""),
        "authors": authors,
        "published_year": paper.get("year"),
        "doi": ext_ids.get("DOI"),
        "citation_count": paper.get("citationCount", 0),
        "peer_reviewed": bool(paper.get("venue")),
        "abstract": paper.get("abstract", ""),
        "experiment_type": "other",
        "change_description": tldr.get("text", paper.get("abstract", "")[:200]),
        "direction": None,
        "effect_size_raw": None,
        "quality_score": 0.0,
        "processed": False,
        "findings_extracted": False,
    }


# ============================================================
# SERPAPI GOOGLE SCHOLAR
# ============================================================

SERPAPI_QUERIES = [
    '"field experiment" "price increase" "customer" "restaurant" OR "retail"',
    '"randomized controlled trial" "consumer behavior" "small business"',
    '"loyalty programme" "field experiment" "lift" OR "increase"',
    '"menu change" "sales" "empirical" restaurant',
    '"store renovation" "customer" "sales" experiment results',
    '"A/B test" results consumer "price" OR "menu" OR "loyalty"',
    '"natural experiment" "price change" "customer retention"',
    'site:hbr.org "experiment" "price" OR "menu" "customers" result',
    '"opening hours" "customer" "experiment" results',
    '"Starbucks" "price increase" "customer" study',
    '"McDonald\'s" "price" experiment customer results',
]


async def search_serpapi_scholar(query: str, limit: int = 5) -> list[dict]:
    """Search Google Scholar via SerpAPI."""
    results = []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_scholar",
                    "q": query,
                    "api_key": SERPAPI_KEY,
                    "num": limit,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for r in data.get("organic_results", []):
                    citations = (r.get("inline_links", {}).get("cited_by", {}).get("total", 0)) or 0
                    if citations < 5:
                        continue
                    results.append({
                        "source_name": r.get("title", ""),
                        "source_url": r.get("link", ""),
                        "source_type": "academic_paper",
                        "publication_name": r.get("publication_info", {}).get("summary", "")[:100],
                        "citation_count": citations,
                        "abstract": r.get("snippet", ""),
                        "experiment_type": "other",
                        "change_description": r.get("snippet", "")[:200],
                        "quality_score": 0.0,
                        "processed": False,
                    })
            else:
                _log_error(f"SerpAPI failed: {resp.status_code} for query: {query}")
    except Exception as e:
        _log_error(f"SerpAPI error: {e} for query: {query}")

    return results


# ============================================================
# MAIN SCRAPER
# ============================================================

async def run_full_scrape() -> dict:
    """Run the complete scraping pipeline."""
    all_records = []
    stats = {"semantic_scholar": 0, "serpapi": 0, "errors": 0, "deduped": 0}

    # Phase 1: Semantic Scholar
    logger.info("Phase 1: Searching Semantic Scholar (%d queries)", len(SEMANTIC_SCHOLAR_QUERIES))
    for i, query in enumerate(SEMANTIC_SCHOLAR_QUERIES):
        logger.info("  [%d/%d] %s", i + 1, len(SEMANTIC_SCHOLAR_QUERIES), query[:60])
        results = await search_semantic_scholar(query)
        all_records.extend(results)
        stats["semantic_scholar"] += len(results)
        time.sleep(2)  # Rate limit

    # Phase 2: SerpAPI Google Scholar
    logger.info("Phase 2: Searching Google Scholar via SerpAPI (%d queries)", len(SERPAPI_QUERIES))
    for i, query in enumerate(SERPAPI_QUERIES):
        logger.info("  [%d/%d] %s", i + 1, len(SERPAPI_QUERIES), query[:60])
        results = await search_serpapi_scholar(query)
        all_records.extend(results)
        stats["serpapi"] += len(results)
        time.sleep(2)  # Rate limit

    # Deduplicate by title similarity
    seen_titles = set()
    unique_records = []
    for r in all_records:
        title_key = r.get("source_name", "").lower().strip()[:80]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            # Score quality
            r["quality_score"] = score_experiment(r)
            unique_records.append(r)
        else:
            stats["deduped"] += 1

    # Save results
    output_path = CORPUS_DIR / f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(unique_records, f, indent=2, default=str)

    stats["total_unique"] = len(unique_records)
    stats["high_quality"] = sum(1 for r in unique_records if r["quality_score"] >= 0.60)
    stats["medium_quality"] = sum(1 for r in unique_records if 0.40 <= r["quality_score"] < 0.60)
    stats["low_quality"] = sum(1 for r in unique_records if r["quality_score"] < 0.40)

    logger.info("Scrape complete: %d unique records (%d high, %d medium, %d low quality)",
                stats["total_unique"], stats["high_quality"], stats["medium_quality"], stats["low_quality"])

    return stats


def _log_error(msg: str):
    """Append error to scrape_errors.log."""
    with open(ERROR_LOG, "a") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")
    logger.warning(msg)


# CLI entry point
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    stats = asyncio.run(run_full_scrape())
    print(json.dumps(stats, indent=2))
