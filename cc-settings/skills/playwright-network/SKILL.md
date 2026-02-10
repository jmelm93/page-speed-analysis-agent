---
name: playwright-network
description: >
  Capture network waterfall data and performance timing using Playwright. Measures
  actual page load time, request counts, transfer sizes, and identifies blocking
  resources. Provides real browser measurements complementing API-based metrics.
---

# Playwright Network Capture Skill

Captures detailed network activity and performance timing by loading a page in
a real browser (headless Chromium). Provides ground-truth measurements of how
the page actually loads.

## When to Use

- Measuring actual page load time in a real browser
- Analyzing network waterfall (what loads when)
- Identifying largest resources and potential optimization targets
- Detecting render-blocking resources
- Getting request counts and transfer sizes by resource type

## Usage

### Capture Network Data

```bash
python {baseDir}/scripts/capture_network.py \
  --url "https://example.com" \
  --output ./network_data.json
```

### With Custom Timeout

```bash
python {baseDir}/scripts/capture_network.py \
  --url "https://example.com" \
  --timeout 60000 \
  --output ./network_data.json
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--url` | Yes | - | URL to analyze |
| `--output` | No | stdout | Output file path for JSON results |
| `--timeout` | No | `30000` | Page load timeout in milliseconds |
| `--viewport-width` | No | `1280` | Browser viewport width |
| `--viewport-height` | No | `720` | Browser viewport height |

## Output Format

```json
{
  "success": true,
  "url": "https://example.com",
  "timing": {
    "navigation_start": 0,
    "dom_content_loaded": 1250,
    "load_event": 2800,
    "time_to_first_byte": 320,
    "dom_interactive": 1100,
    "total_load_time_ms": 2800
  },
  "summary": {
    "total_requests": 45,
    "total_transfer_bytes": 1524000,
    "total_transfer_mb": 1.45,
    "by_type": {
      "document": {"count": 1, "bytes": 45000},
      "script": {"count": 12, "bytes": 450000},
      "stylesheet": {"count": 4, "bytes": 85000},
      "image": {"count": 20, "bytes": 890000},
      "font": {"count": 5, "bytes": 120000},
      "xhr": {"count": 3, "bytes": 34000}
    }
  },
  "largest_resources": [
    {
      "url": "https://example.com/images/hero.jpg",
      "type": "image",
      "size_bytes": 524288,
      "size_kb": 512,
      "duration_ms": 450
    },
    {
      "url": "https://example.com/js/bundle.js",
      "type": "script",
      "size_bytes": 245000,
      "size_kb": 239,
      "duration_ms": 320
    }
  ],
  "blocking_resources": [
    {
      "url": "https://example.com/css/main.css",
      "type": "stylesheet",
      "size_bytes": 45000,
      "blocks": "render"
    }
  ],
  "waterfall": [
    {
      "url": "https://example.com/",
      "type": "document",
      "start_time": 0,
      "duration_ms": 320,
      "size_bytes": 45000,
      "status": 200
    }
  ]
}
```

## Understanding the Output

### Timing Metrics

- `time_to_first_byte`: Server response time (first byte received)
- `dom_content_loaded`: HTML parsed, DOM ready (scripts may still be loading)
- `dom_interactive`: DOM is interactive
- `load_event`: All resources loaded (images, scripts, stylesheets)
- `total_load_time_ms`: Complete page load time

### Resource Types

- `document`: The HTML page itself
- `script`: JavaScript files
- `stylesheet`: CSS files
- `image`: Images (jpg, png, gif, svg, webp)
- `font`: Web fonts (woff, woff2, ttf)
- `xhr`: AJAX/fetch requests
- `other`: Everything else

### Largest Resources

Top 10 resources by transfer size. These are prime candidates for optimization
(compression, lazy loading, code splitting).

### Blocking Resources

Stylesheets and scripts in `<head>` that block initial render. Reducing these
improves First Contentful Paint (FCP) and Largest Contentful Paint (LCP).

## Error Handling

```json
{
  "success": false,
  "url": "https://example.com",
  "error": "Navigation timeout: page did not load within 30000ms"
}
```

## Notes

- Uses headless Chromium for consistent measurements
- Network data includes timing for each resource
- Identifies render-blocking CSS/JS in document head
- Large resources (>100KB) are flagged in largest_resources
- Waterfall includes up to 100 requests (sorted by start time)
