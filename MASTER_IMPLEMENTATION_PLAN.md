# Murmur Production Ready: Master Implementation Plan (TDD)
**Document Version**: 1.0  
**Date**: 2026-04-20  
**Status**: Ready for Claude CLI execution  
**Estimated Duration**: 3-4 weeks  
**Test Target**: 500+ tests, 500+ research papers, full integration

---

## EXECUTIVE SUMMARY

Murmur is a customer simulation platform for ANY business decision (not just pricing). This plan:
1. **Fixes corpus problem** (currently 0 papers pass QC) → Build 500+ high-quality papers
2. **Improves context understanding** (market conditions matter) → Add competitive/market context
3. **Expands beyond pricing** → Support all simulation types
4. **Uses TDD throughout** → Tests first, implementation second
5. **Ensures full integration** → Everything wired together end-to-end

Current state: 436 tests, 0 production-ready papers, 3 integration gaps.  
Target state: 500+ tests, 500+ papers, zero integration gaps.

---

## PART 1: CURRENT STATE INVENTORY

### Tests (436 passing)
- ✅ 19 realtime_intelligence tests
- ✅ 13 location_profiler tests  
- ✅ 10 weather_tool tests
- ✅ 7 context_tools_retry tests
- ✅ 23 quality_control tests
- ✅ 5 corpus_loader_integration tests
- ✅ 12/15 simulation_pipeline_e2e tests (3 failing = gaps identified)
- ❌ 0 market context tests
- ❌ 0 scenario diversity tests
- ❌ 0 full simulation end-to-end tests

### Research Corpus (0 usable papers)
- 114 "experiments" (score: 0.02-0.29, all rejected)
- 53 expansion papers (score: 0.00-0.07, all rejected)
- 391 research papers (different purpose - RAG context, not backtesting)
- **PROBLEM**: None meet quality threshold ≥0.40

### Integrations (12/15 working)
- ✅ Realtime intelligence → context
- ✅ Location profiler → context
- ✅ Context tools with retry logic
- ✅ Quality scoring system
- ❌ Context → persona generation (not wired)
- ❌ Backtesting → accuracy tracking (not stored)
- ❌ Research categorization → simulation use (not tagged)
- ❌ Frontend → research citations (not displayed)

### Simulation Types (Currently Limited)
- ✅ Price changes (partial support)
- ❌ Feature changes
- ❌ Service/experience changes
- ❌ Product changes  
- ❌ Marketing changes
- ❌ Staffing/labor changes
- ❌ Location/hours changes
- ❌ Customer segment targeting

---

## PART 2: RESEARCH CORPUS BUILD (500+ Papers Target)

### 2.1 Paper Types (Diversify Beyond A/B Tests)

**Category A: Behavioral Research (80-100 papers)**
- Stated vs revealed preference studies
- Customer adoption curves
- Feature usage patterns
- Loyalty/repeat purchase drivers
- Sources: Journal of Consumer Research, Consumer Psychology Review

**Category B: Pricing & Elasticity (100-120 papers)**
- Price elasticity by industry (restaurant, SaaS, retail, etc.)
- Dynamic pricing outcomes
- Price discrimination studies
- Price change acceptance research
- **IMPORTANT**: Market-context effects (if competitors raise prices too, acceptance ↑)
- Sources: Journal of Marketing Research, pricing research papers

**Category C: Feature & Product (60-80 papers)**
- Feature adoption rates by complexity
- User onboarding impact on retention
- Product redesign customer reaction
- Feature deprecation churn impact
- Sources: Product management research, CHI/CSCW papers

**Category D: Service & Experience (60-80 papers)**
- Service quality changes and loyalty
- Wait time impact on satisfaction
- Staff behavior customer reaction
- Delivery/shipping time elasticity
- Sources: Journal of Service Research, hospitality research

**Category E: Marketing & Positioning (60-80 papers)**
- Promotional effectiveness by customer segment
- Brand positioning changes
- Advertising spend elasticity
- Customer acquisition cost by channel
- Sources: Journal of Marketing, Marketing Science

**Category F: Location & Hours (40-60 papers)**
- Store hours impact on traffic
- Location change customer retention
- Convenience factor customer segments
- Geographic price differences acceptance
- Sources: Retail research, location analytics papers

**Category G: Staffing & Labor (40-60 papers)**
- Staff count impact on service quality
- Wage changes employee retention
- Staff training ROI customer satisfaction
- Automation acceptance by customer type
- Sources: HR research, service management papers

