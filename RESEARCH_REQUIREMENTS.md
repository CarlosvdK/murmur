# Research Data Requirements — Beyond A/B Tests

## 1. DATA TYPES NEEDED (Not Just A/B Tests)

### Category 1: Behavioral Research (40-50 cases)
**What**: How customers actually behave (stated vs revealed preference)
**Examples**:
- Survey studies on willingness-to-pay vs actual purchase price
- Lab studies on stated preference vs choice behavior
- Field research on intention-to-use vs actual product adoption
- Customer journey mapping studies
**Sources**: 
- Journal of Consumer Research
- Consumer Psychology journals
- Qualtrics XM research library
- SurveyMonkey research reports

### Category 2: Price Elasticity & Demand (30-40 cases)
**What**: How prices affect customer demand/volume
**Examples**:
- Pricing experiment results (A/B tests on prices)
- Demand curve studies
- Price sensitivity segmentation data
- Competitor pricing impact studies
**Sources**:
- Harvard Business School case studies
- McKinsey pricing research
- Deloitte pricing insights
- Academic pricing literature

### Category 3: Market & Competitive Research (30-40 cases)
**What**: Market structure, competitor moves, market share impacts
**Examples**:
- Competitor pricing changes and market response
- New competitor entry studies
- Market consolidation outcomes
- Geographic market performance data
**Sources**:
- Euromonitor research
- Statista studies
- IBISWorld industry reports
- Company earnings call transcripts with data

### Category 4: Seasonality & Temporal Patterns (20-30 cases)
**What**: How business performance varies by season/time
**Examples**:
- Holiday season demand patterns
- Back-to-school impact on customer behavior
- Weather effects on retail
- Day-of-week patterns
- Time-of-day customer preferences
**Sources**:
- Retail analytics reports
- Visa/Mastercard spending indices
- Weather & retail correlation studies
- Booking.com research on seasonality

### Category 5: Demographic & Psychographic (20-30 cases)
**What**: How customer segments differ (age, income, values, etc.)
**Examples**:
- Generational preferences (Gen Z vs Millennial spending)
- Income segment behavior differences
- Geographic demographic patterns
- Lifestyle/values based segmentation
**Sources**:
- Nielsen consumer insights
- Pew Research Center studies
- Bureau of Labor Statistics data
- Academic consumer research

### Category 6: Product/Feature Research (20-30 cases)
**What**: Feature adoption, feature impact on retention/usage
**Examples**:
- New feature adoption curves
- Feature usage impact on retention
- Product redesign outcomes
- Feature complexity vs adoption tradeoffs
**Sources**:
- Company research blogs (product studies)
- Product management case studies
- Mobile app research (iOS/Android studies)
- SaaS product research

### Category 7: Customer Satisfaction & NPS (15-25 cases)
**What**: Correlation between actions and customer satisfaction/loyalty
**Examples**:
- Service change impact on NPS
- Price increase customer churn data
- Experience improvement retention gains
- Complaint handling outcome studies
**Sources**:
- HubSpot CRM research
- Zendesk customer service studies
- Salesforce customer success research
- Journal of Service Research

### Category 8: Industry-Specific Case Studies (30-40 cases)
**By Industry**:
- **Restaurant**: Menu changes, price changes, staff changes, hours impact
- **E-commerce**: Shipping impact, product reviews, checkout flow
- **SaaS**: Pricing tiers, feature access, onboarding changes
- **Retail**: Store layout, staffing, in-store promotions
- **Hospitality**: Room pricing, amenities, booking changes
- **Healthcare**: Appointment time changes, new services impact

**Sources**:
- Industry-specific journals
- Trade publications case studies
- Company annual reports (if they publish consumer impact data)
- Industry association research

## 2. DATA QUALITY DIMENSIONS (Beyond Methodology)

Each research item should be scored on:

```
Quality Score Components:
├── Methodological Rigor (0-25 pts)
│   ├── Peer reviewed (10)
│   ├── Control group/comparison (8)
│   ├── Randomization (5)
│   └── Sample size adequate (2)
├── Statistical Reporting (0-20 pts)
│   ├── P-value/significance (8)
│   ├── Effect size/confidence interval (8)
│   └── Power analysis (4)
├── Business Context (0-20 pts)
│   ├── Industry clarity (5)
│   ├── Customer segment clarity (5)
│   ├── Business model match (5)
│   └── Geography specified (5)
├── Actionability (0-20 pts)
│   ├── Clear metric definition (8)
│   ├── Replicable in small business context (8)
│   └── Applicable across industries (4)
├── Citation & Credibility (0-15 pts)
│   ├── Citation count (8)
│   ├── Author credibility (4)
│   └── Publication date recency (3)
└── Data Completeness (0-5 pts)
    └── All key fields populated (5)
```

