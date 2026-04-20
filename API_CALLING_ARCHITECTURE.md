# API Calling Architecture: Comprehensive Analysis

**Status:** Production design for 1000+ context dimensions  
**Date:** April 2026  
**Purpose:** Deep dive into context intelligence API patterns and implementation

---

## Executive Summary

Current system (v0.1): 8 tools gathering ~15 context signals in 90 seconds.

Proposed system (v1.0): Parallel API gathering covering 1000+ dimensions across 12 categories, non-blocking with cached fallbacks.

**Key principle:** Shallow & broad > deep & narrow. Collect as many signals as possible in parallel, cache aggressively, never block the user.

---

## Part 1: Current API Pattern (Baseline)

### Current Flow (simulations.py:_run_pipeline)

```
1. gather_context(business, question) → BusinessContext
   - Orchestrator (Claude) decides which tools to run
   - 8 tools run in parallel (asyncio.gather), 30s timeout each, 90s hard limit
   - Results filtered into narrative string via relevance filter

2. Tools called:
   - web_search (Brave) → general market context
   - google_places → local business reviews
   - news_search (Brave) → recent events
   - price_index → CPI/inflation
   - weather_trends → current/forecast
   - demographic → population data
   - review_analyzer → review sentiment
   - social_sentiment (Reddit) → community sentiment

3. Output: filtered_narrative (plain text string)
   - ~500-2000 chars
   - Injected into persona generation prompt

4. Graceful degradation:
   - If tools fail, continue with empty context
   - No blocking failures
```

### Problems with Current Design

1. **Too sequential**: Orchestrator makes ONE decision, then gathers. Could parallelize the decision-making.
2. **Too narrow**: 8 tools gather ~15 signals. Missing 985 signals.
3. **No persistence**: Each question re-gathers same data. No caching between questions.
4. **No temporal awareness**: Weather from 3 hours ago. Economic data from last quarter. Not real-time.
5. **No deep regional context**: Iran customer = generic "Middle East" context. Missing Iran-specific inflation (42%), currency volatility, etc.
6. **Binary filtering**: Narrative is filtered to readable text. Loses granular signal strength.
7. **No structural output**: Results come back as unstructured prose. Hard to measure calibration.

---

## Part 2: Proposed Architecture (1000+ Dimensions)

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│  Simulation Kick-off (business, question)               │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   ┌────────────┐      ┌─────────────────┐
   │ Cache Hit? │      │ Question Topic  │
   │            │      │ Analysis        │
   └────────────┘      └─────────────────┘
        │                     │
        │ (cached)            │ (fresh needed?)
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  Parallel API Gathering  │
        │  (non-blocking, 200 APIs)│
        └─────────┬────────────────┘
                  │
   ┌──────────────┼──────────────┐
   │              │              │
   ▼              ▼              ▼
Group 1       Group 2       Group 3
Macro Econ    Micro Local   Behavioral
(50 APIs)     (40 APIs)     (50 APIs)
   │              │              │
   └──────────────┼──────────────┘
                  │
                  ▼
        ┌──────────────────────┐
        │ Aggregate Results    │
        │ (raw signal capture) │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Inject into Prompts  │
        │ (persona + aggreg.)  │
        └──────────────────────┘
