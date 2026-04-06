"""
Research Scraper — collects peer-reviewed articles and studies relevant to Murmur.

Scrapes from:
1. Semantic Scholar API (free, no key needed, 100 req/5min)
   - Peer-reviewed papers with citation counts, abstracts, DOIs
2. arXiv API (free, no key needed)
   - Preprints in CS, economics, statistics
3. CrossRef API (free, no key needed)
   - DOI-based metadata for published papers
4. Google Scholar (via SerpAPI if key provided, else skip)

Stores results as structured JSON in docs/research/.

Usage:
    python -m backend.scraper.research_scraper
    python -m backend.scraper.research_scraper --query "synthetic user simulation"
    python -m backend.scraper.research_scraper --all
"""

import argparse
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent.parent / "docs" / "research"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiting
SEMANTIC_SCHOLAR_DELAY = 3.5  # 100 requests per 5 minutes
ARXIV_DELAY = 3.0
CROSSREF_DELAY = 1.0


# ============================================================
# SEARCH QUERIES — organized by research area
# ============================================================

QUERY_SETS = {
    "synthetic_users": [
        "synthetic user simulation customer behavior",
        "LLM simulated users consumer research",
        "AI generated personas customer feedback",
        "synthetic data user research methodology",
        "large language model role playing simulation",
        "GPT simulated survey respondents",
    ],
    "persona_methodology": [
        "persona based research methodology validity",
        "OCEAN personality model consumer behavior",
        "synthetic persona generation evaluation",
        "customer persona accuracy validation",
        "agent based model consumer simulation",
        "computational social science agent simulation",
    ],
    "ab_testing": [
        "A/B testing statistical pitfalls",
        "online controlled experiment methodology",
        "false positive rate A/B testing",
        "p-hacking online experiments",
        "sample size determination controlled experiments",
        "regression to the mean intervention evaluation",
    ],
    "prediction_validity": [
        "hypothetical bias willingness to pay",
        "stated preference revealed preference gap",
        "survey response bias customer behavior",
        "intention behavior gap consumer research",
        "simulated customer feedback accuracy",
    ],
    "llm_evaluation": [
        "LLM as judge evaluation bias",
        "large language model sycophancy bias",
        "AI positive bias synthetic responses",
        "language model personality simulation",
        "prompt engineering persona consistency",
    ],
}


# ============================================================
# SEMANTIC SCHOLAR
# ============================================================