**Category H: Market & Competitive (60-80 papers)**
- Competitor price change customer switch
- New competitor entry market share loss
- Market consolidation outcomes
- Market saturation customer behavior
- **KEY INSIGHT**: If ALL competitors raise prices 15%, customers accept 12-14% (not just 5-8%)
- Sources: Microeconomics, competitive strategy papers

**Category I: Customer Segment Specific (40-60 papers)**
- Restaurant: Office workers vs tourists vs regulars, price sensitivity by daypart
- SaaS: SMB vs enterprise, feature preferences, pricing model acceptance
- Retail: By income, age, geography, online vs in-store preference
- Sources: Industry-specific research, customer segmentation studies

---

### 2.2 Data Sources (Ranked by ROI)

**TIER 0: Published Company Data (1-2 weeks, 150+ papers)**
```
Airbnb Research Blog
├── 50+ published experiments with methodology
├── Price elasticity, feature impact, seasonality
├── Quality: 0.75+ (company published = high credibility)
└── Time to extract: 2-3 days

Netflix Research
├── 20+ documented experiments
├── UI changes, recommendation impact, pricing
├── Quality: 0.70+
└── Time: 1 day

Booking.com Research
├── 30+ seasonality, pricing, demand studies
├── Hotel, flights, rental cars
├── Quality: 0.65-0.75
└── Time: 2 days

Stripe/Square/Shopify
├── 40+ pricing, feature, customer behavior
├── SaaS-specific + marketplace data
├── Quality: 0.65-0.75
└── Time: 2 days

Uber/Lyft Research
├── 30+ surge pricing, demand, driver supply
├── Market dynamics under competition
├── Quality: 0.70+
└── Time: 1-2 days

Instacart/DoorDash
├── 25+ delivery, pricing, customer acquisition
├── Same-day delivery elasticity
├── Quality: 0.65-0.75
└── Time: 1-2 days

Amazon Research
├── 20+ pricing, recommendations, logistics
├── A/B test methodology papers
├── Quality: 0.75+
└── Time: 1-2 days
```
**Subtotal: ~185 papers in 2 weeks, avg quality 0.70**

**TIER 1: Academic Journals (2-3 weeks, 150+ papers)**
```
Top Journals (Peer-Reviewed, High Rigor):
├── Marketing Science (30 papers)
├── Journal of Marketing Research (35 papers)
├── Journal of Consumer Research (30 papers)
├── Management Science (25 papers)
├── Journal of Retailing (25 papers)
└── Economics & Business journals (50+ papers)

Search Strategy:
├── "A/B test" OR "randomized experiment" (50 papers)
├── "price elasticity" (30 papers)
├── "customer behavior change" (25 papers)
├── "feature adoption" (20 papers)
├── "service quality impact" (15 papers)
└── Industry-specific: "restaurant", "retail", "SaaS" (40+ papers)

Quality: 0.60-0.85 (peer-reviewed, some missing business context)
Time: 3 weeks (PDF parsing, manual extraction)
```
**Subtotal: ~155 papers in 3 weeks, avg quality 0.70**

**TIER 2: Industry Reports & Case Studies (2 weeks, 100+ papers)**
```
Industry Research:
├── Forrester research reports (15 papers)
├── Gartner reports (15 papers)
├── McKinsey insights (20 papers)
├── Deloitte industry trends (20 papers)
├── IBISWorld industry analyses (20 papers)
└── Trade publications (15+ papers)

Case Studies:
├── Harvard Business Review cases (20 papers)
├── INSEAD case studies (15 papers)
├── Stanford GSB cases (10 papers)
└── Business textbooks (15 papers)

Quality: 0.50-0.75 (published but sometimes light on data)
Time: 2 weeks
```
**Subtotal: ~115 papers in 2 weeks, avg quality 0.65**

**TIER 3: Niche + Specialized Research (1-2 weeks, 50-70 papers)**
```
├── Restaurant industry studies (15 papers)
├── Hospitality research journals (15 papers)
├── E-commerce optimization (15 papers)
├── SaaS benchmarking reports (15 papers)
├── Retail analytics (10 papers)
└── Marketplace dynamics (5 papers)

Quality: 0.45-0.70 (specialized but may lack rigor)
Time: 1-2 weeks
```
**Subtotal: ~65 papers in 2 weeks, avg quality 0.58**