```

### The 1000 Dimensions: Organized by Category

#### Category 1: Macroeconomic (80 dimensions)

**Current APIs:**
- World Bank API (inflation, unemployment, GDP)
- FRED (Federal Reserve) (interest rates, employment)
- Trading Economics API (CPI, PMI, unemployment)
- OpenFIGI (commodity prices: oil, gas, metals)

**New API integrations:**
- IMF API (IMF outlook, crisis indicators)
- OECD Stats (advanced economies specific)
- Yahoo Finance (stock market sentiment)
- CoinGecko (crypto market sentiment as risk indicator)
- Eurostat (EU-specific inflation, regulations)

**Signals captured:**
```python
MACRO_SIGNALS = {
    "inflation": [CPI_overall, CPI_food, CPI_energy, CPI_housing, 
                  PPI, core_inflation, inflation_expectation],
    "commodities": [oil_price, oil_trend, gas_price, metals_index, 
                    copper, wheat, gold, freight_index],
    "currency": [exchange_rate, volatility_7d, volatility_30d, 
                 REER, capital_flows, forex_reserves],
    "rates": [policy_rate, prime_rate, mortgage_rate, credit_card_rate,
              yield_curve, credit_spread, real_interest_rate],
    "debt": [govt_debt_gdp, corporate_debt, household_debt, 
             NPL_ratio, delinquency_rates],
    "activity": [gdp_growth, industrial_production, PMI_manuf, PMI_services,
                 retail_sales, capacity_utilization],
    "employment": [unemployment_rate, U6, labor_participation, job_creation,
                   wage_growth, job_quits, job_openings],
    "business": [business_confidence, consumer_confidence, new_businesses, 
                 bankruptcy_rate, profit_margins],
}
```

#### Category 2: Micro-Location Economics (70 dimensions)

**Current APIs:**
- Google Maps/Places (limited)

**New API integrations:**
- Zillow/Redfin API (local real estate)
- Census Bureau API (local demographics)
- LinkedIn Economic Graph (local job market)
- Numbeo (local cost of living)
- Indeed API (local job postings/wage data)
- OpenWeatherMap (hyperlocal, not global)
- Local tax databases (sales tax, property tax by ZIP)

**Signals captured (hyperlocal, down to ZIP code level):**
```python
MICRO_SIGNALS = {
    "labor": [local_unemployment, local_wages_by_job, local_min_wage,
              job_market_tightness, worker_scarcity, remote_work_pct],
    "realestate": [house_price_trend, rental_trend, vacancy_rate,
                   construction_permits, foreclosure_rate, property_tax],
    "taxes": [sales_tax_rate, income_tax_rate, property_tax, 
              corporate_tax, unemployment_tax],
    "infrastructure": [avg_commute, internet_speed, public_transit,
                       utility_costs, broadband_availability],
    "competitive": [business_density, new_openings, closures, 
                    avg_business_age, chain_vs_independent_ratio],
    "population": [population_growth, age_distribution, income_distribution,
                   education_levels, ethnic_diversity],
}
```

#### Category 3: Sentiment & Behavioral (120 dimensions)

**Current APIs:**
- Reddit (via PRAW)
- Google Trends (via SerpAPI)

**New API integrations:**
- Twitter API v2 (real-time sentiment)
- SurveyMonkey API (consumer confidence surveys)
- Slack (if B2B customer base)
- TikTok API (Gen Z sentiment)
- YouTube (content engagement)
- Google Trends (now with category filtering)
- News APIs (sentiment of published news)
- Glassdoor (employee sentiment, used to infer business trust)

**Signals captured:**
```python
SENTIMENT_SIGNALS = {
    "consumer": [consumer_confidence_score, optimism_index, 
                 anxiety_level, aspirational_intent],
    "national": [national_sentiment_score, fear_index, pride_level,
                 trust_in_institutions],
    "psychographics": [openness, conscientiousness, extraversion, 
                       agreeableness, neuroticism],  # via text analysis
    "anxiety": [economic_anxiety_score, job_security_anxiety,
                inflation_worry, recession_fear],
    "aspiration": [wealth_aspiration, status_aspiration,
                   family_aspiration, career_aspiration],
    "trust": [trust_banks, trust_government, trust_business,
              trust_media, trust_neighbors],
    "social_influence": [trend_follower_pct, early_adopter_pct,
                         conformity_score, opinion_leader_exposure],
}
```

#### Category 4: News, Information & Media (100 dimensions)

**Current APIs:**
- Brave News

**New API integrations:**
- Google News API (with filtering)
- NewsAPI (global news coverage)
- CNN/Reuters/BBC RSS feeds (parody for parsing)
- Hacker News API (tech/startup sentiment)
- Product Hunt API (new product launches)
- Reddit API (topic popularity)
- Wikipedia API (trending topics)
- Event databases (major announcements)

**Signals captured:**
```python
NEWS_SIGNALS = {
    "news_landscape": [total_articles_last_24h, article_volume_trend,
                       topics_trending_now, sentiment_of_top_stories],
    "industry": [industry_specific_news_count, positive_stories_ratio,
                 regulatory_announcements, competitor_mentions],
    "local": [local_news_volume, local_positive_stories,
              local_problems_reported, local_business_openings],
    "viral": [trending_hashtags, viral_videos, meme_sentiment,
              influencer_mentions],
    "social_media": {
        "twitter": [tweet_volume, sentiment_score, trending_topics,
                    mention_volume],
        "tiktok": [video_views, engagement_rate, creator_mentions],
        "reddit": [subreddit_mentions, upvote_ratio, comment_sentiment],
        "instagram": [post_engagement, hashtag_trends, influencer_sentiment],
        "linkedin": [professional_sentiment, hiring_optimism, layoff_news],
        "youtube": [video_views, comment_sentiment, creator_engagement],
        "discord": [community_discussions, sentiment_in_servers],
    },
    "information_literacy": [misinformation_prevalence, fact_check_trends,
                             media_trust_score, echo_chamber_strength],
}
```

#### Category 5: Health & Safety (60 dimensions)

**Current APIs:** None

**New API integrations:**
- CDC API (disease prevalence)
- WHO API (global health)
- Crime databases (local crime stats)
- OSHA data (workplace safety)
- FDA alerts (product safety)
- Pollution APIs (air quality, water quality)
- Flu tracking APIs
- COVID tracking (if relevant)

**Signals captured:**
```python
HEALTH_SIGNALS = {
    "pandemic": [covid_cases_trend, vaccination_rate, hospitalizations,
                 death_rate, variant_prevalence],
    "disease": [flu_prevalence, outbreak_news, disease_spread_rate],
    "mental_health": [depression_prevalence, anxiety_prevalence,
                      suicide_rate_trend, mental_health_resource_demand],
    "safety": [crime_rate_local, violent_crime_trend, safety_perception],
    "workplace_safety": [injury_rate, OSHA_violations, worker_compensation],
    "product_safety": [FDA_recalls, product_defect_news, safety_concerns],
    "environmental": [air_quality_index, water_quality, pollution_level,
                      natural_disaster_risk],
}
```

#### Category 6: Weather & Climate (60 dimensions)

**Current APIs:**
- OpenWeatherMap

**Signals captured:**
```python
WEATHER_SIGNALS = {
    "current": [temperature, humidity, wind_speed, conditions,
                UV_index, visibility, pressure],
    "forecast": [7day_forecast, temp_range, precipitation_chance,
                 extreme_weather_alert, seasonal_anomaly],
    "seasonal": [season_in_region, is_normal_for_season, anomaly_score,
                 daylight_hours, snowfall_risk],
    "climate": [long_term_trend, warming_anomaly, drought_risk,
                flood_risk, hurricane_risk, wildfire_risk],
    "impact_on_behavior": [shopping_trip_likelihood, indoor_vs_outdoor_pref,
                           clothing_purchase_likelihood, food_preference_shift],
}
```

#### Categories 7-12: (Industry, Culture, Competitive, Financial, Personal, Temporal)

Similar expansion pattern: each category has 20-50 data APIs integrated.

---

## Part 3: Implementation: The Context Intelligence Engine

### Pseudo-Code Architecture

```python
class ContextIntelligenceEngine:
    """Gathers 1000+ context signals in parallel, non-blocking."""
    
    async def gather_all_context(
        self,
        business: BusinessSnapshot,
        customer_location: str,  # e.g., "Tehran, Iran"
        business_location: str,
        question: str,
        simulation_date: datetime = None,
        cache_ttl: dict = None,  # granular by category
    ) -> FullContextSnapshot:
        """
        Returns FullContextSnapshot with all 1000+ dimensions.
        
        Logic:
        1. Check location profiles cache (updated quarterly)
        2. Kick off 12 parallel category gatherers (non-blocking)
        3. Each gatherer hits 15-50 APIs in parallel
        4. Cache results by category and TTL
        5. Return immediately with whatever completed
        6. UI shows completion % as data streams in
        """
        
        # Phase 1: Fast cache lookups (50ms)
        location_profile = await self.location_profiler.get_or_create(
            customer_location,  # cached quarterly
        )
        
        # Phase 2: Kick off 12 parallel gatherers (non-blocking)
        tasks = [
            self._gather_macro_economic(customer_location, cache_ttl),
            self._gather_micro_local(customer_location, cache_ttl),
            self._gather_sentiment(customer_location, cache_ttl),
            self._gather_news(question, customer_location, cache_ttl),
            self._gather_health(customer_location, cache_ttl),
            self._gather_weather(customer_location, cache_ttl),
            self._gather_temporal(simulation_date, cache_ttl),
            self._gather_industry(business.industry, cache_ttl),
            self._gather_culture(customer_location, cache_ttl),
            self._gather_competitive(business, customer_location, cache_ttl),
            self._gather_financial(customer_location, cache_ttl),
            self._gather_personal(customer_location, cache_ttl),  # inferred
        ]
        
        # Parallel gather with 5s timeout per category
        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
            timeout=5.0,
        )
        
        # Phase 3: Assemble snapshot
        snapshot = FullContextSnapshot(
            timestamp=datetime.now(),
            macro=results[0],
            micro=results[1],
            sentiment=results[2],
            # ... etc
        )
        
        return snapshot


    async def _gather_macro_economic(
        self, location: str, cache_ttl: dict
    ) -> MacroEconomicContext:
        """Gather 80 macro signals in parallel."""
        
        apis_to_call = {
            "world_bank": [
                ("inflation", fetch_world_bank_inflation(location)),
                ("unemployment", fetch_world_bank_unemployment(location)),
                ("gdp_growth", fetch_world_bank_gdp(location)),
            ],
            "fed_api": [
                ("interest_rate", fetch_fed_interest_rate(location)),
                ("yield_curve", fetch_fed_yield_curve()),
            ],
            "trading_economics": [
                ("cpi", fetch_te_cpi(location)),
                ("pmi", fetch_te_pmi(location)),
                ("consumer_confidence", fetch_te_confidence(location)),
            ],
            "openfigi": [
                ("oil_price", fetch_oil_price()),
                ("commodity_index", fetch_commodity_index()),
                ("gold_price", fetch_gold_price()),
            ],
            # ... 50+ more APIs
        }
        
        # Run all in parallel, cache by category
        results = {}
        for category, calls in apis_to_call.items():
            cached = await self.cache.get(f"macro_{category}")
            if cached and not is_expired(cached, cache_ttl.get("macro", "daily")):
                results[category] = cached
            else:
                # Fetch in parallel
                cat_results = await asyncio.gather(
                    *[call for name, call in calls],
                    return_exceptions=True,
                    timeout=2.0,
                )
                results[category] = dict(zip([n for n, _ in calls], cat_results))
                await self.cache.set(f"macro_{category}", results[category], 
                                   ttl=cache_ttl.get("macro", "daily"))
        
        return MacroEconomicContext(**results)
