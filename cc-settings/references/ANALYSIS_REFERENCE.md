# Analysis Reference: Budgets & Report Templates

Reference this when structuring recommendations with performance budgets or choosing a report format template.

---

## Performance Budgets

Recommend specific budgets based on site type:

### E-commerce Sites
| Resource | Budget | Rationale |
|----------|--------|-----------|
| Total page weight | <2MB | Balance rich content with speed |
| JavaScript | <300KB | Interactivity needs |
| LCP image | <200KB | Product images need quality |
| Third-party scripts | <400KB | Analytics, ads, chat |

### Content/Blog Sites
| Resource | Budget | Rationale |
|----------|--------|-----------|
| Total page weight | <1.5MB | Text-focused |
| JavaScript | <200KB | Minimal interactivity |
| LCP image | <150KB | Hero images |

### Marketing/Landing Pages
| Resource | Budget | Rationale |
|----------|--------|-----------|
| Total page weight | <1MB | Speed is conversion |
| JavaScript | <150KB | Minimal |
| LCP image | <100KB | Aggressive optimization |

**Present current vs recommended:**
> "JavaScript: 920KB (budget: 300KB) - 206% over budget"

---

## Example Report Templates

Adapt based on your findings -- add sections for unique insights, remove sections that don't apply.

### Example A: Multi-Page Analysis with Template Patterns
Use when analyzing multiple pages with clear template groupings:
- Core Web Vitals Status (Mobile/Desktop/CrUX tables)
- Site-Wide Issues (issues affecting ALL pages)
- Template-Specific Issues (grouped by template)
- Page-Specific Issues (unique to individual pages)
- Prioritized Action Plan (Immediate/Short-term/Medium-term)
- Technical Details
- Recommendations Summary

### Example B: Single Page Deep Dive
Use when analyzing 1-2 pages in depth:
- Core Web Vitals Status
- LCP Deep Dive (TTFB, resource load, render delay breakdown)
- INP/TBT Analysis (main thread blocking analysis)
- CLS Analysis (layout shift sources)
- Network Analysis (resource breakdown)
- Prioritized Recommendations

### Example C: Competitive Comparison
Use when CrUX data shows competitive positioning:
- Competitive Positioning Summary
- Core Web Vitals vs Competitors
- Opportunities to Outperform
- Recommendations by Impact

Choose or combine structures based on what your analysis reveals. The goal is **actionable insights**, not rigid formatting.