**TOTAL ESTIMATE: 520+ papers in 4 weeks**

---

### 2.3 Quality Scoring (Updated for Market Context)

```python
Quality Score (0.0-1.0) Components:

1. METHODOLOGY RIGOR (0-25 pts):
   ├── Peer reviewed (10 pts)
   ├── Controlled/comparison group (8 pts)
   ├── Randomization (5 pts)
   └── Sample size adequate (2 pts)

2. STATISTICAL REPORTING (0-20 pts):
   ├── P-value/significance (8 pts)
   ├── Effect size/confidence interval (8 pts)
   └── Power analysis documented (4 pts)

3. BUSINESS CONTEXT (0-20 pts):
   ├── Industry clearly specified (5 pts)
   ├── Customer segment defined (5 pts)
   ├── Company size/type (5 pts)
   └── Geography specified (5 pts)

4. MARKET DYNAMICS (0-15 pts):  # NEW
   ├── Competitor context mentioned (7 pts)
   ├── Market saturation/growth state (5 pts)
   └── Seasonal/temporal factors (3 pts)

5. ACTIONABILITY (0-10 pts):
   ├── Metric clear & replicable (8 pts)
   └── Applicable to SMB (2 pts)

6. CREDIBILITY (0-10 pts):
   ├── Citation count (5 pts)
   ├── Author/organization reputation (5 pts)

THRESHOLDS:
├── <0.40: REJECTED (don't load)
├── 0.40-0.59: CALIBRATION (use for persona training)
├── 0.60-0.79: BACKTESTING (use for accuracy validation)
└── 0.80+: PREMIUM (showcase as exemplar cases)
```

---

### 2.4 Market Context Intelligence (NEW CAPABILITY)

**Problem**: "Price increase always bad" is wrong. Context matters.

**Solution**: Tag each paper with market conditions

```python
Market Context Tags:

1. COMPETITIVE LANDSCAPE:
   ├── "monopoly" (single seller)
   ├── "duopoly" (2 main competitors)
   ├── "oligopoly" (3-5 competitors)
   └── "perfect_competition" (10+ competitors)

2. PRICE MOVEMENT:
   ├── "sole_raiser" (only this company raises price)
   ├── "coordinated_increase" (all competitors raise ~same %)
   ├── "mixed_movement" (some up, some down)
   └── "deflation" (all prices falling)

3. MARKET CONDITIONS:
   ├── "high_demand" (sellers have leverage)
   ├── "equilibrium" (balanced supply/demand)
   ├── "excess_supply" (buyers have leverage)
   └── "crisis" (abnormal conditions)

EFFECT MODIFIERS:
├── IF competitor_landscape = "monopoly" AND you_raise_price:
│   └── Customer acceptance: 60-80% (what choice do they have?)
├── IF competitor_landscape = "perfect_competition" AND all_raise_price:
│   └── Customer acceptance: 50-70% (everyone raised it, can't switch)
├── IF competitor_landscape = "perfect_competition" AND only_you_raise:
│   └── Customer acceptance: 20-40% (will switch to competitor)
└── IF market = "high_demand" AND you_raise_price:
    └── Customer acceptance: +15% boost (demand pulling up)
```

---

## PART 3: SIMULATION SCENARIOS (Beyond Pricing)

### 3.1 Scenario Types Supported

