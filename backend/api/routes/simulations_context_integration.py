"""
Integration guide: Wiring context intelligence into _run_pipeline.

This module shows the exact changes needed to wire LocationProfiler and
RealtimeIntelligence into the simulation pipeline.

Changes are NON-BLOCKING and GRACEFUL: if APIs fail, simulation continues.
"""

# ============================================================================
# CHANGES TO simulations.py
# ============================================================================

# At the top of the file, add imports:
"""
from backend.context.location_profiler import LocationProfiler, LocationProfile
from backend.context.realtime_intelligence import RealtimeIntelligence, RealtimeContext
"""

# In _run_pipeline, after line 558 (after gather_context call), add:
"""
        # Step 0.3: Gather location profile + real-time context (NEW)
        location_profile = None
        realtime_context = None

        try:
            # Extract customer location from workspace data or business location
            customer_location = (workspace_data or {}).get("customer_location") or business.location

            # Initialize profilers
            db = get_supabase()
            cache = None  # Could use Redis cache here

            profiler = LocationProfiler(db=db, cache=cache)
            intelligence = RealtimeIntelligence(cache=cache)

            # Gather location profile (cached quarterly) + real-time context (cached hourly)
            # in parallel, non-blocking
            async def gather_location_and_realtime():
                tasks = [
                    profiler.get_or_create(customer_location),
                    intelligence.gather_all(
                        location=customer_location,
                        simulation_date=datetime.now(timezone.utc),
                    ),
                ]
                results = await asyncio.gather(
                    *tasks,
                    return_exceptions=True,
                    timeout=3.0,  # 3 second timeout
                )
                return results[0] if not isinstance(results[0], Exception) else None, \
                       results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None

            location_profile, realtime_context = await gather_location_and_realtime()

            if location_profile:
                logger.info(
                    "Location profile: %s, inflation=%.1f%%, trust=%s",
                    location_profile.country_code,
                    location_profile.inflation_rate,
                    location_profile.trust_in_institutions,
                )
                _update_sim(sim_id, location_profile=location_profile.model_dump())

            if realtime_context:
                logger.info(
                    "Real-time context: temp=%.0f°C, sentiment=%.2f, payday_week=%s",
                    realtime_context.weather_temp,
                    realtime_context.social_sentiment_score,
                    realtime_context.is_payday_week,
                )
                _update_sim(sim_id, realtime_context=realtime_context.model_dump())

        except Exception as e:
            logger.warning("Location/realtime context gathering failed (non-fatal): %s", e)
            # Continue without this context - non-blocking


        # MODIFY the enriched_parts assembly (around line 586) to include location + realtime:
        enriched_parts = []
        if survey_context:
            enriched_parts.append(survey_context)
        if profile_context:
            enriched_parts.append(profile_context)
        if research_context:
            enriched_parts.append(research_context[:6000])
        if context_narrative:
            enriched_parts.append(context_narrative)

        # NEW: Add location intelligence
        if location_profile:
            location_intel = f\"\"\"LOCATION INTELLIGENCE (Customer Base):
Country: {location_profile.country_code}
Timezone: {location_profile.timezone}
Cultural Profile (Hofstede):
  - Power Distance: {location_profile.hofstede.get('pdist', '?')}/100 (authority matters)
  - Individualism: {location_profile.hofstede.get('idv', '?')}/100 (vs collective)
  - Uncertainty Avoidance: {location_profile.hofstede.get('uai', '?')}/100 (risk tolerance)

Economic Context:
  - Inflation: {location_profile.inflation_rate:.1f}% annually
  - Unemployment: {location_profile.unemployment_rate:.1f}%
  - Interest Rates: {location_profile.interest_rate:.1f}%
  - GDP Growth: {location_profile.gdp_growth_rate:.1f}%

Business Context:
  - Primary Payment: {location_profile.primary_payment}
  - Digital Adoption: {location_profile.digital_adoption}
  - Trust in Institutions: {location_profile.trust_in_institutions}
  - Communication Style: {'High-context (indirect)' if location_profile.context_culture == 'high' else 'Low-context (direct)'}
\"\"\"
            enriched_parts.append(location_intel)

        # NEW: Add real-time context
        if realtime_context:
            realtime_intel = f\"\"\"REAL-TIME CONTEXT (Today):
Weather: {realtime_context.weather_temp:.0f}°C, {realtime_context.weather_condition}
Forecast: {realtime_context.weather_forecast_7d}

Temporal:
  - Day: {realtime_context.day_of_week}
  - Time: {realtime_context.time_of_day}
  - Is Holiday: {realtime_context.is_holiday}
  - Is Payday Week: {realtime_context.is_payday_week}

Economic News:
{chr(10).join(f'  - {news}' for news in realtime_context.economic_news[:3]) if realtime_context.economic_news else '  - No major economic news'}

Sentiment: {realtime_context.social_sentiment_score:.2f} (-1=very negative, 0=neutral, 1=very positive)

Trending Topics: {', '.join(realtime_context.trending_topics[:3]) if realtime_context.trending_topics else 'None'}

Upcoming Events: {', '.join(realtime_context.upcoming_events[:2]) if realtime_context.upcoming_events else 'None'}
\"\"\"
            enriched_parts.append(realtime_intel)

        # END OF NEW CODE - rest of assembly continues as before
        if interpretation and interpretation.key_context_for_personas:
            enriched_parts.append(
                f"QUESTION CONTEXT:\\n{interpretation.key_context_for_personas}\\n"
                f"Framing: {interpretation.framing_instruction}"
            )
        if enriched_parts:
            context_narrative = "\\n\\n---\\n\\n".join(enriched_parts)
"""

