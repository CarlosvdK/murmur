# A/B Test Corpus Curation Plan — Target 150+ High-Quality Cases

## Current State
- ❌ 114 "experiments" = research papers without methodology (score: 0.02-0.29)
- ✅ 391 research papers = good for RAG context
- ❌ 53 expansion papers = all low quality (score: 0.00-0.07)
- ❌ **Zero papers pass QC (≥0.40)**

## Target
**150 A/B test case studies** with full methodology:
- Sample size, control group, randomization, statistical significance
- Effect sizes, p-values, confidence intervals
- Business context (industry, location, customer type)
- Real outcomes data for backtesting

## Data Sources (Ranked by Quality)

### Tier 1: Published Academic (50-60 cases)
**Source**: Journal databases + published business case studies
- *Marketing Science*, *Journal of Marketing Research* — rigorous published experiments
- *Harvard Business Review* case studies with data
- *Journal of Retailing* — retail-specific A/B tests
- *Cornell Hospitality Quarterly* — hospitality/restaurant experiments
- Keywords: "A/B test", "randomized experiment", "field experiment", "online experiment"

**Quality**: ✅ High (peer-reviewed, control groups, randomization documented)
**Extraction**: PDF parsing + manual curation for methodology

### Tier 2: Published Industry Reports (40-50 cases)
**Source**: Company research publications, consulting reports
- Airbnb research blog (published experiments)
- Booking.com research papers
- Netflix research publications
- Amazon research papers
- Stripe research papers

**Quality**: ✅ Medium-High (usually good methodology, author-credible)
**Extraction**: Direct from published reports + blogs

### Tier 3: Conference Papers (30-40 cases)
**Source**: KDD, WWW, CSCW, CHI, EC proceedings
- "Online controlled experiment" keyword search
- Business-focused tracks
- Published with effect sizes and p-values

**Quality**: ✅ Medium (peer-review rigorous, sometimes limited business context)
**Extraction**: arXiv + conference databases

### Tier 4: Business Textbooks & Case Studies (20-30 cases)
**Source**: "Testing the Impossible" (Thomke), A/B Testing guides, case study compilations
- Known documented experiments with real numbers
- Multiple independent sources for cross-validation

**Quality**: ✅ Medium (curated but not original research)
**Extraction**: Manual transcription from published cases

## Methodology Extraction Template

For each case, extract:

```json
{
  "source_name": "Case title",
  "source_type": "academic_paper|industry_report|textbook|blog",
  "publication_name": "Journal/Company/Conference",
  "authors": ["Author 1", "Author 2"],
  "published_year": 2024,
  "doi": "10.1234/example",
  "peer_reviewed": true,
  
  "business_context": {
    "industry": "e-commerce|hospitality|saas|restaurant|retail",
    "business_type": "saas",
    "customer_count": 50000,
    "country": "US",
    "region": "global|US|EU"
  },
  
  "experiment_design": {
    "had_control_group": true,
    "was_randomised": true,
    "randomization_unit": "user|session|order",
    "sample_size": 100000,
    "duration_days": 30,
    "statistical_power": 0.80
  },
  
  "change_description": "Increased button color from blue to red",
  "primary_metric": "click_through_rate",
  "change_magnitude": "15% increase in CTA button color saturation",
  
  "results": {
    "direction": "positive",
    "effect_size_numeric": 0.25,
    "effect_size_type": "cohen_d",
    "statistical_significance": "significant",
    "p_value": 0.001,
    "confidence_interval": [0.18, 0.32],
    "customer_acceptance_rate": 0.92,
    "revenue_impact": 0.08
  },
  
  "citation_count": 245,
  "abstract": "..."
}
```

## Quality Scoring (This determines usability)

Papers will be scored on:
1. **Methodology** (peer_reviewed, control_group, randomization): 60 pts
2. **Sample size & power** (10K+, published power analysis): 20 pts
3. **Reporting quality** (p-values, CI, effect size): 10 pts
4. **Citation/credibility** (academic or company authored): 10 pts

**Minimum**: 0.40 (use for calibration)
**Strong**: ≥0.60 (use for backtesting)
**Premium**: ≥0.80 (publish as exemplar cases)

## Collection Workflow

### Phase 1: Systematic Search (1-2 weeks)
1. Set up academic database access (Google Scholar, arXiv, JSTOR)
2. Search 20+ keyword combinations per Tier 1-2 source
3. Download + auto-extract metadata (title, authors, DOI, abstract)
4. Initial screen: does paper report an A/B test with numbers?
5. **Target**: 200-300 candidate papers

### Phase 2: Manual Curation (2-3 weeks)
1. For each candidate, extract full methodology from PDF
2. Rate on 0.0-1.0 quality scale
3. Keep only ≥0.40
4. **Target**: 150 papers pass QC

### Phase 3: Validation (1 week)
1. Spot-check 20 random papers for extraction accuracy
2. Compare effect sizes across similar industries (sanity check)
3. Add missing fields via fallback sources
4. **Target**: <5% extraction errors

### Phase 4: Continuous (Ongoing)
1. Monthly search for new published papers
2. Auto-score on ingestion
3. Quarterly review of citation counts + relevance
4. Prune papers that age out (>10 years, outdated context)

## Implementation Priority

**Week 1**: Focus on Tier 1 academic sources
- Search 15 journals for "A/B test", "randomized experiment"
- Extract 50 cases minimum
- Get to ≥20 papers ≥0.60 quality for backtesting

**Week 2**: Add Tier 2 industry reports
- Compile company research blogs (Airbnb, Netflix, Stripe)
- Transcribe 30-40 documented experiments
- Cross-check for duplicates

**Week 3**: Tier 3 conferences + textbooks
- KDD/WWW proceedings search
- Business case textbooks (Thomke, etc.)
- Aim for 150 total

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Total cases collected | 150+ | — |
| ≥0.40 quality | 150 | — |
| ≥0.60 backtesting-ready | 80+ | — |
| Industry diversity | 8+ industries | — |
| Geographic diversity | 5+ countries | — |
| Date range | 2010-2024 | — |
| Avg citations/case | 50+ | — |

## Technical Notes

- Store in `research/corpus/curated_experiments.json` (master file)
- Version control important: include `sourced_date`, `extracted_by`, `verified_by`
- Flag papers needing human review: `needs_verification: true`
- Link to source PDF for spot-checking: `pdf_url` field

---

**Next Step**: Agree on target number (aim for 150+), then prioritize sources to start with.
