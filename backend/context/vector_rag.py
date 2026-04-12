"""
Vector RAG -- semantic search across research article sections.

Uses sentence-transformers to embed the user's question, then queries
Supabase pgvector for the most relevant research sections. Returns
concatenated context ready for prompt injection.

Falls back to the keyword-based rag_selector if pgvector is unavailable.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-loaded model singleton
_model = None
_model_loading = False


def _get_model():
    """Load sentence-transformer model (lazy singleton, ~400MB, ~10s first load)."""
    global _model, _model_loading
    if _model is not None:
        return _model
    if _model_loading:
        return None  # prevent re-entrant loading
    try:
        _model_loading = True
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformer model: all-mpnet-base-v2")
        _model = SentenceTransformer("all-mpnet-base-v2")
        logger.info("Model loaded successfully")
        return _model
    except ImportError:
        logger.warning("sentence-transformers not installed -- vector RAG unavailable")
        return None
    except Exception as e:
        logger.error("Failed to load sentence-transformer model: %s", e)
        return None
    finally:
        _model_loading = False


async def search_research(
    question: str,
    business_type: str = "",
    max_sections: int = 10,
    max_chars: int = 6000,
    similarity_threshold: float = 0.35,
) -> Optional[dict]:
    """Semantic search across all research sections in Supabase.

    Returns dict with:
    - context: str (concatenated relevant sections)
    - sections_used: list of {domain, title, similarity}
    - total_chars: int
    - method: "vector_search"

    Returns None if vector search is unavailable (falls back to keyword selector).
    """
    model = _get_model()
    if model is None:
        return None

    # Encode the question
    try:
        # Combine question with business type for better matching
        search_text = question
        if business_type:
            search_text = f"{business_type} business: {question}"
        embedding = model.encode(search_text).tolist()
    except Exception as e:
        logger.error("Failed to encode question: %s", e)
        return None

    # Query Supabase
    try:
        from backend.db.client import get_supabase
        db = get_supabase()

        result = db.rpc("match_research_sections", {
            "query_embedding": embedding,
            "match_count": max_sections * 2,  # fetch extra, filter by char limit
            "similarity_threshold": similarity_threshold,
        }).execute()

        if not result.data:
            logger.info("Vector search returned no results above threshold %.2f", similarity_threshold)
            return None

        # Assemble context from top matches, respecting char limit
        sections = []
        total_chars = 0
        for row in result.data:
            content_len = len(row.get("content", ""))
            if total_chars + content_len > max_chars:
                if not sections:  # always include at least one
                    sections.append(row)
                    total_chars += content_len
                break
            sections.append(row)
            total_chars += content_len

        # Build context string with section labels
        context_parts = []
        for s in sections:
            label = f"[{s['domain']}::{s['section_title']}] (relevance: {s['similarity']:.0%})"
            context_parts.append(f"{label}\n{s['content']}")

        context = "\n\n---\n\n".join(context_parts)

        sections_meta = [
            {
                "domain": s["domain"],
                "title": s["section_title"],
                "similarity": round(s["similarity"], 3),
            }
            for s in sections
        ]

        logger.info(
            "Vector RAG: %d sections, %d chars, top match: %s (%.0f%%)",
            len(sections),
            total_chars,
            sections_meta[0]["title"] if sections_meta else "none",
            sections_meta[0]["similarity"] * 100 if sections_meta else 0,
        )

        return {
            "context": context,
            "sections_used": sections_meta,
            "total_chars": total_chars,
            "method": "vector_search",
        }

    except Exception as e:
        logger.warning("Vector RAG query failed (falling back to keyword): %s", e)
        return None


async def search_research_with_fallback(
    question: str,
    business_type: str = "",
    country_code: str = "",
    max_chars: int = 6000,
) -> dict:
    """Try vector search first, fall back to keyword-based selector.

    Always returns a dict with context string.
    """
    # Try vector search
    result = await search_research(question, business_type, max_chars=max_chars)

    if result and result.get("context"):
        return result

    # Fall back to keyword-based selector
    logger.info("Falling back to keyword-based RAG selector")
    try:
        from research.rag_library import get_simulation_context
        context = get_simulation_context(
            country_code=country_code or "DEFAULT",
            business_type=business_type,
            question=question,
        )
        return {
            "context": context[:max_chars] if context else "",
            "sections_used": [],
            "total_chars": len(context[:max_chars]) if context else 0,
            "method": "keyword_fallback",
        }
    except Exception as e:
        logger.error("Both vector and keyword RAG failed: %s", e)
        return {
            "context": "",
            "sections_used": [],
            "total_chars": 0,
            "method": "failed",
        }
