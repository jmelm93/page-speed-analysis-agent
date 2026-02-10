# Page Speed Analyzer Agent

An autonomous AI-powered page speed analysis tool that generates comprehensive Core Web Vitals reports. Powered by the Claude Code SDK, it orchestrates multiple data collection skills (PageSpeed Insights, CrUX, Playwright network capture) and produces a detailed markdown report with an accompanying Excel workbook.

## What It Does

1. Fetches **Google PageSpeed Insights** data (lab metrics, opportunities, diagnostics)
2. Fetches **Chrome UX Report (CrUX)** field data (real user metrics)
3. Captures **network waterfall** data via Playwright (resource sizes, timing, blocking resources)
4. Generates a **4-sheet Excel workbook** (Summary, Core Web Vitals, Network Analysis, Opportunities)
5. Produces a **comprehensive markdown report** with root cause analysis and prioritized recommendations

All of this runs autonomously - you configure the URLs, run the script, and get back a complete analysis.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Claude Code CLI** (`npm install -g @anthropic-ai/claude-code`)
- **Anthropic API key** (for Claude)
- **Google API key** (for PageSpeed Insights and CrUX APIs)

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright browser

```bash
playwright install chromium
```

### 3. Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### 4. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)
- `GOOGLE_PAGESPEED_API_KEY` - Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
  - Enable **PageSpeed Insights API** and **Chrome UX Report API** in your Google Cloud project

### 5. Configure URLs

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` with your URLs (see [Configuration](#configuration) below).

## Usage

### 1. Edit your URLs

Open `config.yaml` and add your URLs:

```yaml
urls:
  - url: "https://yoursite.com"
    template_type: "homepage"
  - url: "https://yoursite.com/blog/post-1"
    template_type: "blog-post"
  - url: "https://yoursite.com/products"
    template_type: "category"
```

The `template_type` is optional but recommended for multi-page analysis - it enables the agent to identify template-level vs page-specific issues.

### 2. Choose analysis strategy

In `config.yaml`:

```yaml
strategy: "both"  # "mobile", "desktop", or "both"
```

### 3. Run the analysis

```bash
python run.py
```

The analysis typically takes 3-10 minutes depending on the number of URLs.

## Output

Reports are saved to the `./output/` directory:

- **Markdown report**: `output/page_speed_report_YYYYMMDD_HHMMSS.md`
- **Excel workbook**: `output/page_speed_analysis_YYYYMMDD_HHMMSS.xlsx`

### Excel Workbook Sheets

| Sheet | Contents |
|-------|----------|
| **Summary** | All URL scores at a glance (mobile/desktop scores, CWV status, top issue) |
| **Core Web Vitals** | Full metrics breakdown with lab and field data |
| **Network Analysis** | Resource details by type (scripts, images, CSS, fonts) |
| **Opportunities** | All PSI recommendations with estimated savings |

## Configuration

All configuration lives in `config.yaml`. Available options:

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `strategy` | `"mobile"`, `"desktop"`, `"both"` | `"both"` | Which device strategies to analyze |
| `template_type` | Any string | `""` | Groups URLs by template for pattern detection |
| `include_network_waterfall` | `true`/`false` | `true` | Capture network data via Playwright |
| `include_screenshots` | `true`/`false` | `false` | Capture page screenshots (experimental) |
| `model_override` | Model ID string | `null` | Override the Claude model used |

To enable advanced options, uncomment them in `config.yaml`:

```yaml
urls:
  - url: "https://yoursite.com"
    template_type: "homepage"

strategy: "both"
include_network_waterfall: true
model_override: "claude-sonnet-4-5"
```

## How It Works

This tool uses the **Claude Code SDK** to orchestrate an autonomous AI agent. The agent:

1. Receives a structured prompt with your URLs and analysis requirements
2. Invokes specialized skills (Python scripts) to collect data from Google APIs and Playwright
3. Generates an Excel workbook from the collected data
4. Writes a comprehensive markdown report with root cause analysis

The agent runs in a sandboxed environment with access to specific tools (file read/write, bash execution, skill invocation).

## Troubleshooting

### "API not enabled" or 403 errors
- Ensure both **PageSpeed Insights API** and **Chrome UX Report API** are enabled in your Google Cloud project
- Verify your `GOOGLE_PAGESPEED_API_KEY` is correct in `.env`

### "claude-agent-sdk not installed"
```bash
pip install claude-agent-sdk
```

### "Browser not installed" (Playwright)
```bash
playwright install chromium
```

### "Claude Code CLI not found"
```bash
npm install -g @anthropic-ai/claude-code
```

### CrUX returns "not in CrUX"
This is normal for low-traffic sites. The analysis will continue with lab data only.

### Analysis seems stuck
The agent may take several minutes per URL, especially with network waterfall capture. For 5+ URLs, expect 10-15 minutes.

## Cost

Each analysis run uses the Anthropic API. Typical costs:
- **1-2 URLs**: ~$0.50-1.00
- **5-10 URLs**: ~$1.00-3.00

Actual costs depend on the complexity of findings and report length. The cost is displayed after each run.

## License

MIT
