"""
One-time script to chunk research articles and generate vector embeddings.

Reads all .md files from research/processed/prompts/,
splits by ## headers into sections, generates 768-dim embeddings
with all-mpnet-base-v2, and uploads to Supabase research_sections table.

Usage:
    python -m research.embed_articles
    python -m research.embed_articles --dry-run   # preview without uploading
    python -m research.embed_articles --clear      # clear existing and re-embed
"""

import argparse
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "processed" / "prompts"
MODEL_NAME = "all-mpnet-base-v2"
MAX_TOKENS_PER_SECTION = 768


def split_by_headers(content: str, domain: str) -> list[dict]:
    """Split markdown content into sections by ## headers.

    Returns list of dicts with domain, section_title, content, token_count.
    """
    sections = []
    lines = content.split("\n")
    current_title = domain  # fallback for content before first header
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("## "):
            # Save previous section
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text and len(text) > 50:  # skip tiny fragments
                    sections.append({
                        "domain": domain,
                        "section_title": current_title,
                        "content": text,
                        "token_count": len(text.split()),
                    })
            current_title = line.lstrip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_lines:
        text = "\n".join(current_lines).strip()
        if text and len(text) > 50:
            sections.append({
                "domain": domain,
                "section_title": current_title,
                "content": text,
                "token_count": len(text.split()),
            })

    # Split oversized sections
    final = []
    for section in sections:
        if section["token_count"] > MAX_TOKENS_PER_SECTION:
            chunks = _split_long_section(section)
            final.extend(chunks)
        else:
            final.append(section)

    return final


def _split_long_section(section: dict) -> list[dict]:
    """Split a section that exceeds MAX_TOKENS_PER_SECTION into overlapping chunks."""
    words = section["content"].split()
    chunks = []
    step = MAX_TOKENS_PER_SECTION
    overlap = int(step * 0.1)  # 10% overlap
    start = 0
    part = 1

    while start < len(words):
        end = min(start + step, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "domain": section["domain"],
            "section_title": f"{section['section_title']} (part {part})",
            "content": chunk_text,
            "token_count": end - start,
        })
        start = end - overlap if end < len(words) else end
        part += 1

    return chunks


def main():
    parser = argparse.ArgumentParser(description="Embed research articles for vector search")
    parser.add_argument("--dry-run", action="store_true", help="Preview sections without uploading")
    parser.add_argument("--clear", action="store_true", help="Clear existing sections before uploading")
    args = parser.parse_args()

    # Collect all sections
    md_files = sorted(PROMPTS_DIR.glob("*.md"))
    if not md_files:
        logger.error("No .md files found in %s", PROMPTS_DIR)
        sys.exit(1)

    all_sections = []
    for md_file in md_files:
        domain = md_file.stem
        content = md_file.read_text()
        sections = split_by_headers(content, domain)
        all_sections.extend(sections)
        logger.info("  %s: %d sections", domain, len(sections))

    logger.info("Total: %d sections from %d domains", len(all_sections), len(md_files))

    if args.dry_run:
        print("\n=== DRY RUN -- sections that would be embedded ===\n")
        for s in all_sections:
            print(f"  {s['domain']:>40}::{s['section_title']:<50} ({s['token_count']} tokens)")
        print(f"\nTotal: {len(all_sections)} sections")
        return

    # Load model
    logger.info("Loading sentence-transformer model: %s", MODEL_NAME)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME)

    # Generate embeddings
    logger.info("Generating embeddings for %d sections...", len(all_sections))
    texts = [s["content"] for s in all_sections]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    logger.info("Embeddings generated: shape %s", embeddings.shape)

    # Upload to Supabase
    from backend.db.client import get_supabase
    db = get_supabase()

    if args.clear:
        logger.info("Clearing existing research_sections...")
        db.table("research_sections").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        logger.info("Cleared.")

    logger.info("Uploading %d sections to Supabase...", len(all_sections))
    batch_size = 20
    for i in range(0, len(all_sections), batch_size):
        batch = []
        for j in range(i, min(i + batch_size, len(all_sections))):
            section = all_sections[j]
            batch.append({
                "domain": section["domain"],
                "section_title": section["section_title"],
                "content": section["content"],
                "token_count": section["token_count"],
                "embedding": embeddings[j].tolist(),
            })
        db.table("research_sections").insert(batch).execute()
        logger.info("  Uploaded %d/%d", min(i + batch_size, len(all_sections)), len(all_sections))

    logger.info("Done. %d sections embedded and uploaded.", len(all_sections))


if __name__ == "__main__":
    main()
