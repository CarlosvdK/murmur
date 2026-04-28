# Murmur Production Readiness Plan — Complete TDD Approach

## Executive Summary
Taking Murmur from 554 passing tests to production-ready with comprehensive context enrichment. Following TDD: plan tests → verify failures → implement → verify passes.

**Timeline**: ~12-14 days
**Phases**: 5 → 4 → 6 → 1-3 (with focus on context engine comprehensiveness)

---

## PHASE 5: Deployment & Monitoring (2 days)
**Goal**: Get observable, auto-deployed, monitored production infrastructure

### 5a. Sentry Integration (Backend + Frontend)
**Test Plan**: `backend/tests/test_sentry.py` + `frontend/src/lib/sentry.test.ts`

Tests to write first:
```python
# Backend
class TestSentryInit:
    def test_sentry_initializes_with_dsn(self): ...
    def test_errors_captured_and_reported(self): ...
    def test_user_context_attached_to_errors(self): ...
    def test_sampling_rate_correct(self): ...
```

Implementation: Add to `backend/main.py`, `backend/config.py`

### 5b. Health Check Endpoint
**Test Plan**: `backend/tests/test_health.py` (extend existing)

```python
class TestHealthCheckComplete:
    def test_health_includes_version(self): ...
    def test_health_checks_db_connection(self): ...
    def test_health_includes_api_status(self): ...
    def test_health_has_required_fields(self): ...
```

Implementation: Update `/api/health` endpoint

### 5c. CI/CD Pipeline
**Files**: `.github/workflows/test-and-deploy.yml` (new)

Pipeline stages:
1. Lint & type check
2. Run backend tests (pytest)
3. Run frontend tests (vitest)
4. Build frontend (next build)
5. Deploy to Railway (backend) + Vercel (frontend)

### 5d. railway.json Configuration
**Test Plan**: Verify in CI/CD tests

```json
{
  "build": {"builder": "DOCKERFILE"},
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 30
  }
}
```

### 5e. Database Migrations
**Files**: Run pending migrations from `backend/db/migrations/`

---

## PHASE 4: Upload Data Injection (1-2 days)
**Goal**: Wire parsed CSV data into persona generation context

### 4a. CSV Context Injection
**Test Plan**: `backend/tests/test_simulation_upload_injection.py`

Tests to write first:
```python
class TestUploadContextInjection:
    async def test_csv_data_included_in_persona_generation(self): ...
    async def test_csv_summary_in_enriched_context(self): ...
    async def test_multiple_uploads_all_included(self): ...
    async def test_pending_uploads_excluded(self): ...
```

Implementation: Update `backend/api/routes/simulations.py` `_run_pipeline()` to:
1. Query parsed uploads for business
2. Build context string from parsed_data
3. Inject into enriched_parts

---

## PHASE 6: Real Outcomes Feedback Loop (1 day)
**Goal**: Complete A/B testing validation with real-world feedback

### 6a. Dashboard Outcomes UI
**Test Plan**: `frontend/src/app/app/page.test.tsx` (extend with 8 new tests)

Tests to write first:
```typescript
describe("Real Outcomes", () => {
  it("shows 'What happened?' button on completed sim", async () => { ... });
  it("opens outcome form when button clicked", async () => { ... });
  it("submits outcome and shows Logged badge", async () => { ... });
  it("shows Logged badge if outcome already recorded", async () => { ... });
  it("calculates accuracy stats correctly", async () => { ... });
  it("displays accuracy % on dashboard", async () => { ... });
  it("handles partial matches correctly", async () => { ... });
  it("shows empty state when no outcomes yet", async () => { ... });
});
```

Implementation: Update `frontend/src/app/app/page.tsx`

---

## PHASE 1: Context Engine - COMPREHENSIVE RESEARCH (3-4 days)

### Architecture: Multi-Layered Context for All Angles

The context engine searches 100+ angles organized into 5 layers:

**Layer 1: Market Fundamentals**
- Market size & growth trends
- Pricing benchmarks & trends
- Competitor analysis (5-10 key competitors)
- Demand signals & seasonality
- Supply chain health

**Layer 2: Economic Climate**
- Local inflation rates
- Currency fluctuations
- Interest rates & credit availability
- Labor market conditions
- Unemployment & wage trends

