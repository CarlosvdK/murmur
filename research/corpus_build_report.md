# Experiment Corpus Build Report
Date: 2026-04-09

## Sources Scraped
- Semantic Scholar API: 18 + 21 queries (39 total)
- SerpAPI Google Scholar: 11 + 28 + 15 queries (54 total)
- WebFetch case study pages: 3 pages (Contentsquare, Fibr.ai, Pricing Solutions)
- WebSearch: 2 searches (Optimizely base rates, restaurant pricing)
- Total API calls: ~95

## Corpus Size
Total unique records: **114**

By source type:
- Academic papers: 76
- Company case studies: 36
- Industry reports: 2

By citation quality:
- 100+ citations: 16
- 50-99 citations: 13
- 20-49 citations: ~20
- <20 citations or no count: ~65

With quantified outcomes:
- Numeric effect size: 38
- Direction (positive/negative/neutral): 38

## Key High-Value Records

### Foundational Papers (1000+ citations)
- Diffusion of Innovations (Rogers) -- 172,865 citations
- Prospect Theory (Kahneman & Tversky) -- 98,731 citations
- Whence Consumer Loyalty (Oliver) -- 23,418 citations
- Mental Accounting (Thaler) -- 10,514 citations
- Status Quo Bias (Samuelson & Zeckhauser) -- 9,191 citations
- Agent-Based Modeling (Bonabeau) -- 7,264 citations
- Generative Agents (Park et al.) -- 4,849 citations

### Directly Applicable Experiments
- Restaurant price increase: +4% revenue, no traffic loss (Pricing Solutions)
- Store remodel: comparing new vs existing customer reactions (90 citations)
- Coffee loyalty card frequency effects (130 citations)
- Menu simplification and sales impact
- Service robot introduction: labor + customer effects (95 citations)
- Nudging effects on food purchasing (123 citations)
- Hotel in-room sustainability experiments (106 citations)

### Calibration Findings
- Optimizely: Only 12% of 127,000+ experiments produce significant wins
- Hypothetical bias: ~25-35% overstatement in stated preferences (Murphy meta-analysis, 1,622 citations)
- LLM simulation: ~85% accuracy with rich data (Park 2024, 395 citations)
- LLM positive bias: ~20-30% overstatement (Gui & Toubia, 72 citations)

## Gaps Still Present

### Need more:
1. **Small restaurant/cafe price experiments** (only 1 quantified case found)
2. **European SMB experiments** (most data is US-based)
3. **Hours change experiments** (very few found)
4. **Renovation/remodel with customer retention data**
5. **Vendor negotiation experiments** (B2B field experiments rare)

### Quality improvement needed:
- 76 records lack methodology fields (had_control_group, sample_size)
- These need full-text processing to extract quality indicators
- Currently all academic papers score "low quality" because methodology fields are empty

## Database Migration
Run `backend/db/migration_004_experiment_corpus.sql` in Supabase SQL Editor.

## Files
- `research/corpus/combined_corpus.json` -- 114 records (master file)
- `research/corpus/scrape_20260409_010916.json` -- original 42 records
- `research/corpus/serpapi_extended.json` -- 49 extended papers
- `research/corpus/must_fetch_papers.json` -- 2 direct-fetched papers
- `research/corpus/final_round.json` -- 33 final round papers
- `backend/research/quality_scorer.py` -- quality scoring module
- `backend/research/corpus_scraper.py` -- automated scraper
- `backend/db/migration_004_experiment_corpus.sql` -- DB tables