## 3. SOURCES RANKED BY AVAILABILITY & SPEED

### Tier 0: Published Data (Fast - 2-3 weeks to 50+ cases)
**Why Fast**: Already extracted, structured data available
- Booking.com research archive
- Airbnb research blog (50+ published experiments)
- Netflix research papers (20+ documented changes with outcomes)
- Stripe research publications
- Square research
- Shopify research reports

### Tier 1: Academic Databases (Medium - 4-6 weeks)
**Why Medium**: Requires PDF scraping + manual extraction
- Google Scholar (free)
- arXiv.org (free)
- JSTOR (need institutional access or pay)
- ResearchGate (semi-free)
- PubMed (free for life sciences)

### Tier 2: Industry Reports (Medium - 4-6 weeks)
- McKinsey insights (some free)
- BCG research
- Deloitte industry reports
- IBISWorld (paid)
- Statista (paid, but some free summaries)

### Tier 3: Case Study Compilations (Medium - 3-5 weeks)
- Business textbooks with data
- "Testing the Impossible" (Thomke)
- Case study databases (some universities free)
- LinkedIn Learning courses with transcripts

### Tier 4: Direct Company Sources (Slow - 6-8+ weeks)
**Why Slow**: Must reach out, negotiate, wait for response
- Company research teams (Booking, Netflix, etc.)
- Industry associations with research
- University research centers

## 4. DIFFERENT VALIDATION APPROACHES

### Beyond A/B Testing

**Approach 1: Backtesting Against Known Outcomes**
- Run simulation with historical data
- Compare predicted customer reactions to actual customer behavior
- Metric: % accuracy of predicted sentiment direction
- Challenge: Need historical data + outcomes

**Approach 2: Persona Consistency Validation**
- Run same scenario 5+ times with same seed
- Personas should give similar answers (consistency check)
- Metric: CoVar between runs < 0.15
- Advantage: No external data needed

**Approach 3: Sensitivity Analysis**
- Vary one input parameter at a time
- Verify outputs change proportionally
- Metric: Elasticity curves match academic literature
- Example: Price up 10% → demand down 5-15% (matches elasticity studies)

**Approach 4: Sanity Checks**
- Run known scenarios (e.g., "price increase by 50%")
- Verify simulation matches intuition
- Personas should mostly say "negative"
- Metric: ≥80% negative sentiment on extreme scenario

**Approach 5: Comparative Validation**
- Run same scenario through multiple personas
- Verify diversity of responses (not all agree)
- Metric: Entropy of responses > threshold
- Advantage: Validates persona diversity

**Approach 6: Behavioral Economics Cross-Check**
- Verify simulation respects known behavioral principles
- Example: Loss aversion (losing $10 > gaining $10)
- Metric: Persona responses match behavioral econ literature
- Sources: "Thinking, Fast and Slow" (Kahneman), behavioral econ papers

**Approach 7: Industry Benchmark Comparison**
- For each business type/scenario, compare to industry norms
- Example: Restaurant price increase → compare to Restaurant A/B tests
- Metric: Simulation results within industry range
- Advantage: Cheap to validate (just need industry data)

## INTEGRATION REQUIREMENTS

### Should Be Connected:
✓ Research data → Context engine (used for enrichment)
✓ Research data → Backtesting validation
✓ A/B test cases → Persona calibration
✓ Behavioral studies → Persona prompts
✓ Seasonality data → Realtime context enrichment
✓ Industry benchmarks → Caveat generation
✓ Price elasticity research → Price change scenarios

### Testing Points:
- Can simulator access all research data?
- Does context engine incorporate research in persona generation?
- Are backtesting scores tracked and published?
- Do validation runs produce consistent results?
- Is every research paper scored and categorized?

---

## RECOMMENDED EXECUTION

**Phase 1 (Weeks 1-2)**: Build from published company data
- Airbnb: 50 documented experiments
- Netflix: 20 documented changes
- Stripe: 15+ pricing/feature research
- Booking: 30 seasonal/behavioral studies
- Target: 120 cases, all high quality (0.70+)

**Phase 2 (Weeks 3-4)**: Add academic research
- Journal of Marketing Research: 40 studies
- Journal of Consumer Research: 30 studies  
- Marketing Science: 25 studies
- Pricing literature: 30 studies
- Target: 150 more cases, mixed quality (0.40-0.85)

**Phase 3 (Weeks 5-6)**: Industry-specific case studies
- Restaurant case studies: 15
- SaaS case studies: 15
- Retail case studies: 15
- E-commerce case studies: 15
- Target: 100+ more cases, contextual value high

**Total Target**: 350+ research items (diverse types) with full integration
