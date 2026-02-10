# LCP Deep Dive & Diagnostic Reference

Reference this when diagnosing specific Core Web Vital issues, investigating LCP bottlenecks, or explaining lab vs field data discrepancies.

---

## LCP Subparts Analysis

When LCP is slow, diagnose which phase is the bottleneck:

### 1. TTFB (Time to First Byte)
- **Target**: <800ms
- **If slow**: Server optimization, CDN, HTML caching
- **Check**: `server-response-time` in PSI audits

### 2. Resource Load Delay (TTFB -> LCP request start)
- **Target**: <100ms
- **If slow**: LCP resource not discoverable in HTML, blocked by CSS/JS
- **Check**: Is the LCP image in HTML or loaded via CSS/JS?

### 3. Resource Load Time (LCP request start -> download complete)
- **Target**: Depends on resource size
- **If slow**: Large image, slow CDN, missing HTTP/2
- **Check**: Image file size, CDN performance

### 4. Element Render Delay (download -> paint)
- **Target**: <100ms
- **If slow**: Render-blocking CSS, heavy JS, lazy-loaded LCP element
- **Check**: `render-blocking-resources` audit

**Present subparts in analysis:**
> "LCP is 4.2s broken down: TTFB 1.2s (slow server) + Load Delay 0.3s + Load Time 2.1s (1.3MB image) + Render Delay 0.6s"

---

## Interpreting Lab vs Field Discrepancies

When lab and field data differ significantly, explain WHY:

| Scenario | Likely Cause | What to Recommend |
|----------|--------------|-------------------|
| Field LCP much **better** than Lab | CDN caching, return visitors | Focus on first-visit experience optimization |
| Field LCP **worse** than Lab | Real-world network variation, slower devices | Prioritize mobile optimizations |
| Field INP worse than Lab | Real user interactions differ from lab | Investigate specific interaction patterns |
| Field CLS worse than Lab | Dynamic content loads after scroll | Check above-fold vs full-page CLS sources |

---

## Common Fixes Reference

| Issue | Metric Affected | Typical Fix | Est. Impact |
|-------|-----------------|-------------|-------------|
| Large images | LCP | WebP/AVIF, responsive images, compression | 30-70% size reduction |
| Render-blocking CSS | LCP, FCP | Critical CSS inlining, async loading | 0.3-1.0s |
| Render-blocking JS | LCP, FCP, TBT | async/defer, code splitting | 0.2-0.8s |
| Slow TTFB | LCP | CDN, server optimization, caching | 0.2-1.0s |
| Layout shifts from images | CLS | width/height attributes | CLS reduction |
| Web font shifts | CLS | font-display: swap, preload | CLS reduction |
| Heavy JavaScript | INP, TBT | Code splitting, tree shaking | 20-50% reduction |
| Third-party scripts | INP, TBT | Lazy load, facade pattern | Variable |
