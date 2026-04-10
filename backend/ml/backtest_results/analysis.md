# Backtest Results Analysis -- 2026-04-09

## Results: 6/9 correct (67%)

| # | Case | Result | Why |
|---|------|--------|-----|
| 1 | Booking.com Urgency | WRONG | Stated vs revealed preference gap. Personas say they hate urgency but behavior shows it works. |
| 2 | Netflix Personalization | ERROR | API parsing error. Need retry. |
| 3 | HubSpot Remove Nav | WRONG | Same gap. Personas feel "trapped" without nav but conversion data shows it works. |
| 4 | Etsy Free Shipping | CORRECT | Clear preference signal -- shipping costs are universally disliked. |
| 5 | Obama Button Text | CORRECT | "Learn More" = lower commitment. Personas correctly identify friction. |
| 6 | Airbnb Pro Photos | CORRECT | Universal consensus that quality photos matter. |
| 7 | Amazon One-Click | CORRECT | Personas correctly value convenience over security concerns. |
| 8 | Basecamp Long Page | WRONG | Personas prefer short/clean but real users need information to decide. |
| 9 | Walmart Page Speed | CORRECT | Universal agreement that faster = better. |
| 10 | Groove Personal Email | CORRECT | Strong preference for authenticity from small business. |

## Key Insight: The Stated vs Revealed Preference Gap

All 3 failures share the same pattern: personas express STATED preferences (what they say they want) that differ from REVEALED preferences (what they actually do).

- **Urgency messaging**: People say they hate pressure, but it increases conversions
- **Removing navigation**: People say they want freedom to browse, but fewer options = more action
- **Long-form pages**: People say they prefer clean/short, but more information = more confidence to act

This is documented in the research library:
- Murphy et al. 2005: hypothetical bias correction = ~28%
- Gui & Toubia 2023: LLM personas overstate acceptance by 20-30%
- The gap is LARGER for psychologically uncomfortable options (manipulation, restriction, information overload)

## What This Means for the ML Model

With 9 data points we cannot train a meaningful model. We need:
- 50+ backtest cases for basic model training
- 100+ for reliable feature importance
- Diverse business types, countries, and question types

## Recommended Improvements

1. **Apply hypothetical bias correction**: For questions where the change feels "manipulative" or "restrictive", apply a 25-30% correction toward the positive direction
2. **Add behavioral realism instructions**: Tell personas to respond based on what they'd ACTUALLY DO, not what they'd SAY in a survey
3. **Detect friction-reduction patterns**: Questions about removing steps/options should flag the stated/revealed gap
4. **More backtest cases**: Need 40+ more cases across different industries and countries

## Training Set vs Holdout

- Training set (cases 1-7): 4/6 = 67%
- Holdout set (cases 8-10): 2/3 = 67%
- Consistency between sets suggests the error rate is genuine, not overfitting
