---
name: crux-data
description: >
  Fetch Chrome UX Report (CrUX) real user data for a URL or origin. Returns 28-day
  rolling average of actual user metrics including LCP, INP, CLS distributions.
  Only available for sites with sufficient Chrome traffic.
---

# CrUX Data Skill

Fetches real user metrics from Google's Chrome UX Report API. Unlike PageSpeed
Insights lab data, CrUX provides actual field data from Chrome users visiting
the site over the past 28 days.

## When to Use

- Getting real user experience metrics (not lab simulations)
- Understanding how actual visitors experience the page
- Comparing lab data vs field data to identify discrepancies
- Checking if a site has enough traffic to be in CrUX

## Usage

### Query by URL

```bash
python {baseDir}/scripts/fetch_crux.py \
  --url "https://example.com/page"
```

### Query by Origin (Entire Domain)

```bash
python {baseDir}/scripts/fetch_crux.py \
  --origin "https://example.com" \
  --form-factor "PHONE"
```

### Get All Form Factors

```bash
python {baseDir}/scripts/fetch_crux.py \
  --url "https://example.com" \
  --form-factor "ALL_FORM_FACTORS" \
  --output ./crux_results.json
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--url` | Yes* | - | Specific URL to query |
| `--origin` | Yes* | - | Origin (domain) to query |
| `--form-factor` | No | `PHONE` | Device type: `PHONE`, `DESKTOP`, `TABLET`, or `ALL_FORM_FACTORS` |
| `--output` | No | stdout | Output file path for JSON results |
| `--api-key` | No | env var | Google API key (uses GOOGLE_PAGESPEED_API_KEY env var if not provided) |

*Either `--url` or `--origin` is required

## Output Format

```json
{
  "success": true,
  "query_type": "url",
  "query_value": "https://example.com",
  "form_factor": "PHONE",
  "in_crux": true,
  "collection_period": {
    "first_date": "2026-01-08",
    "last_date": "2026-02-04"
  },
  "metrics": {
    "lcp": {
      "p75": 2.8,
      "unit": "s",
      "status": "needs_improvement",
      "distribution": {
        "good": 0.45,
        "needs_improvement": 0.35,
        "poor": 0.20
      }
    },
    "inp": {
      "p75": 180,
      "unit": "ms",
      "status": "good",
      "distribution": {
        "good": 0.75,
        "needs_improvement": 0.20,
        "poor": 0.05
      }
    },
    "cls": {
      "p75": 0.12,
      "unit": "",
      "status": "needs_improvement",
      "distribution": {
        "good": 0.60,
        "needs_improvement": 0.30,
        "poor": 0.10
      }
    }
  }
}
```

## Understanding CrUX Data

### Metrics Included

- **LCP** (Largest Contentful Paint) - Loading performance
- **INP** (Interaction to Next Paint) - Interactivity
- **CLS** (Cumulative Layout Shift) - Visual stability
- **FCP** (First Contentful Paint) - Initial render
- **TTFB** (Time to First Byte) - Server responsiveness

### Distribution Breakdown

Each metric includes the percentage of page loads that fall into each category:
- `good`: Meets Google's Core Web Vitals threshold
- `needs_improvement`: Between good and poor thresholds
- `poor`: Fails to meet minimum threshold

### p75 Value

The 75th percentile value - 75% of users experience this value or better.
This is the value Google uses for Core Web Vitals assessment.

## Error Handling

### Site Not in CrUX

```json
{
  "success": true,
  "in_crux": false,
  "reason": "The requested URL or origin does not have enough data in CrUX"
}
```

### API Error

```json
{
  "success": false,
  "error": "API request failed: 403 Forbidden"
}
```

## Notes

- Data is a 28-day rolling average, updated daily
- Not all sites have CrUX data - requires sufficient Chrome traffic
- URL-level data may not be available even if origin-level is
- Mobile (PHONE) form factor is most relevant for Google rankings
