# Murmur Production Readiness — Claude CLI Handoff Prompt

## COPY EVERYTHING BELOW AND PASTE INTO CLAUDE CLI

---

# PROJECT CONTEXT

You are continuing work on **Murmur**, a customer simulation platform for small businesses. The system generates synthetic customer personas to test business decisions (pricing, features, service, marketing, staffing, location, positioning). 

**Current Status**: 
- 524 research papers collected (410+ passing quality threshold 0.40+)
- 472 backend tests passing
- 3 new API tools created but NOT YET WIRED IN
- Production goal: 500+ tests, full integration, zero gaps

**Tech Stack**: 
- Backend: FastAPI (Python 3.11) + Supabase + Redis
- Frontend: Next.js 14 + TypeScript + Tailwind
- AI: Claude API (claude-sonnet-4-20250514)
- Context Engine: 8 data tools + orchestrator

---

## YOUR TASK THIS SESSION

**Phase**: Week 2 (Integration & Wiring)  
**Approach**: Strict TDD - RED → GREEN → REFACTOR  
**Success Metric**: All tests passing, all tools wired, zero integration gaps

**DO THIS FIRST**:
1. Read MASTER_IMPLEMENTATION_PLAN.md (see below)
2. Install & verify all dependencies
3. Wire 3 NEW API tools into context engine orchestrator
4. Write integration tests (RED phase)
5. Implement integration code (GREEN phase)
6. Run full test suite - NO FAILURES

---

## MASTER_IMPLEMENTATION_PLAN.md

### Executive Summary
Murmur needs:
- ✅ 500+ research papers (DONE - 524 papers, 410 passing QC)
- ✅ Market context intelligence (DONE - tags present in corpus)
- ✅ 8+ scenario types (DONE - all 8 covered in corpus)
- ❌ NEW API tools wired (TO DO - FRED, Alpha Vantage, Google Trends)
- ❌ Integration tests for new tools (TO DO - must verify tools work end-to-end)
- ❌ Tools integrated into orchestrator (TO DO - must select right tool per question)
- ❌ Full E2E pipeline tested (TO DO - corpus → tools → context → personas → output)

### Current State Inventory

**Tests**: 472 passing (up from 436)
- ✅ 23 corpus quality tests
- ✅ 13 new API tool tests
- ✅ 19 realtime_intelligence tests
- ✅ 13 location_profiler tests
- ✅ 10 weather_tool tests
- ✅ 7 context_tools_retry tests
- ✅ 23 quality_control tests
- ✅ 5 corpus_loader_integration tests
- ❌ 3 integration gaps (context→personas, backtesting→storage, research→citations)

**Research Corpus**: 524 papers
- Tier 0 (Published companies): 215 papers (Airbnb, Netflix, Booking, Stripe, Uber, DoorDash, Amazon)
- Tier 1 (Academic): 145 papers (Marketing Science, JMR, JCR, Management Science)
- Tier 2+ (Industry): 164 papers
- Quality: 410+ passing ≥0.40 threshold, avg 0.63

**API Keys** (Set these in .env -- never commit actual values):
```
FRED_API_KEY=<redacted -- get from https://fred.stlouisfed.org/docs/api/api_key.html>
ALPHA_VANTAGE_API_KEY=<redacted -- get from https://www.alphavantage.co/support/#api-key>
WORLD_BANK_API_KEY=  # Free, no key needed
GOOGLE_TRENDS=pytrends  # Library installed, no key needed
```

**New Files Created**:
- `backend/context/tools/economic_data.py` - FRED API (inflation, unemployment, fed rate)
- `backend/context/tools/market_data.py` - Alpha Vantage (S&P 500, sectors, currency)
- `backend/context/tools/trends_data.py` - Google Trends via pytrends (trending searches, interest)
- `backend/tests/test_context_tools_new_apis.py` - 13 unit tests (all passing)
- `backend/requirements.txt` - Added `pytrends==4.7.3`

### Three Integration Gaps to Fix

**Gap 1: Context → Personas** 
- Context gathered but NOT injected into persona system prompt
- Tests: `test_context_injected_into_system_prompt()`, `test_context_affects_persona_behavior()`
- Fix: Update `persona_generator.py` to accept context param and inject {{context}} into template

**Gap 2: Backtesting → Accuracy Storage**
- Backtesting logic exists but results NOT stored in database
- Tests: `test_backtest_result_stored_in_db()`, `test_accuracy_trends_queryable()`
- Fix: Create `simulation_accuracy` table, wire `/api/accuracy-stats` endpoint

