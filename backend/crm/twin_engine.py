"""
Twin Engine -- answers questions about a contact based on their communication profile.

This is a PREPARATION tool, not a prediction tool.
Every response includes confidence and caveats.
"""

import json
import logging
from typing import Optional

from anthropic import AsyncAnthropic
from backend.config import get_settings

logger = logging.getLogger(__name__)

TWIN_SYSTEM_PROMPT = """You are Murmur's relationship intelligence engine.
You have been given anonymised communication pattern data for a specific
professional contact. Your job is to help the user prepare for their next
interaction with this person.

IMPORTANT FRAMING:
- This is a PREPARATION tool, not a prediction tool
- You are helping the user prepare, not deciding for them
- Every response must include a confidence indicator
- Every response must acknowledge what you don't know
- Never claim certainty about a person's internal state
- Frame outputs as "based on the pattern in your history"

COMMUNICATION PROFILE:
{profile}

When answering:
1. Lead with the direct answer
2. Cite specific patterns from the communication data
3. Name the uncertainty clearly
4. Give concrete preparation recommendations
5. End with confidence level: High/Medium/Low

Return JSON:
{{
  "answer": "full response text -- direct, practical, specific",
  "key_signals": ["signal from the data that supports this answer"],
  "preparation_tips": ["concrete thing to do before the conversation"],
  "confidence": "high|medium|low",
  "confidence_reason": "why this confidence level",
  "caveats": ["what we don't know", "what could be different"]
}}"""


async def query_twin(
    question: str,
    contact_name: str,
    extracted_signals: dict,
    recent_activities: Optional[list[dict]] = None,
) -> dict:
    """Ask a question about a contact's likely behaviour.

    Returns a structured response with answer, confidence, and caveats.
    """
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    # Build profile from extracted signals
    profile_parts = [f"Contact: {contact_name}"]

    if extracted_signals.get("communication_style"):
        profile_parts.append(f"Communication style: {extracted_signals['communication_style']}")
    if extracted_signals.get("formality_level") is not None:
        profile_parts.append(f"Formality level: {extracted_signals['formality_level']}/10")
    if extracted_signals.get("avg_response_hours"):
        profile_parts.append(f"Average response time: {extracted_signals['avg_response_hours']:.0f} hours")
    if extracted_signals.get("typical_response_style"):
        profile_parts.append(f"Typical response: {extracted_signals['typical_response_style']}")
    if extracted_signals.get("decision_patterns"):
        profile_parts.append(f"Decision patterns: {', '.join(extracted_signals['decision_patterns'])}")
    if extracted_signals.get("objection_patterns"):
        profile_parts.append(f"Typical objections: {', '.join(extracted_signals['objection_patterns'])}")
    if extracted_signals.get("what_matters_most"):
        profile_parts.append(f"What matters most: {', '.join(extracted_signals['what_matters_most'])}")
    if extracted_signals.get("topic_themes"):
        profile_parts.append(f"Common topics: {', '.join(extracted_signals['topic_themes'])}")
    if extracted_signals.get("message_count"):
        profile_parts.append(f"Based on: {extracted_signals['message_count']} messages")

    profile = "\n".join(profile_parts)

    system = TWIN_SYSTEM_PROMPT.replace("{profile}", profile)

    response = await client.messages.create(
        model=settings.model_name,
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": question}],
    )

    raw = response.content[0].text.strip()

    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "answer": raw[:500],
            "key_signals": [],
            "preparation_tips": [],
            "confidence": "low",
            "confidence_reason": "Response parsing failed",
            "caveats": ["This response may not be fully structured"],
        }

    logger.info(
        "Twin query for %s: confidence=%s",
        contact_name, result.get("confidence", "unknown"),
    )

    return result
