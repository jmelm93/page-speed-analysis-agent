---
name: pagespeed-insights
description: >
  Fetch Google PageSpeed Insights data for a URL. Returns Core Web Vitals metrics
  (LCP, INP, CLS), performance score, and actionable opportunities for improvement.
  Includes both lab data (Lighthouse) and field data (real user metrics from CrUX).
---

# PageSpeed Insights Skill

Fetches comprehensive page speed data from Google's PageSpeed Insights API, including
Core Web Vitals, performance scores, and optimization opportunities.

## When to Use

- Analyzing Core Web Vitals (LCP, INP, CLS) for a URL
- Getting Google's official performance score
- Identifying specific optimization opportunities
- Comparing lab vs field (real user) data

## Usage

### Analyze a Single URL

```bash
python {baseDir}/scripts/fetch_psi.py \
  --url "https://example.com" \
  --strategy "mobile"
```

### Analyze with Both Mobile and Desktop

```bash
python {baseDir}/scripts/fetch_psi.py \
  --url "https://example.com" \
  --strategy "both" \
  --output ./psi_results.json
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--url` | Yes | - | URL to analyze |
| `--strategy` | No | `mobile` | Strategy: `mobile`, `desktop`, or `both` |
| `--output` | No | stdout | Output file path for JSON results |
| `--api-key` | No | env var | Google API key (uses GOOGLE_PAGESPEED_API_KEY env var if not provided) |

## Output Format

```json
{
  "success": true,
  "url": "https://example.com",
  "strategies": {
    "mobile": {
      "performance_score": 65,
      "core_web_vitals": {
        "lcp": {"value": 3.2, "unit": "s", "status": "needs_improvement"},
        "inp": {"value": 180, "unit": "ms", "status": "good"},
        "cls": {"value": 0.15, "unit": "", "status": "needs_improvement"}
      },
      "field_data_available": true,
      "field_metrics": {
        "lcp_p75": 3.5,
        "inp_p75": 200,
        "cls_p75": 0.12
      },
      "opportunities": [
        {
          "id": "properly-size-images",
          "title": "Properly size images",
          "description": "Serve images that are appropriately-sized...",
          "savings_ms": 1200,
          "savings_bytes": 524288
        }
      ],
      "diagnostics": [
        {
          "id": "largest-contentful-paint-element",
          "title": "Largest Contentful Paint element",
          "description": "The largest image or text block...",
          "element": "img.hero-banner"
        }
      ]
    }
  }
}
```

## Core Web Vitals Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤2.5s | 2.5-4.0s | >4.0s |
| INP | ≤200ms | 200-500ms | >500ms |
| CLS | ≤0.1 | 0.1-0.25 | >0.25 |

## Error Handling

On failure, returns:
```json
{
  "success": false,
  "url": "https://example.com",
  "error": "API request failed: 429 Too Many Requests"
}
```

## Notes

- API rate limit: 25,000 queries/day, 400 queries/100 seconds
- Field data (real user metrics) only available for sites in Chrome UX Report
- Lab data (Lighthouse) always available
- Mobile strategy is Google's primary ranking factor