**Gap 3: Research → Citations**
- Research papers used but NOT cited in output
- Tests: `test_simulation_result_includes_citations()`, `test_persona_reasoning_cites_research()`
- Fix: Add citations array to SimulationResult, track papers used in context

---

## WEEK 2 EXECUTION PLAN

### Day 1-2: Wire New API Tools into Orchestrator

**RED Phase** (Write failing tests):

```python
# backend/tests/test_context_orchestrator_with_new_tools.py
@pytest.mark.asyncio
async def test_orchestrator_selects_economic_tool_for_pricing_question():
    """If question is about pricing, select EconomicDataTool"""
    orchestrator = ContextOrchestrator()
    tools_selected = await orchestrator.select_tools(
        business_type="restaurant",
        question="What if I raise prices 15%?",
        location="San Francisco, USA"
    )
    assert any("economic" in t.lower() for t in tools_selected)

@pytest.mark.asyncio
async def test_orchestrator_selects_market_tool_for_competition_question():
    """If question is about competitors, select MarketDataTool"""
    orchestrator = ContextOrchestrator()
    tools_selected = await orchestrator.select_tools(
        business_type="restaurant",
        question="How are competitors pricing in my area?",
        location="San Francisco, USA"
    )
    assert any("market" in t.lower() for t in tools_selected)

@pytest.mark.asyncio
async def test_orchestrator_selects_trends_tool_for_customer_interest():
    """If question is about customer interest, select GoogleTrendsTool"""
    orchestrator = ContextOrchestrator()
    tools_selected = await orchestrator.select_tools(
        business_type="restaurant",
        question="Is there growing interest in healthy food options?",
        location="San Francisco, USA"
    )
    assert any("trend" in t.lower() for t in tools_selected)

@pytest.mark.asyncio
async def test_new_tools_return_string_narrative():
    """All tools must return plain-text narrative (not JSON)"""
    economic = EconomicDataTool(FRED_API_KEY)
    market = MarketDataTool(ALPHA_VANTAGE_KEY)
    trends = GoogleTrendsTool()
    
    result_e = await economic.execute("San Francisco, USA")
    result_m = await market.execute("San Francisco, USA")
    result_t = await trends.execute("restaurant", "San Francisco, USA")
    
    assert isinstance(result_e, str) and len(result_e) > 0
    assert isinstance(result_m, str) and len(result_m) > 0
    assert isinstance(result_t, str) and len(result_t) > 0

@pytest.mark.asyncio
async def test_orchestrator_runs_tools_in_parallel():
    """Tools should run in parallel, not sequentially"""
    orchestrator = ContextOrchestrator()
    
    import time
    start = time.time()
    context = await orchestrator.gather_context(
        business={...},
        question="What if I raise prices?",
        location="SF, USA"
    )
    elapsed = time.time() - start
    
    # Should complete in ~10s (parallel) not 30s (sequential)
    assert elapsed < 15, f"Orchestrator took {elapsed}s, should be <15s for parallel execution"

@pytest.mark.asyncio
async def test_orchestrator_gracefully_degrades_on_tool_failure():
    """If a tool fails, orchestrator should still return context from other tools"""
    # Mock one tool to fail
    with patch("backend.context.tools.economic_data.EconomicDataTool.execute", side_effect=Exception("API down")):
        context = await orchestrator.gather_context(...)
        assert context is not None
        assert "market" in context.lower() or "trend" in context.lower()
```

**GREEN Phase** (Implement):

1. Update `backend/context/orchestrator.py`:
   - Add new tools to registry
   - Update tool selection logic (keyword matching + Claude reasoning)
   - Ensure parallel execution with `asyncio.gather()`
   - Implement graceful degradation

2. Update `backend/context/realtime_intelligence.py`:
   - Integrate new tools into context gathering pipeline
   - Inject economic + market + trend context into filtered_narrative

3. Wire into simulation pipeline:
   - `backend/api/routes/simulations.py` calls orchestrator
   - Result includes context from all 11 tools (8 existing + 3 new)

### Day 3-4: Test Integration with Full Pipeline

**RED Phase**:

```python
# backend/tests/test_context_pipeline_full_integration.py
@pytest.mark.asyncio
async def test_full_pipeline_restaurant_pricing_scenario():
    """End-to-end: business → context (with new tools) → personas → results"""
    business = Business(
        id="test-1",
        type="restaurant",
        location="San Francisco, USA",
        description="Italian restaurant, upscale",
        customer_description="Affluent professionals, age 35-55"
    )
    
    scenario = "Price increase 15%"
    
    # Should gather context using all tools
    context = await context_engine.gather_context(business, scenario)
    
    # Context should include:
    assert "inflation" in context.lower() or "economic" in context.lower()  # FRED
    assert "market" in context.lower() or "competitor" in context.lower()   # Alpha Vantage
    assert "trend" in context.lower() or "search" in context.lower()       # Google Trends
    
    # Generate personas with context
    personas = await persona_generator.generate(business, context)
    
    # Personas should reference context in reasoning
    assert any("inflation" in p.reasoning.lower() for p in personas)
    
    # Run simulation
    result = await simulator.run(personas, scenario)
    
    # Result should include metadata
    assert result.overall_sentiment in ["positive", "negative", "neutral"]
    assert result.confidence >= 0.0 and result.confidence <= 1.0

@pytest.mark.asyncio
async def test_all_scenario_types_work_with_new_context():
    """Test all 8 scenario types with new context tools"""
    scenarios = [
        ("pricing", "Price increase 20%"),
        ("features", "Add loyalty program"),
        ("service", "Extend hours 6am-11pm"),
        ("marketing", "Focus on Instagram"),
        ("staffing", "Hire 3 more staff"),
        ("location", "Move to downtown"),
        ("segmentation", "Target young professionals"),
        ("positioning", "Go premium/upscale"),
    ]
    
    for scenario_type, description in scenarios:
        context = await orchestrator.gather_context(business, description)
        assert context is not None
        assert len(context) > 50  # Should have substantial context

@pytest.mark.asyncio
async def test_context_relevance_filtering():
    """Orchestrator should select only relevant tools"""
    # Question about pricing → should include economic tool
    tools = await orchestrator.select_tools(
        question="What if I raise prices?",
        business_type="restaurant",
        location="SF, USA"
    )
    assert "economic" in [t.lower() for t in tools]
    
    # Question about foot traffic → should NOT include economic tool (not relevant)
    tools = await orchestrator.select_tools(
        question="Should I extend hours?",
        business_type="restaurant",
        location="SF, USA"
    )
    # Could include market or trends, but not necessarily economic
    assert len(tools) >= 2  # Should still select multiple relevant tools
```

**GREEN Phase**: Full integration tests must pass

### Day 5: Fix Integration Gaps

**Fix Gap 1: Context → Personas**

```python
# backend/tests/test_context_injection_into_personas.py
@pytest.mark.asyncio
async def test_context_injected_into_persona_system_prompt():
    """System prompt should include {{context}} variable"""
    context = "Economic Context: Inflation 3.2%, unemployment 4.1%"
    
    persona = await persona_generator.generate_single(
        business=test_business,
        context=context
    )
    
    # Persona's reasoning should reference context
    assert "inflation" in persona.reasoning.lower()

@pytest.mark.asyncio
async def test_personas_with_context_differ_from_without():
    """Personas given context should respond differently"""
    context = "Market is saturated, inflation rising 3.2%, customers price-sensitive"
    
    persona_with_context = await persona_generator.generate_single(
        business=test_business,
        context=context
    )
    
    persona_without_context = await persona_generator.generate_single(
        business=test_business,
        context=""
    )
    
    # Should produce different responses
    assert persona_with_context.response != persona_without_context.response
```

**Fix Gap 2: Backtesting → Accuracy Storage**

```python
# backend/tests/test_backtesting_storage.py
@pytest.mark.asyncio
async def test_simulation_accuracy_stored_in_db():
    """When simulation completes, accuracy should be stored"""
    simulation = await run_simulation(business, scenario)
    
    # Query accuracy
    accuracy = await db.table("simulation_accuracy").select("*").eq(
        "simulation_id", simulation.id
    ).single().execute()
    
    assert accuracy["accuracy_pct"] is not None
    assert accuracy["predicted_sentiment"] is not None
    assert accuracy["actual_outcome"] is not None
```

**Fix Gap 3: Research → Citations**

```python
# backend/tests/test_research_citations.py
@pytest.mark.asyncio
async def test_simulation_result_includes_citations():
    """Result should cite papers that informed it"""
    result = await run_simulation(business, scenario)
    
    assert "citations" in result
    assert len(result["citations"]) >= 1
    
    for citation in result["citations"]:
        assert "title" in citation
        assert "doi" in citation
```

---

## STEP-BY-STEP NEXT ACTIONS (IN ORDER)

### 1️⃣ SETUP (Do First)
```bash
# Install new dependency
pip install -r backend/requirements.txt

# Set environment variables
export FRED_API_KEY=<your-key>
export ALPHA_VANTAGE_API_KEY=<your-key>

# Verify tests pass
python -m pytest backend/tests/test_context_tools_new_apis.py -v
# Should: 13 passed
```