```
PRICING SCENARIOS:
├── Absolute increase ($5 → $6)
├── Percentage increase (10%, 20%, 50%)
├── Tiered pricing (different for segments)
├── Dynamic pricing (peak vs off-peak)
└── WITH market context (sole_raiser vs coordinated)

FEATURE/PRODUCT SCENARIOS:
├── New feature launch (adoption curve)
├── Feature removal (churn impact)
├── UI redesign (learning curve cost vs benefit)
├── Complexity reduction (accessibility vs capability)
├── Feature pricing (tier-based access)
└── Bundle changes (what's included in plan)

SERVICE/EXPERIENCE SCENARIOS:
├── Service quality up (premium materials, training)
├── Service quality down (cost-cutting, automation)
├── Wait time increase (understaffing, growth)
├── Convenience changes (hours, locations, online)
├── Personalization level (data usage, privacy)
└── Support responsiveness (chat speed, ticket time)

MARKETING SCENARIOS:
├── Promotional frequency (discounts, loyalty)
├── Brand positioning shift
├── Targeting changes (age, income, location)
├── Channel shifts (online vs offline emphasis)
├── Pricing transparency (hide vs show costs)
└── Customer acquisition spend

STAFFING SCENARIOS:
├── Staff count change (hours cut, hiring freeze)
├── Staff training investment (quality improvement)
├── Wage changes (retention impact)
├── Automation introduction (efficiency vs trust)
├── Staff behavior change (scripts, personality)
└── Diversity/representation changes

LOCATION/OPERATIONS SCENARIOS:
├── Store hours change (open earlier/later)
├── Location move (new neighborhood)
├── Store closing (consolidation)
├── Capacity changes (expansion, downsizing)
├── Delivery areas (geographic expansion)
└── Supply chain changes (local vs global)

SEGMENT TARGETING SCENARIOS:
├── Focus on high-value customers only
├── Serve budget segment exclusively
├── Vertical specialization (niche down)
├── Geographic focus (one region vs national)
├── Customer tenure priority (new vs repeat)
└── Demographic targeting changes

MARKET POSITIONING SCENARIOS:
├── Premium repositioning (quality, price up)
├── Value repositioning (budget, price down)
├── Niche positioning (specific segment)
├── Disruption positioning (new model)
└── Sustainability/values positioning
```

### 3.2 Test Scenarios (TDD - Write These First)

```python
# test_pricing_scenarios.py
test_sole_raiser_high_competition():
    # If only you raise prices in competitive market → negative
    assert sentiment < -0.5

test_coordinated_price_increase():
    # If all competitors raise prices → less negative
    assert sentiment_coordinated > sentiment_sole_raiser

test_price_increase_high_demand():
    # If market demand is high → customers accept higher prices
    assert sentiment_with_demand > sentiment_baseline

test_feature_launch_adoption_curve():
    # New feature adoption follows S-curve
    assert adoption_day_1 < adoption_day_30 < adoption_day_60

test_service_quality_downgrade():
    # Quality decrease → customer churn increases
    assert churn_rate_after > churn_rate_before

test_staff_reduction_impact():
    # Staff cuts → longer wait times → customer satisfaction down
    assert satisfaction_after < satisfaction_before

test_store_hours_cut():
    # Reduced hours → convenience loss → traffic decline
    assert traffic_after < traffic_before

test_sustainability_positioning():
    # ESG message → some customers accept premium price
    assert premium_acceptance_with_esg > without_esg

test_bundle_change_migration():
    # Removing a bundle → migration to other tiers
    assert migration_rate > 0

test_personalization_privacy_tradeoff():
    # High personalization → better experience but privacy concerns
    assert satisfaction_up but_privacy_concerns_up
```

---

## PART 4: INTEGRATION WIRING (Fix the 3 Gaps)

### 4.1 Gap 1: Context → Persona Generation

**Current**: Context gathered but not injected into prompts

**Test First** (test_context_injection.py):
```python
async def test_context_injected_into_system_prompt():
    """Persona system prompt should include context narrative."""
    business = get_test_business()
    context = await gather_context(business, question)
    
    # Mock the persona generation
    personas = await generate_personas(business, context=context)
    
    # Verify context was used (check persona reasoning mentions context)
    assert any("inflation" in p.reasoning.lower() for p in personas)
    assert any("competitor" in p.reasoning.lower() for p in personas)

async def test_context_affects_persona_behavior():
    """Personas with context should give different answers than without."""
    context_rich = "Market inflation 8%, competitors raising prices"
    context_poor = ""
    
    personas_rich = await generate_personas(business, context=context_rich)
    personas_poor = await generate_personas(business, context=context_poor)
    
    # Rich context should produce more nuanced responses
    assert personas_rich[0].response != personas_poor[0].response
```

**Implementation**: 
1. Update `backend/swarm/persona_generator.py`
2. Add `{{context}}` variable to system prompt template
3. Inject `context.filtered_narrative` before API call

### 4.2 Gap 2: Backtesting → Accuracy Storage

**Test First** (test_backtesting_tracking.py):
```python
async def test_backtest_result_stored_in_db():
    """Backtest result should be stored with simulation."""
    simulation = create_simulation()
    actual_outcome = "customer_churn_8pct"  # Known from data
    predicted = "customer_churn_5pct"  # From simulation
    accuracy = calculate_accuracy(predicted, actual)
    
    store_backtest_result(simulation.id, {
        "predicted": predicted,
        "actual": actual_outcome,
        "accuracy_pct": accuracy,
        "match": True/False
    })
    
    # Query back
    stored = get_backtest_result(simulation.id)
    assert stored["accuracy_pct"] == accuracy

async def test_accuracy_trends_queryable():
    """Accuracy metrics should be aggregatable."""
    results = get_accuracy_trends(
        business_type="restaurant",
        scenario_type="price_increase",
        days=30
    )
    
    assert results["avg_accuracy"] >= 0.0
    assert results["count"] >= 1
```

