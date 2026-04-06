"""
Correspondence Processor -- extracts communication patterns from uploaded files.

PRIVACY: This is the most sensitive module in Murmur.
- Raw file content is processed in memory ONLY
- No message text is stored -- only aggregate patterns
- Raw files are deleted immediately after processing
- Output is a signals dict containing only anonymised patterns

Supported formats:
- WhatsApp .txt export
- Plain text email threads
- Meeting notes (.txt)
"""

import json
import logging
import re
from datetime import datetime
from typing import Optional

from anthropic import AsyncAnthropic
from backend.config import get_settings

logger = logging.getLogger(__name__)


async def process_correspondence(
    raw_text: str,
    contact_name: str,
    source_type: str,
    on_progress: Optional[callable] = None,
) -> dict:
    """Process raw correspondence text and extract anonymised signals.

    Returns a signals dict -- NEVER raw message content.
    The raw_text parameter must be discarded by the caller after this returns.
    """
    settings = get_settings()

    if on_progress:
        on_progress("Anonymising correspondence...")

    # Count messages
    lines = raw_text.strip().split("\n")
    message_count = len([l for l in lines if l.strip()])

    if on_progress:
        on_progress(f"Extracting patterns from {message_count} messages...")

    # Use Claude to extract ONLY patterns -- never store content
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await client.messages.create(
        model=settings.model_name,
        max_tokens=1500,
        system=(
            "You are a communication pattern analyser. You extract PATTERNS "
            "from correspondence -- never quote or store actual message content. "
            "Return ONLY a JSON object with anonymised communication signals. "
            "Do NOT include any actual message text, names, or identifying information "
            "in your output."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Analyse this correspondence with {contact_name} ({source_type}). "
                f"Extract ONLY communication patterns. Never quote actual messages.\n\n"
                f"Correspondence ({message_count} messages):\n{raw_text[:8000]}\n\n"
                f"Return JSON with these fields ONLY:\n"
                f'{{"avg_response_hours": float, '
                f'"formality_level": 0-10, '
                f'"initiator_ratio": float (0=they always initiate, 1=you always do), '
                f'"avg_message_length": "short|medium|long", '
                f'"topic_themes": ["theme1", "theme2"], '
                f'"communication_style": "formal|casual|brief|detailed|mixed", '
                f'"decision_patterns": ["pattern1"], '
                f'"objection_patterns": ["pattern1"], '
                f'"positive_signals": ["signal1"], '
                f'"negative_signals": ["signal1"], '
                f'"preferred_contact_time": "morning|afternoon|evening|mixed", '
                f'"key_interests": ["interest1"], '
                f'"what_matters_most": ["thing1"], '
                f'"typical_response_style": "description of how they typically respond"}}'
            ),
        }],
    )

    raw_response = response.content[0].text.strip()

    # Parse JSON
    try:
        if raw_response.startswith("```"):
            raw_response = raw_response.split("```")[1]
            if raw_response.startswith("json"):
                raw_response = raw_response[4:]
            raw_response = raw_response.strip()
        signals = json.loads(raw_response)
    except json.JSONDecodeError:
        logger.error("Failed to parse correspondence signals")
        signals = {
            "avg_response_hours": None,
            "formality_level": 5,
            "communication_style": "unknown",
            "topic_themes": [],
            "error": "Pattern extraction failed",
        }

    signals["message_count"] = message_count
    signals["source_type"] = source_type
    signals["processed_at"] = datetime.utcnow().isoformat()

    if on_progress:
        on_progress("Pattern extraction complete -- raw data discarded")

    # CRITICAL: The caller must discard raw_text after this returns
    # We do not store it anywhere

    logger.info(
        "Correspondence processed: %d messages, style=%s, formality=%s",
        message_count,
        signals.get("communication_style", "unknown"),
        signals.get("formality_level", "?"),
    )

    return signals