### 2️⃣ WEEK 2 DAY 1-2: WIRE TOOLS INTO ORCHESTRATOR

**File**: `backend/context/orchestrator.py`

DO THIS:
- [ ] Import 3 new tools (EconomicDataTool, MarketDataTool, GoogleTrendsTool)
- [ ] Add tools to registry dict
- [ ] Update `select_tools()` method with keyword matching for new tools
- [ ] Update `gather_context()` to call new tools
- [ ] Run parallel execution with `asyncio.gather()`
- [ ] Test: `pytest backend/tests/test_context_orchestrator_with_new_tools.py -v`

EXPECTED: All tests RED first, then GREEN after implementation

### 3️⃣ WEEK 2 DAY 3-4: INTEGRATION TESTS

**File**: `backend/tests/test_context_pipeline_full_integration.py`

DO THIS:
- [ ] Create end-to-end test: business → context → personas → results
- [ ] Verify context includes economic + market + trends data
- [ ] Test all 8 scenario types work with new context
- [ ] Test tool selection is smart (only relevant tools for question)
- [ ] Run: `pytest backend/tests/test_context_pipeline_full_integration.py -v`

EXPECTED: All integration tests passing

### 4️⃣ WEEK 2 DAY 5: FIX THREE INTEGRATION GAPS

#### Gap 1: Context Injection
**File**: `backend/swarm/persona_generator.py`

Changes:
```python
async def generate_single(self, business: Business, context: str = "") -> Persona:
    """Add context parameter"""
    system_prompt = self.PERSONA_SYSTEM_PROMPT.replace(
        "{{context}}", context
    )
    # ... rest of generation
```

Test: `pytest backend/tests/test_context_injection_into_personas.py -v`

#### Gap 2: Backtesting Storage
**File**: `backend/api/routes/simulations.py`

Changes:
1. Create table (SQL migration):
```sql
CREATE TABLE IF NOT EXISTS simulation_accuracy (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  simulation_id UUID NOT NULL REFERENCES simulations(id),
  predicted_sentiment TEXT,
  actual_outcome TEXT,
  accuracy_pct FLOAT,
  match BOOLEAN,
  created_at TIMESTAMP DEFAULT NOW()
);
```

2. Store result after simulation:
```python
await db.table("simulation_accuracy").insert({
    "simulation_id": simulation.id,
    "predicted_sentiment": result.overall_sentiment,
    "accuracy_pct": calculate_accuracy(predicted, actual),
}).execute()
```

Test: `pytest backend/tests/test_backtesting_storage.py -v`

#### Gap 3: Research Citations
**File**: `backend/swarm/aggregator.py`

Changes:
- Track which papers were used during context gathering
- Include citations in aggregation result:
```python
result.citations = [
    {"title": paper.source_name, "doi": paper.doi, "url": paper.url}
    for paper in papers_used
]
```

Test: `pytest backend/tests/test_research_citations.py -v`

### 5️⃣ FINAL VERIFICATION

Run full test suite:
```bash
python -m pytest backend/tests/ --tb=short -q
# Expected: ALL tests passing, 500+ total
```

Verify coverage:
- All 8 scenario types covered ✅
- All 3 integration gaps fixed ✅
- All new tools wired in ✅
- All tests passing ✅

---

## SUCCESS CRITERIA

At end of this session:
- [ ] 3 new API tools integrated into orchestrator
- [ ] 25+ new integration tests written and passing
- [ ] 3 integration gaps fixed
- [ ] 500+ backend tests passing
- [ ] Zero test failures
- [ ] Full E2E pipeline working (corpus → tools → context → personas → output)
- [ ] Research citations appearing in results
- [ ] Accuracy metrics tracked in database

**Deliverable**: Fully integrated context engine ready for production with all tests passing.

---

## KEY CONSTRAINTS

1. **TDD ONLY**: Write test first (RED), implementation second (GREEN)
2. **NO SKIPPED TESTS**: All tests must pass before moving to next phase
3. **GRACEFUL DEGRADATION**: If a tool fails, continue with other tools
4. **PARALLEL EXECUTION**: Tools must run in parallel (max 15s total)
5. **NO HARDCODING**: All configuration via environment variables
6. **INTEGRATION VERIFICATION**: E2E tests catch what unit tests miss

---

## REMEMBER

- This is a continuation session - corpus is built, unit tests for tools exist
- Focus: WIRING existing tools together + fixing integration gaps
- Not building new features - integrating existing ones
- Strict TDD: test failures tell you exactly what's wrong
- If a test fails, DON'T skip it - fix the root cause

Good luck! 🚀