def search_semantic_scholar(
    query: str, limit: int = 20, year_min: int = 2018
) -> list[dict]:
    """Search Semantic Scholar for papers. Free API, no key needed."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,year,citationCount,url,externalIds,authors,venue,publicationDate",
        "year": f"{year_min}-",
    }

    try:
        resp = httpx.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        papers = data.get("data", [])
        logger.info("Semantic Scholar: %d results for '%s'", len(papers), query)

        results = []
        for p in papers:
            doi = (p.get("externalIds") or {}).get("DOI")
            results.append({
                "source": "semantic_scholar",
                "title": p.get("title", ""),
                "abstract": p.get("abstract", ""),
                "year": p.get("year"),
                "citation_count": p.get("citationCount", 0),
                "url": p.get("url", ""),
                "doi": doi,
                "authors": [a.get("name", "") for a in (p.get("authors") or [])[:5]],
                "venue": p.get("venue", ""),
                "publication_date": p.get("publicationDate"),
                "query": query,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })
        return results

    except Exception as e:
        logger.error("Semantic Scholar error for '%s': %s", query, e)
        return []


# ============================================================
# ARXIV
# ============================================================

def search_arxiv(query: str, limit: int = 15) -> list[dict]:
    """Search arXiv for preprints. Free API."""
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{quote_plus(query)}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        resp = httpx.get(url, params=params, timeout=15)
        resp.raise_for_status()
        text = resp.text

        # Parse XML response (simple regex extraction — arXiv returns Atom XML)
        entries = re.findall(r"<entry>(.*?)</entry>", text, re.DOTALL)
        results = []

        for entry in entries:
            title = _xml_extract(entry, "title").strip().replace("\n", " ")
            abstract = _xml_extract(entry, "summary").strip().replace("\n", " ")
            published = _xml_extract(entry, "published")[:10]
            arxiv_id = _xml_extract(entry, "id")
            authors_raw = re.findall(r"<name>(.*?)</name>", entry)

            # Extract DOI if linked
            doi_match = re.search(r'doi.org/(.*?)["\s<]', entry)
            doi = doi_match.group(1) if doi_match else None

            year_match = re.search(r"(\d{4})", published)
            year = int(year_match.group(1)) if year_match else None

            results.append({
                "source": "arxiv",
                "title": title,
                "abstract": abstract[:1500],
                "year": year,
                "citation_count": None,
                "url": arxiv_id,
                "doi": doi,
                "authors": authors_raw[:5],
                "venue": "arXiv",
                "publication_date": published,
                "query": query,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

        logger.info("arXiv: %d results for '%s'", len(results), query)
        return results

    except Exception as e:
        logger.error("arXiv error for '%s': %s", query, e)
        return []


def _xml_extract(xml: str, tag: str) -> str:
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.DOTALL)
    return match.group(1) if match else ""


# ============================================================
# CROSSREF
# ============================================================

def search_crossref(query: str, limit: int = 15) -> list[dict]:
    """Search CrossRef for published papers with DOIs."""
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "rows": limit,
        "sort": "relevance",
        "filter": "type:journal-article",
        "select": "DOI,title,abstract,author,published-print,container-title,is-referenced-by-count,URL",
    }
    headers = {
        "User-Agent": "Murmur-Research-Scraper/1.0 (mailto:research@murmur.dev)"
    }

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])
        results = []

        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else ""
            abstract = item.get("abstract", "")
            # Strip HTML from CrossRef abstracts
            abstract = re.sub(r"<[^>]+>", "", abstract)

            pub_date = item.get("published-print", {}).get("date-parts", [[None]])[0]
            year = pub_date[0] if pub_date else None

            authors = []
            for a in (item.get("author") or [])[:5]:
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)

            venue_list = item.get("container-title", [])
            venue = venue_list[0] if venue_list else ""

            results.append({
                "source": "crossref",
                "title": title,
                "abstract": abstract[:1500],
                "year": year,
                "citation_count": item.get("is-referenced-by-count", 0),
                "url": item.get("URL", ""),
                "doi": item.get("DOI"),
                "authors": authors,
                "venue": venue,
                "publication_date": f"{year}" if year else None,
                "query": query,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

        logger.info("CrossRef: %d results for '%s'", len(results), query)
        return results

    except Exception as e:
        logger.error("CrossRef error for '%s': %s", query, e)
        return []


# ============================================================
# DEDUPLICATION
# ============================================================

def deduplicate(papers: list[dict]) -> list[dict]:
    """Remove duplicate papers by DOI or normalized title."""
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()
    unique = []

    for p in papers:
        doi = (p.get("doi") or "").lower().strip()
        title_norm = re.sub(r"[^a-z0-9]", "", (p.get("title") or "").lower())

        if doi and doi in seen_dois:
            continue
        if title_norm and title_norm in seen_titles:
            continue

        if doi:
            seen_dois.add(doi)
        if title_norm:
            seen_titles.add(title_norm)
        unique.append(p)

    return unique


# ============================================================
# RELEVANCE SCORING
# ============================================================

def score_relevance(paper: dict) -> float:
    """Simple relevance scoring. Higher = more useful for Murmur."""
    score = 0.0

    # Citation count (capped impact)
    citations = paper.get("citation_count") or 0
    score += min(citations / 50.0, 5.0)

    # Recency bonus
    year = paper.get("year") or 2020
    if year >= 2023:
        score += 3.0
    elif year >= 2021:
        score += 2.0
    elif year >= 2018:
        score += 1.0

    # Title keyword bonus
    title = (paper.get("title") or "").lower()
    high_value_terms = [
        "synthetic user", "simulated customer", "persona",
        "a/b test", "controlled experiment", "llm",
        "language model", "bias", "sycophancy",
        "hypothetical bias", "stated preference",
        "customer simulation", "agent-based",
    ]
    for term in high_value_terms:
        if term in title:
            score += 2.0

    # Has abstract (more useful)
    if paper.get("abstract"):
        score += 1.0

    # Published in a venue (not just preprint)
    venue = (paper.get("venue") or "").lower()
    if venue and venue != "arxiv":
        score += 1.0

    return round(score, 2)


# ============================================================
# MAIN SCRAPER
# ============================================================

def scrape_category(category: str, queries: list[str]) -> list[dict]:
    """Run all queries for a category across all sources."""
    all_papers: list[dict] = []

    for query in queries:
        # Semantic Scholar
        papers = search_semantic_scholar(query, limit=20)
        all_papers.extend(papers)
        time.sleep(SEMANTIC_SCHOLAR_DELAY)

        # arXiv
        papers = search_arxiv(query, limit=10)
        all_papers.extend(papers)
        time.sleep(ARXIV_DELAY)

        # CrossRef
        papers = search_crossref(query, limit=10)
        all_papers.extend(papers)
        time.sleep(CROSSREF_DELAY)

    # Deduplicate
    unique = deduplicate(all_papers)

    # Score and sort
    for p in unique:
        p["relevance_score"] = score_relevance(p)
        p["category"] = category

    unique.sort(key=lambda x: x["relevance_score"], reverse=True)

    return unique


def save_results(category: str, papers: list[dict]):
    """Save results to docs/research/ as JSON."""
    output_file = OUTPUT_DIR / f"{category}.json"

    # Merge with existing if present
    existing = []
    if output_file.exists():
        try:
            existing = json.loads(output_file.read_text())
        except json.JSONDecodeError:
            existing = []

    # Merge and re-deduplicate
    merged = deduplicate(existing + papers)
    for p in merged:
        if "relevance_score" not in p:
            p["relevance_score"] = score_relevance(p)
    merged.sort(key=lambda x: x["relevance_score"], reverse=True)

    output_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    logger.info("Saved %d papers to %s", len(merged), output_file)


def save_summary():
    """Generate a human-readable summary of all scraped research."""
    summary_file = OUTPUT_DIR / "SUMMARY.md"
    lines = [
        "# Scraped Research Corpus",
        "",
        f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    total = 0
    for json_file in sorted(OUTPUT_DIR.glob("*.json")):
        try:
            papers = json.loads(json_file.read_text())
        except json.JSONDecodeError:
            continue

        category = json_file.stem
        total += len(papers)

        lines.append(f"## {category.replace('_', ' ').title()} ({len(papers)} papers)")
        lines.append("")

        # Top 10 by relevance
        for p in papers[:10]:
            title = p.get("title", "Untitled")
            year = p.get("year", "?")
            citations = p.get("citation_count") or 0
            doi = p.get("doi", "")
            score = p.get("relevance_score", 0)
            source = p.get("source", "?")

            doi_link = f"https://doi.org/{doi}" if doi else p.get("url", "")
            lines.append(
                f"- **{title}** ({year}, {citations} citations, score={score}) "
                f"[{source}]({doi_link})"
            )

        if len(papers) > 10:
            lines.append(f"- ... and {len(papers) - 10} more")
        lines.append("")

    lines.insert(3, f"**Total papers: {total}**")
    lines.insert(4, "")

    summary_file.write_text("\n".join(lines))
    logger.info("Summary written to %s", summary_file)


def run_single_query(query: str):
    """Run a single custom query across all sources."""
    logger.info("Running custom query: '%s'", query)
    all_papers = []

    papers = search_semantic_scholar(query, limit=25)
    all_papers.extend(papers)
    time.sleep(SEMANTIC_SCHOLAR_DELAY)

    papers = search_arxiv(query, limit=15)
    all_papers.extend(papers)
    time.sleep(ARXIV_DELAY)

    papers = search_crossref(query, limit=15)
    all_papers.extend(papers)
    time.sleep(CROSSREF_DELAY)

    unique = deduplicate(all_papers)
    for p in unique:
        p["relevance_score"] = score_relevance(p)
        p["category"] = "custom"

    unique.sort(key=lambda x: x["relevance_score"], reverse=True)
    save_results("custom", unique)
    save_summary()

    logger.info("Custom query complete: %d unique papers", len(unique))
    return unique


def run_all():
    """Run all predefined query sets."""
    for category, queries in QUERY_SETS.items():
        logger.info("=== Scraping category: %s (%d queries) ===", category, len(queries))
        papers = scrape_category(category, queries)
        save_results(category, papers)
        logger.info("Category %s: %d unique papers\n", category, len(papers))

    save_summary()
    logger.info("=== All categories complete ===")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Scrape scientific articles for Murmur")
    parser.add_argument("--query", type=str, help="Run a single custom query")
    parser.add_argument("--all", action="store_true", help="Run all predefined query sets")
    parser.add_argument("--category", type=str, choices=list(QUERY_SETS.keys()),
                        help="Run queries for a specific category")
    args = parser.parse_args()

    if args.query:
        run_single_query(args.query)
    elif args.category:
        papers = scrape_category(args.category, QUERY_SETS[args.category])
        save_results(args.category, papers)
        save_summary()
    elif args.all:
        run_all()
    else:
        # Default: run a quick subset to demonstrate
        logger.info("No arguments provided. Running quick demo (2 categories)...")
        for category in ["synthetic_users", "llm_evaluation"]:
            queries = QUERY_SETS[category][:2]  # First 2 queries only
            papers = scrape_category(category, queries)
            save_results(category, papers)
        save_summary()


if __name__ == "__main__":
    main()
