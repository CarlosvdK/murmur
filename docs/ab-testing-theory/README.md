# A/B Testing Theory Reference

This folder contains distilled knowledge from Prof. Uri Simonsohn's "Thinking with Data" course (MiBA 2025/2026). These are NOT the original slides — they are structured reference documents extracting the concepts most relevant to Murmur's swarm engine and confidence/caveat system.

## Files

| File | Topic | Key Murmur Relevance |
|------|-------|---------------------|
| [topic1-how-wrong.md](topic1-how-wrong.md) | Statistics is about quantifying error | CI-based decision framework, 4 p-value errors to avoid |
| [topic2-simulations.md](topic2-simulations.md) | Monte Carlo simulations & test evaluation | Our swarm IS a simulation — apply same rigor |
| [topic3-p-hacking.md](topic3-p-hacking.md) | Multiple comparisons & p-hacking | Don't cherry-pick persona responses, flag subgroup noise |
| [topic4-challenges.md](topic4-challenges.md) | Sample size, dependence, attrition | Novelty effects, self-selection, adherence caveats |
| [topic5-regression-to-mean.md](topic5-regression-to-mean.md) | RTM & intervention evaluation | Warn users asking questions after extreme performance |
| [topic6-causation.md](topic6-causation.md) | Correlation vs causation | Murmur cannot claim causation — must be honest about this |

## How Claude Code Should Use These

1. **When writing aggregation prompts**: Reference the decision framework from Topic 1 (three outcomes: do it, don't, need more info)
2. **When building confidence scores**: Use calibration concepts from Topic 2
3. **When selecting standout voices**: Avoid cherry-picking bias from Topic 3
4. **When generating caveats**: Pull from the specific warnings in Topics 4-6
5. **When users describe extreme situations**: Surface RTM warnings from Topic 5
6. **Never claim causation**: Topic 6 is clear — we simulate intentions, not causal effects