# ============================================================================
# PERSONA GENERATION: No changes needed!
# ============================================================================
# The existing code at line 642+ continues as-is:
# personas, personas_generated = await get_or_create_archetype(...)
#
# The archetype system is completely separate. Context flows into prompts,
# personas are cached independently.


# ============================================================================
# DATABASE SCHEMA CHANGES (optional, for persistence)
# ============================================================================
"""
-- Add these columns to simulations table if you want to persist context data:

ALTER TABLE simulations ADD COLUMN IF NOT EXISTS location_profile JSONB;
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS realtime_context JSONB;

-- Create location_profiles cache table (if using DB-backed caching):

CREATE TABLE IF NOT EXISTS location_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location VARCHAR(255) UNIQUE NOT NULL,
    country_code VARCHAR(2),
    timezone VARCHAR(100),
    data JSONB,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_location_profiles_location ON location_profiles(location);
CREATE INDEX idx_location_profiles_expires ON location_profiles(expires_at);
"""


# ============================================================================
# EXPECTED OUTPUT IN PERSONA RESPONSES
# ============================================================================
"""
When a persona (e.g., Ahmad from Tehran) is interviewed, the context is injected
into the system prompt. The response should reflect:

1. Location-specific behavior:
   - High power distance (68) → respects authority, owner's decision matters
   - Low individualism (41) → family/collective decisions
   - High uncertainty avoidance (59) → prefers familiar brands

2. Economic context:
   - 42% inflation → EXTREME price sensitivity
   - Low trust in institutions → skeptical of business motives
   - Cash-first payment → digital adoption low

3. Real-time context:
   - Payday week → spending slightly higher
   - Ramadan starts → daytime fasting affects visiting patterns
   - Social sentiment negative → customers anxious about future

Result: Ahmad's response sounds like THIS:

"Coffee is already expensive. Everything costs so much now. Before the
crisis it was cheaper. I understand you need to make money, but please
don't price us out.

15% more? That's a lot. I'd think about going to the cheaper place next
door. Maybe come once a week instead of three times.

But... if you keep the quality and treat us well, maybe it's okay. You
have been honest with me for years. So perhaps I stay.

Just don't raise it again next month, yes? We're all suffering with the
prices."

NOT like this (generic response without context):

"This seems like a reasonable price increase given the market. I would
likely accept it and continue visiting."

The location + realtime context transforms generic personas into
realistic customer reactions grounded in real-world constraints.
"""
