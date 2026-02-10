# Competitive Analysis Reference

Reference this when the task includes competitor URLs or when CrUX data reveals competitive positioning opportunities.

---

## Competitive Analysis Workflow

When competitors are known or can be inferred:

1. Use `crux-data` skill with `--origin "https://competitor.com"` for each competitor
2. Create a relative ranking table
3. Contextualize recommendations based on competitive position

**Example workflow:**
```
Run: crux-data --origin "https://competitor-a.com" --form-factor ALL_FORM_FACTORS
Run: crux-data --origin "https://competitor-b.com" --form-factor ALL_FORM_FACTORS
```

**Example output:**
| Domain | LCP | INP | CLS | CWV Pass | Rank |
|--------|-----|-----|-----|----------|------|
| client.com | 2.4s | 150ms | 0.05 | Yes | 2/4 |
| competitor-a.com | 3.1s | 180ms | 0.12 | No | 3/4 |
| competitor-b.com | 2.2s | 120ms | 0.03 | Yes | 1/4 |

> "Your site ranks #2 among analyzed competitors. Competitor-B is faster but only marginally (0.2s LCP difference)."