```

### Cache Strategy (by category)

| Category | Update Frequency | Cache TTL | Cost |
|----------|------------------|-----------|------|
| Macro Economic | Daily | 24h | Free (World Bank) + $$ (Trading Economics) |
| Micro Location | Weekly | 7d | Free (Census) + $ (Zillow) |
| Sentiment | Hourly | 1h | $ (Twitter) + Free (Reddit) |
| News | Hourly | 1h | Free (NewsAPI) + $ (Bloomberg) |
| Health | Daily | 24h | Free (CDC, WHO) |
| Weather | Hourly | 1h | Free (Open-Meteo) |
| Temporal | Real-time | 5m | Calculated (no API) |
| Industry | Daily | 24h | Free (industry reports) |
| Culture | Quarterly | 90d | Free (Hofstede) |
| Competitive | Daily | 24h | $$ (market research APIs) |
| Financial | Daily | 24h | Free (World Bank) |
| Personal | Static | ∞ | Calculated from demo |

### Concrete Example: Iranian Customer

User: "I own a coffee shop in Tehran. What if I raise prices 15%?"

```
1. Location detection: Tehran, Iran
   ✓ Cached location profile instantly:
     - Country: IR, Timezone: Asia/Tehran
     - Culture: High power distance (68), collectivist (41),
       uncertainty avoidant (59), low trust in institutions
     - Language: Farsi, cash-first business
   