**Implementation**:
1. Create `simulation_accuracy` table in Supabase
2. Update `backend/api/routes/simulations.py` to store results
3. Add `/api/accuracy-stats` query endpoint

### 4.3 Gap 3: Research → Citation in Output

**Test First** (test_research_citations.py):
```python
async def test_simulation_result_includes_citations():
    """Simulation output should cite research that influenced it."""
    result = await run_simulation(business, scenario)
    
    assert "citations" in result
    assert len(result["citations"]) >= 1
    assert all("title" in c and "doi" in c for c in result["citations"])

async def test_persona_reasoning_cites_research():
    """Persona responses should reference relevant research."""
    personas = result["personas"]
    
    # At least some personas should cite research in reasoning
    cited_personas = [p for p in personas if "research" in p.reasoning.lower()]
    assert len(cited_personas) >= len(personas) * 0.5
```

**Implementation**:
1. Link context tools to research corpus
2. Track which papers contributed to context
3. Include `citations` array in simulation output
4. Frontend displays: "Based on research by [Citation 1], [Citation 2]..."

---

## PART 5: TDD EXECUTION (Tests → Code)

### 5.1 Test Creation Order

**Week 1: Foundation Tests**
```
Day 1-2: Research corpus tests
├── test_quality_control.py (already done)
├── test_corpus_loader_integration.py (already done)  
└── test_research_corpus_500_papers.py (NEW)
    └── Verify 500+ papers loaded, >0.40 quality threshold

Day 3: Market context tests
├── test_market_context_tags.py (NEW)
│   └── Verify competitor landscape affects customer acceptance
├── test_price_change_competitive_effects.py (NEW)
│   └── Sole raiser vs coordinated increase scenarios
└── test_seasonal_market_conditions.py (NEW)

Day 4-5: Scenario type tests
├── test_pricing_scenarios.py (NEW - 8 tests)
├── test_feature_scenarios.py (NEW - 8 tests)
├── test_service_scenarios.py (NEW - 8 tests)
├── test_marketing_scenarios.py (NEW - 8 tests)
└── test_staffing_scenarios.py (NEW - 8 tests)

Week 1 Total: 40+ new tests, all FAILING
```

**Week 2: Integration Tests**
```
Day 6-7: Wiring tests
├── test_context_injection.py (NEW - 3 tests)
├── test_backtesting_tracking.py (NEW - 3 tests)
└── test_research_citations.py (NEW - 3 tests)

Day 8-9: E2E pipeline tests
├── test_simulation_full_pipeline.py (NEW - 10 tests)
│   └── Verify: business → context → personas → aggregation → output
├── test_market_context_flow.py (NEW - 5 tests)
├── test_scenario_diversity.py (NEW - 5 tests)
└── test_result_citation_accuracy.py (NEW - 5 tests)

Day 10: Integration validation
├── test_frontend_backend_contracts.py (NEW - 5 tests)
└── test_api_response_schemas.py (NEW - 5 tests)

Week 2 Total: 41+ new tests, all FAILING
```

**Week 3-4: Implementation (RED → GREEN)**
```
Week 3: Core implementations
├── Build market context tag system
├── Implement 8 scenario types  
├── Wire context into persona prompts
├── Add backtesting result storage
└── Link research to citations

Week 4: Polish + E2E validation
├── All tests PASSING
├── 500+ papers loaded
├── Full simulation pipeline working
├── Accuracy tracking implemented
└── Research citations displaying
```

### 5.2 Test Template

```python
# EVERY test follows this pattern:

@pytest.mark.asyncio
async def test_description_of_behavior():
    """What should happen."""
    
    # ARRANGE: Set up test data
    business = create_test_business(
        type="restaurant",
        location="San Francisco, CA",
        description="Coffee shop"
    )
    scenario = create_test_scenario(
        type="price_increase",
        magnitude=15,
        market_context="coordinated_increase"
    )
    
    # ACT: Execute the code
    result = await run_simulation(business, scenario)
    
    # ASSERT: Verify expected behavior
    assert result["overall_sentiment"] == "negative"
    assert result["average_acceptance"] >= 0.45  # Coordinated = higher acceptance
    assert "citations" in result  # Should cite research

# Key: EVERY test is independent, can run in any order, cleans up after itself
```