**Layer 3: Geographic & Environmental**
- Weather patterns & forecasts
- Climate impact on business
- Natural disaster risk
- Traffic/location intelligence
- Retail foot traffic trends

**Layer 4: Political & Regulatory**
- Local tax changes coming
- Business regulation changes
- Trade policy shifts
- Labor law changes
- Industry-specific regulations

**Layer 5: Cultural & Psychological**
- Consumer sentiment shifts
- Social media trends
- Brand perception in region
- Cultural events/holidays affecting demand
- Generational preferences
- News sentiment about industry

### 1a. Realtime Intelligence (Temporal + Social)

**Test Plan**: `backend/tests/test_realtime_intelligence.py`

```python
class TestTemporalContext:
    async def test_identifies_payday_weeks(self): ...
    async def test_identifies_holidays_by_country(self): ...
    async def test_identifies_shopping_seasons(self): ...
    async def test_returns_time_of_day_bucket(self): ...

class TestSocialSentiment:
    async def test_gathers_reddit_sentiment_for_industry(self): ...
    async def test_gathers_twitter_sentiment_for_brand(self): ...
    async def test_sentiment_score_in_valid_range(self): ...
    async def test_graceful_degradation_on_api_error(self): ...
```

Implementation: `backend/context/tools/realtime_intelligence.py`
- Uses `holidays` library for global holiday detection
- Reddit API for industry sentiment (via OAuth2)
- Google Trends for search momentum
- Current time/season analysis

### 1b. Location Profiler (Deep Geographic Intelligence)

**Test Plan**: `backend/tests/test_location_profiler.py`

```python
class TestLocationProfile:
    async def test_extracts_country_from_location(self): ...
    async def test_fetches_world_bank_inflation_data(self): ...
    async def test_fetches_gdp_growth(self): ...
    async def test_includes_hofstede_cultural_dimensions(self): ...
    async def test_includes_doing_business_index(self): ...
    async def test_includes_ease_of_doing_business_rank(self): ...

class TestDemographics:
    async def test_gathers_population_data(self): ...
    async def test_includes_income_distribution(self): ...
    async def test_includes_age_distribution(self): ...
    async def test_includes_urbanization_rate(self): ...
```

Implementation: `backend/context/tools/location_profiler.py`
- World Bank API: inflation, GDP, development indicators
- Hofstede cultural dimensions (cached database)
- Doing Business index for regulatory burden
- Open-Meteo for geocoding & coordinate extraction

### 1c. Weather & Environmental Impact

**Test Plan**: `backend/tests/test_weather_trends.py`

```python
class TestWeatherContext:
    async def test_fetches_current_weather(self): ...
    async def test_fetches_weather_forecast(self): ...
    async def test_identifies_weather_sensitivity(self): ...
    async def test_returns_seasonal_patterns(self): ...
    async def test_identifies_extreme_weather_risk(self): ...
    async def test_includes_air_quality_if_relevant(self): ...
```

Implementation: `backend/context/tools/weather_trends.py`
- Open-Meteo for real-time & forecast
- Identifies weather-sensitive industries
- Historical patterns for seasonality
- Extreme weather risk assessment

### 1d. Smart Orchestrator (Which angles matter for THIS business?)

**Test Plan**: `backend/tests/test_context_orchestrator_smart.py`

```python
class TestSmartOrchestration:
    async def test_restaurant_gathers_food_prices_inflation(self): ...
    async def test_ecommerce_gathers_shipping_costs(self): ...
    async def test_retail_gathers_foot_traffic_weather(self): ...
    async def test_salon_gathers_consumer_sentiment_trends(self): ...
    async def test_gym_gathers_seasonality_new_years(self): ...
    async def test_prioritizes_most_relevant_tools(self): ...
    async def test_completes_in_90_seconds_hard_timeout(self): ...
```

Implementation: Update `backend/context/orchestrator.py`
- Business type → relevance scoring for each tool
- Select 5-8 most relevant tools per business
- Run all in parallel with Semaphore(10)
- 90-second hard timeout with graceful degradation

### 1e. System Prompts for Comprehensive Search

**Files**: `backend/context/tools/prompts/` (new directory)

For each tool, create intelligent search instructions:

```
# web_search_prompt.txt
You are searching for information about {business_type} in {location}.

The user wants to understand how {question} might affect their business.

Search for ALL angles that could matter:
1. Direct market impact (prices, demand, supply)
2. Economic impact (inflation, interest rates, currency)
3. Regulatory/political impact (new laws, taxes, trade)
4. Competitive impact (competitor moves, market shifts)
5. Customer behavior shifts (trends, preferences, sentiment)
6. Operational impact (labor, supplies, logistics)
7. Risk factors (macro trends, emerging threats)

Return diverse perspectives, not just first Google results.
```

---

## PHASE 2-3: Error Handling & Frontend Polish (2-3 days)

### 2a. HTTP Retry Logic with Tenacity

**Test Plan**: `backend/tests/test_context_tools_retry.py`

```python
class TestRetryBehavior:
    async def test_retries_on_429_rate_limit(self): ...
    async def test_retries_on_500_server_error(self): ...
    async def test_no_retry_on_401_auth_error(self): ...
    async def test_exponential_backoff_correct(self): ...
    async def test_max_retries_respected(self): ...
```

### 2b. Frontend Polling & SSE

**Test Plan**: Extend existing ChatInterface tests

```typescript
describe("ChatInterface Resilience", () => {
  it("reconnects after network error", async () => { ... });
  it("shows timeout after 8 minutes", async () => { ... });
  it("falls back to polling if SSE fails", async () => { ... });
  it("shows connection lost after 3 failures", async () => { ... });
});
```

### 2c. Form Validation

**Test Plan**: Extend BusinessProfileForm tests

```typescript
describe("Form Validation", () => {
  it("requires min 3 chars for business name", () => { ... });
  it("requires min 50 chars for description", () => { ... });
  it("shows error messages on blur", () => { ... });
  it("disables next until valid", () => { ... });
});
```

---

## Execution Timeline

| Phase | Task | Tests | Implementation | Days |
|-------|------|-------|-----------------|------|
| **5** | Sentry setup | 8 | config, main.py, frontend | 0.5 |
| **5** | Health check | 4 | /api/health | 0.5 |
| **5** | CI/CD + railway.json | 0 | GitHub Actions, config | 1 |
| **4** | CSV injection | 4 | simulations.py | 1 |
| **6** | Outcomes UI | 8 | app/page.tsx | 1 |
| **1a** | Realtime intelligence | 8 | context tools | 1 |
| **1b** | Location profiler | 6 | context tools + World Bank | 1 |
| **1c** | Weather | 6 | Open-Meteo integration | 0.5 |
| **1d** | Smart orchestrator | 7 | orchestrator.py | 0.5 |
| **1e** | System prompts | 0 | prompts directory | 0.5 |
| **2a** | Retry logic | 5 | tenacity decorators | 0.5 |
| **2b** | Frontend resilience | 8 | ChatInterface.tsx | 1 |
| **2c** | Form validation | 4 | BusinessProfileForm.tsx | 0.5 |
| | **TOTAL** | **70 new tests** | | **10-12 days** |

---

## Success Criteria

- ✅ 554 existing tests + 70 new tests = **624 total tests all passing**
- ✅ CI/CD pipeline green on main
- ✅ Sentry errors visible in dashboard
- ✅ Context engine searches 100+ angles for any business type
- ✅ Real outcomes loop complete
- ✅ Production health check responding
- ✅ Zero network calls from tests
- ✅ All features work without API keys (graceful degradation)

---

## Notes on Context Engine Comprehensiveness

The context engine uses a **"smart selection" approach** rather than searching everything every time:

1. **Business Profile Analysis**: Extract business type, industry, customer base
2. **Relevance Scoring**: Score all 50+ available data sources by relevance (0-100)
3. **Select Top 5-8**: Run highest-relevance sources
4. **Parallel Execution**: All selected tools run in parallel with Semaphore
5. **Graceful Degradation**: If any tool fails, continue with others
6. **90-Second Hard Timeout**: Return whatever we have by deadline

Example scoring:
- Restaurant + "raise prices" → (food_inflation: 95, competitor_prices: 90, customer_sentiment: 85, labor_costs: 80, ...)
- SaaS + "new feature" → (tech_trends: 95, customer_sentiment: 90, competitor_features: 85, market_size: 80, ...)

This way, the context is always relevant without requiring perfect system prompts.