2. Macro Economic (kicked off in parallel):
   ✓ Iran inflation: 42% annually (vs 3% global)
   ✓ Currency volatility: Rial depreciating 5% this month
   ✓ Central bank policy: interest rates at 30%
   ✓ Unemployment: 8%, but youth unemployment 25%
   ✓ Business confidence: LOW (sanctions, uncertainty)
   
3. Micro Location (kicked off):
   ✓ Tehran cost of living: +18% last quarter
   ✓ Coffee shop density: HIGH (200+ coffee shops in central Tehran)
   ✓ Rent trends: +12% this year
   ✓ Average customer income: 2-3M Rial/month
   
4. Sentiment (kicked off):
   ✓ Consumer sentiment: ANXIOUS (economic uncertainty)
   ✓ Trust in business: LOW (expectations of price gouging)
   ✓ Price sensitivity: VERY HIGH (every 1% price increase discussed)
   
5. News (kicked off):
   ✓ Ramadan starts in 1 week → coffee shop traffic shifts
   ✓ Recent news: government wage increases announced
   ✓ Competitor news: nearby cafe raised prices 10% last week
   
6. Weather (kicked off):
   ✓ Current: 18°C, spring (warming trend)
   ✓ Ramadan impact: daytime fasting → evening coffee spikes
   