---

## PART 6: IMPLEMENTATION CHECKLIST

### Phase 1: Research Corpus (Weeks 1-2)

- [ ] **Day 1-2: Tier 0 data extraction**
  - [ ] Airbnb blog scraper (50 papers)
  - [ ] Netflix research parser (20 papers)
  - [ ] Booking.com data extraction (30 papers)
  - [ ] Stripe/Square/Shopify compilation (40 papers)
  - [ ] Subtotal: 140 papers

- [ ] **Day 3-4: Tier 1 academic**
  - [ ] Google Scholar search automation (query builder)
  - [ ] arXiv PDF downloader
  - [ ] JSTOR metadata extraction
  - [ ] Subtotal: 100 papers (collected, not all extracted yet)

- [ ] **Day 5-6: Tier 2 industry reports**
  - [ ] McKinsey insights scraper
  - [ ] Deloitte report downloader
  - [ ] HBR case study parser
  - [ ] Subtotal: 80 papers

- [ ] **Day 7-10: Tier 3 specialized**
  - [ ] Restaurant industry research
  - [ ] SaaS benchmarking
  - [ ] E-commerce studies
  - [ ] Marketplace research
  - [ ] Subtotal: 60 papers

- [ ] **Day 11-14: Quality scoring + tagging**
  - [ ] Run quality scorer on all 500 papers
  - [ ] Tag with market context (competitor landscape, price movement)
  - [ ] Categorize by scenario type
  - [ ] Load into Supabase with full metadata
  - [ ] Verify ≥400 papers ≥0.40 quality

### Phase 2: Market Context Intelligence (Weeks 1-2)

- [ ] **Design market context model**
  - [ ] Define competitor_landscape enum (monopoly, duopoly, oligopoly, perfect_competition)
  - [ ] Define price_movement enum (sole_raiser, coordinated, mixed, deflation)
  - [ ] Define market_conditions enum (high_demand, equilibrium, excess_supply, crisis)
  - [ ] Create effect modifier lookup table

- [ ] **Tests for market context** (all must be RED first)
  - [ ] test_sole_raiser_acceptance() → expects 20-40%
  - [ ] test_coordinated_increase_acceptance() → expects 50-70%
  - [ ] test_monopoly_price_power() → expects 60-80%
  - [ ] test_high_demand_acceptance_boost() → expects +15%
  - [ ] test_market_saturation_price_sensitivity() → expects -10%

- [ ] **Implementation**
  - [ ] Add market context to BusinessContext model
  - [ ] Add effect modifier function: apply_market_context(base_sentiment, context)
  - [ ] Update persona prompts with market awareness
  - [ ] Wire market data into context enrichment

### Phase 3: Scenario Types (Weeks 2-3)

- [ ] **Feature/Product scenarios**
  - [ ] NEW tests: adoption_curve, feature_removal_churn, ui_redesign, bundling
  - [ ] Implementation: scenario handler for each type
  - [ ] Research data: link to 80+ feature studies

- [ ] **Service/Experience scenarios**
  - [ ] NEW tests: service_quality_impact, wait_time_effect, convenience_value
  - [ ] Implementation: service change analyzer
  - [ ] Research data: link to 80+ service studies

- [ ] **Marketing scenarios**
  - [ ] NEW tests: promotion_effectiveness, brand_shift, targeting_impact
  - [ ] Implementation: marketing scenario generator
  - [ ] Research data: link to 80+ marketing studies

- [ ] **Staffing scenarios**
  - [ ] NEW tests: staff_reduction_impact, training_roi, wage_retention
  - [ ] Implementation: labor change analyzer
  - [ ] Research data: link to 60+ HR studies

- [ ] **Location/Operations scenarios**
  - [ ] NEW tests: hours_impact, location_move, capacity_change
  - [ ] Implementation: operations change simulator
  - [ ] Research data: link to 60+ operational studies

- [ ] **Segment targeting scenarios**
  - [ ] NEW tests: value_vs_premium_segments, niche_focus, geographic_focus
  - [ ] Implementation: segmentation impact calculator
  - [ ] Research data: link to 60+ segmentation studies

### Phase 4: Integration Wiring (Weeks 2-4)

