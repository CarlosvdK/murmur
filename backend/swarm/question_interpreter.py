"""
Question Interpreter -- analyses the user's question in business context
before the simulation runs.

Solves the "wine pricing at a restaurant" problem: the raw question
"increase wine quality and prices" gets misinterpreted as "is this a wine
business?" when it should be "will diners accept higher wine prices?"

This module adds ONE Claude API call before persona generation that:
1. Interprets the question in business context
2. Identifies what product/service is affected
3. Estimates what % of customers are affected
4. Provides search queries for targeted research
5. Frames the question correctly for personas
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from anthropic import AsyncAnthropic
from backend.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "question_interpretation.txt"


@dataclass
class QuestionInterpretation:
    """Structured interpretation of the user's question."""
    original_question: str
    interpreted_question: str
    question_type: str = "other"
    affected_product: str = ""
    is_core_product: bool = True
    estimated_affected_customers_pct: int = 100
    market_search_queries: list[str] = field(default_factory=list)
    key_context_for_personas: str = ""
    null_hypothesis: str = "No change"
    framing_instruction: str = ""


async def interpret_question(
    question: str,
    business_name: str,
    business_type: str,
    survey_context: str,
) -> Optional[QuestionInterpretation]:
    """Interpret the user's question in the context of their business.

    Makes one Claude API call. Returns None on failure (non-fatal).
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        return None

    try:
        template = PROMPT_PATH.read_text()
    except FileNotFoundError:
        logger.error("Question interpretation prompt template not found")
        return None

    prompt = template.replace("{{question}}", question)
    prompt = prompt.replace("{{business_name}}", business_name)
    prompt = prompt.replace("{{business_type}}", business_type)
    prompt = prompt.replace("{{survey_context}}", survey_context[:4000])

    try:
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model=settings.model_name,
            max_tokens=800,
            system=(
                "You are a business analyst preparing a customer simulation. "
                "Return ONLY valid JSON. No markdown, no explanation."
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)

        interpretation = QuestionInterpretation(
            original_question=question,
            interpreted_question=data.get("interpreted_question", question),
            question_type=data.get("question_type", "other"),
            affected_product=data.get("affected_product", ""),
            is_core_product=data.get("is_core_product", True),
            estimated_affected_customers_pct=data.get("estimated_affected_customers_pct", 100),
            market_search_queries=data.get("market_search_queries", []),
            key_context_for_personas=data.get("key_context_for_personas", ""),
            null_hypothesis=data.get("null_hypothesis", "No change"),
            framing_instruction=data.get("framing_instruction", ""),
        )

        logger.info(
            "Question interpreted: type=%s, affected=%s, core=%s, customers=%d%%",
            interpretation.question_type,
            interpretation.affected_product,
            interpretation.is_core_product,
            interpretation.estimated_affected_customers_pct,
        )

        return interpretation

    except Exception as e:
        logger.warning("Question interpretation failed (non-fatal): %s", e)
        return None