7. Temporal:
   ✓ Today: April 20, Sunday (not Friday weekend yet)
   ✓ This week: pre-Ramadan rush begins
   ✓ Payday cycle: Many employees paid monthly (start/end of month)

=== RESULT ===

Persona Injection:
"Ahmad, 34, daily customer: 'Coffee is now 15% more expensive? The Rial 
is worthless anyway, everything's getting expensive. But I come here 
because it's near work and the owner is honest. If you raise prices 
15%, I'd look elsewhere. Maybe come 2x/week instead of 3x.

My salary hasn't gone up. Food costs are up 20%. Why should I pay more 
for coffee? I can make coffee at home.

But... Ramadan is starting. I'll need more coffee during work hours 
to stay focused during fasting. So maybe I'll still come, just fewer 
days.'"

Probability: Ahmad accepts with conditions (60%)
- Conditions: No more than 1-2 times per week (down from 3-4)
- Acceptance contingent on: quality increase OR loyalty discount

Key insight that ONLY appeared because of Iran-specific context:
- 42% inflation + Ramadan + currency crisis + low trust =
  Price increase works SHORT-TERM (emergency behavior) but
  Damages LONG-TERM loyalty (customers think you're price gouging)
```

---

## Part 4: Error Handling & Graceful Degradation

### Principle: Never block, always degrade gracefully

```python
async def _gather_macro_economic(...):
    """If APIs fail, still proceed."""
    
    results = {}
    
    for api_name, api_call in all_calls:
        try:
            data = await asyncio.wait_for(
                api_call,
                timeout=2.0,  # Per-API timeout
            )
            results[api_name] = data
        except asyncio.TimeoutError:
            logger.warning(f"API timeout: {api_name}, using fallback")
            results[api_name] = get_cached_or_default(api_name)
        except Exception as e:
            logger.warning(f"API error: {api_name}: {e}, continuing")
            results[api_name] = get_cached_or_default(api_name)
    
    # Return partial results even if 30% failed
    if len(results) >= len(all_calls) * 0.7:
        return MacroEconomicContext(**results)
    else:
        logger.error("Too many API failures, using fully cached context")
        return get_fully_cached_context()
```

### Fallback Chain

```
1. Try fresh API call (2s timeout)
2. If fails, check Redis cache (24h TTL)
3. If missing, check database history (30d)
4. If missing, use sector default (e.g., "global average inflation")
5. If all missing, skip this dimension (non-fatal)
```

---

## Part 5: Data Quality & Bias Detection

### Signal Strength Scoring

Each signal gets a confidence score (0-1):

```python
signal_confidence = {
    "macro_inflation": 0.95,  # Published daily by central bank
    "micro_local_house_price": 0.70,  # Updated weekly, but lagged
    "sentiment_twitter": 0.50,  # Noisy, only 5% of population on Twitter
    "news_sentiment": 0.60,  # News is biased, not representative
    "my_calculation_from_demographics": 0.30,  # Inferred, not measured
}
```

When injecting into prompts:
```
"CONFIDENCE NOTE: Inflation is 42% (VERY HIGH confidence, from 
central bank). Customer sentiment is anxious (MEDIUM confidence, 
from Twitter/Reddit sample). House prices up 5% (LOW confidence, 
real estate market lags)."
```

### Bias Detection

```python
def detect_biases(context: FullContextSnapshot) -> dict:
    """Identify known biases in the context."""
    
    biases = {}
    
    # Bias 1: Social media overrepresents young, urban, educated
    if context.sentiment.data_source == "twitter":
        biases["demographic_bias"] = {
            "direction": "young, urban, educated overrepresented",
            "correction": "weight down youth sentiment, up elderly",
        }
    
    # Bias 2: Published news overrepresents negative
    if context.news.sentiment_score < -0.1:
        biases["negativity_bias"] = {
            "direction": "negative news overrepresented",
            "correction": "adjust sentiment +0.15",
        }
    
    # Bias 3: Macro data is lagged (monthly CPI, weekly unemployment)
    if context.macro.inflation_age_days > 7:
        biases["temporal_lag"] = {
            "direction": f"data is {context.macro.inflation_age_days} days old",
            "correction": f"apply trend extrapolation",
        }
    
    return biases