- [ ] **Gap 1: Context → Personas**
  - [ ] test_context_injected_into_system_prompt() [RED]
  - [ ] test_context_affects_persona_behavior() [RED]
  - [ ] Update persona_generator.py to accept context param
  - [ ] Inject {{context}} into system prompt template
  - [ ] Run tests [GREEN]

- [ ] **Gap 2: Backtesting → Tracking**
  - [ ] test_backtest_result_stored_in_db() [RED]
  - [ ] test_accuracy_trends_queryable() [RED]
  - [ ] Create simulation_accuracy Supabase table
  - [ ] Add storage logic to simulations.py
  - [ ] Add /api/accuracy-stats endpoint
  - [ ] Run tests [GREEN]

- [ ] **Gap 3: Research → Citations**
  - [ ] test_simulation_result_includes_citations() [RED]
  - [ ] test_persona_reasoning_cites_research() [RED]
  - [ ] Add citations array to SimulationResult model
  - [ ] Track papers used during context gathering
  - [ ] Link papers to personas in output
  - [ ] Run tests [GREEN]

- [ ] **Full E2E pipeline**
  - [ ] test_full_simulation_pipeline() [RED]
    - [ ] business → context gathering
    - [ ] context → persona generation
    - [ ] personas → interview
    - [ ] interviews → aggregation
    - [ ] aggregation → result with citations
  - [ ] Implementation: wire all components
  - [ ] Run test [GREEN]

### Phase 5: Validation & Publishing (Week 4)

- [ ] **Accuracy validation**
  - [ ] Run backtest on 50+ papers with known outcomes
  - [ ] Calculate accuracy_pct for each
  - [ ] Publish accuracy dashboard
  - [ ] Document results by scenario type

- [ ] **Diversity validation**
  - [ ] Verify 500+ papers across all scenario types
  - [ ] Check coverage: ≥5 industries, ≥3 company sizes
  - [ ] Ensure ≥50% papers ≥0.60 quality (backtesting-ready)

- [ ] **Integration validation**
  - [ ] Run full test suite: 500+ tests
  - [ ] All must pass
  - [ ] Coverage: every code path tested
  - [ ] No integration gaps remaining

- [ ] **Production readiness**
  - [ ] Documentation: all scenario types explained
  - [ ] Release notes: what's new in this version
  - [ ] API docs: updated with new endpoints
  - [ ] Research docs: explain how papers inform results

---

## PART 7: TEST COUNTS & EXPECTATIONS

```
Current: 436 tests
Target: 500+ tests

Breakdown of new tests:
├── Market context tests: 20
├── Scenario type tests: 50 (8 per type × 6 types + 2 common)
├── Integration tests: 30 (context, backtesting, citations × 3 each)
├── E2E pipeline tests: 20
└── Result validation tests: 20
──────────────────────────
TOTAL NEW: 140+
GRAND TOTAL: 576+ tests ✅
```

---

## PART 8: SUCCESS CRITERIA

- ✅ **500+ research papers** loaded, >400 ≥0.40 quality
- ✅ **576+ tests** all passing
- ✅ **8+ scenario types** supported (pricing, features, service, marketing, staffing, location, segmentation, positioning)
- ✅ **Market context** affects customer acceptance realistically
- ✅ **Context → Personas** fully wired
- ✅ **Backtesting** results stored and queryable
- ✅ **Citations** displayed with every result
- ✅ **Zero integration gaps** remaining
- ✅ **Diverse industries** covered (restaurant, SaaS, retail, hospitality, e-commerce, marketplace, etc.)
- ✅ **Diverse company sizes** covered (solo, SMB, enterprise)

---

## PART 9: EXECUTION COMMAND FOR CLAUDE CLI

When context runs out, use this command to continue:

```bash
claude code /Users/Carlos/Desktop/Projects/murmur/murmur

# Then paste this entire plan as context, add:
# "Continue with Phase 1 of the implementation plan. Start with Week 1, Day 1 tasks. Use strict TDD - write failing tests first, then implement to make them pass. Report which tests are now passing and which are still failing. Focus on building the 500+ research paper corpus starting with Tier 0 (published company data)."
```

---

## PART 10: KEY INSIGHTS FOR IMPLEMENTATION

### Insight 1: Market Context Matters
```
// DON'T assume price increase always = negative
// DO account for competitive landscape

scenario: price_increase_15pct
├── IF sole_raiser_in_competitive_market: 
│   └── customer_acceptance = 20-40%
├── IF coordinated_increase_across_industry:
│   └── customer_acceptance = 50-70%
└── IF high_demand_market:
    └── customer_acceptance = +15% boost to baseline
```

### Insight 2: Scenario Diversity
```
// DON'T only simulate pricing changes
// DO support ANY business decision

- A coffee shop can simulate: 
  ├── Price increase (pricing)
  ├── Adding espresso bar (feature)
  ├── Extending hours (operations)
  ├── Hiring more baristas (staffing)
  ├── Focusing on walk-ins vs tourists (segmentation)
  └── Going "premium craft" positioning (marketing)

- Each uses different research base
- Each has different customer acceptance
- ALL equally valuable to business owner
```

### Insight 3: Integration Testing Catches Gaps
```
// DON'T just unit test components
// DO write E2E tests for full pipeline

// E2E test revealed 3 gaps that unit tests missed:
├── Context gathered but not injected into prompts
├── Backtesting logic written but results not stored
└── Research papers used but not cited in output

// Only full pipeline tests catch these
```

### Insight 4: Quality > Quantity
```
// DON'T load 1000 low-quality papers
// DO load 500 high-quality papers

// Current corpus had 114 papers @ 0.02-0.29 quality
// All were rejected by 0.40 threshold
// Better: 500 papers @ 0.60+ quality

// Quality gates prevent garbage-in-garbage-out
```

---

## APPENDIX A: Research Corpus JSON Schema

```json
{
  "id": "unique-id",
  "source_name": "Case Title",
  "source_type": "academic_paper|industry_report|case_study|blog",
  "publication_name": "Journal/Company Name",
  "authors": ["Author 1", "Author 2"],
  "published_year": 2024,
  "doi": "10.1234/example",
  "citation_count": 45,
  "url": "https://...",
  "pdf_url": "https://...",
  
  "quality_score": 0.75,
  "quality_breakdown": {
    "methodology_rigor": 20,
    "statistical_reporting": 18,
    "business_context": 18,
    "market_dynamics": 12,
    "actionability": 8,
    "credibility": 9
  },
  
  "business_context": {
    "industry": "restaurant|saas|retail|etc",
    "business_type": "cafe|hotel|marketplace",
    "company_size": "solo|smb|mid_market|enterprise",
    "geography": ["US", "EU", "Global"],
    "customer_segment": "premium|budget|mixed"
  },
  
  "market_dynamics": {
    "competitor_landscape": "monopoly|duopoly|oligopoly|perfect_competition",
    "market_condition": "high_demand|equilibrium|excess_supply|crisis",
    "price_movement": "sole_raiser|coordinated_increase|mixed|deflation"
  },
  
  "scenario_type": ["pricing", "features", "service", "marketing", "staffing", "location", "segmentation"],
  
  "study_details": {
    "change_description": "What changed in the study",
    "magnitude": "15% increase",
    "metric": "customer_churn|revenue|satisfaction",
    
    "methodology": {
      "study_type": "a_b_test|case_study|observational|experimental",
      "sample_size": 50000,
      "duration_days": 30,
      "control_group": true,
      "randomized": true,
      "power_analysis": 0.80
    },
    
    "results": {
      "direction": "positive|negative|neutral",
      "effect_size": 0.25,
      "effect_size_type": "cohen_d|percentage|absolute",
      "p_value": 0.001,
      "confidence_interval": [0.18, 0.32],
      "significant": true
    }
  },
  
  "key_insight": "Summary of what this research teaches",
  "applicability": "For [scenario type], expect [outcome] in [industry]",
  "caveats": ["Small sample", "Limited to premium segment", "etc"],
  
  "sourced_date": "2026-04-20",
  "extracted_by": "claude",
  "verified": false,
  "verified_by": null
}
```

---

## APPENDIX B: Implementation Checklist Template

Copy this for each phase:

```markdown
## Week 1: Foundation

### Day 1: [Task Name]
- [ ] Subtask 1 (RED test)
- [ ] Subtask 2 (GREEN implementation)
- [ ] Subtask 3 (validation)
- [ ] **Status**: _pending / in_progress / blocked / done_
- [ ] **Tests**: X passing / X failing
- [ ] **Notes**: 

### Day 2: [Task Name]
...
```

---

**This plan is ready to hand off to Claude CLI. Contains everything needed to complete production implementation without needing the full conversation context.**