```

---

## Part 6: Testing & Validation

### Unit Tests for API Layers

```python
@pytest.mark.asyncio
async def test_macro_economic_api_gathering():
    """Verify macro APIs return expected structure."""
    engine = ContextIntelligenceEngine()
    result = await engine._gather_macro_economic(
        location="Tehran, Iran",
        cache_ttl={"macro": "daily"}
    )
    
    # Should have inflation data
    assert result.inflation.cpi_overall > 0
    assert result.inflation.cpi_food > result.inflation.cpi_overall
    
    # Should have confidence scores
    assert 0 <= result.inflation.confidence_score <= 1

@pytest.mark.asyncio
async def test_graceful_degradation_on_api_failure():
    """Verify system works even if 50% of APIs fail."""
    engine = ContextIntelligenceEngine(
        mock_failures={"world_bank": True, "fed": True}  # Force failures
    )
    
    result = await engine._gather_macro_economic(
        location="Tehran, Iran",
        cache_ttl={"macro": "daily"}
    )
    
    # Should still return data from non-failing APIs
    assert result.commodities.oil_price > 0  # OpenFIGI should work
    assert result.macro_score >= 0.5  # At least 50% coverage
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_context_gathering_iran_customer():
    """End-to-end: Iranian customer context gathering."""
    
    context = await engine.gather_all_context(
        business=BusinessSnapshot(name="Coffee Shop", type="cafe"),
        customer_location="Tehran, Iran",
        business_location="Tehran, Iran",
        question="What if I raise prices 15%?",
        simulation_date=datetime(2026, 4, 20),  # Start of Ramadan
    )
    
    # Should detect Iran economic crisis context
    assert context.macro.inflation.cpi_overall > 40
    assert context.location_profile.country_code == "IR"
    
    # Should detect Ramadan impact
    assert context.temporal.upcoming_event == "Ramadan"
    assert context.behavioral.daytime_activity_level == "low"
    
    # Should show very high price sensitivity
    assert context.sentiment.price_sensitivity_score > 0.8
```

---

## Part 7: Cost Optimization

### API Cost Breakdown (Monthly, 100K simulations)

| Source | Cost Model | Est. Cost | Notes |
|--------|-----------|-----------|-------|
| World Bank | Free | $0 | No rate limits |
| FRED | Free | $0 | No rate limits |
| Open-Meteo | Free | $0 | No rate limits |
| OpenFIGI | Free | $0 | Free commodity data |
| NewsAPI | Freemium | $50-100 | 100 requests/day free tier |
| Twitter API | Paid | $100-500 | Depends on volume |
| Google Trends | Free (via SerpAPI) | $50-100 | 100 requests/month free |
| CDC/WHO | Free | $0 | Government data |
| Trading Economics | Paid | $200-1000 | Advanced tier for PMI |
| Zillow/Redfin | Limited free | $200-500 | Free tier exhausted quickly |
| **Total** | | **~$600-2200/month** | Scales with usage |

### Cost Reduction Strategies

1. **Aggressive caching**: Each category cached for TTL (macro: 24h, news: 1h)
   - Avoids 80% of redundant API calls
   
2. **Batch mode**: Process 10 questions at once, cache all context once
   - Example: Small business owner asks 5 questions → gather context once, reuse

3. **Tiered gathering**: "Fast mode" (macro only), "Standard" (macro+sentiment), "Deep" (all)
   - User chooses mode, costs scale

4. **Geographic clustering**: Tehran customers share Iran macro context
   - Store at location level, not per-business level

**Cost per simulation at scale:**
- Aggressive caching + batching: ~$0.005-0.01 per simulation
- Without optimization: ~$0.05-0.1 per simulation

---

## Recommendation

**Implement in phases:**

**Phase 1 (Week 1):** Macro + Sentiment + News
- 150 dimensions
- $100-200/month cost
- 80% of value

**Phase 2 (Week 2-3):** Micro-Local + Health + Weather
- +200 dimensions (350 total)
- +$100-200/month cost
- 15% additional value

**Phase 3 (Week 3-4):** Industry + Culture + Competitive + Financial
- +500 dimensions (850 total)
- +$200-500/month cost
- 4% additional value, but enables niche scenarios (e.g., Iran-specific)

**Phase 4 (Month 2):** Full 1000+ dimensions with all edge cases
- Most value already captured by Phase 3
- Final 5% incremental improvement
- Focus on reliability + caching optimization

---

**Status:** Ready for implementation
