"""Page Speed Analyzer - Core analysis engine.

Orchestrates Claude Code SDK to analyze page speed using custom skills.
No LangGraph, no Engine base class, no Firebase - standalone execution.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .client import run_claude_code, ClaudeCodeResult
from .models import PageSpeedRequest

import logging

logger = logging.getLogger(__name__)

# Resolve project root (page_speed_analyzer_agent/ directory)
PROJECT_ROOT = Path(__file__).parent.parent


def build_task_prompt(request: PageSpeedRequest) -> str:
    """Build the task prompt for the Claude Code agent.

    Args:
        request: Page speed analysis request with URLs and options

    Returns:
        Formatted prompt string for the agent
    """
    urls_list = "\n".join(f"- {url}" for url in request.get_urls())

    strategy_text = {
        "mobile": "mobile only",
        "desktop": "desktop only",
        "both": "both mobile and desktop",
    }.get(request.strategy, "both mobile and desktop")

    screenshot_text = (
        "Take screenshots of each page to help visualize the LCP element and any layout shift issues."
        if request.include_screenshots
        else "Screenshots are not requested for this analysis."
    )

    network_text = (
        "Capture network waterfall data using playwright-network to identify specific resources causing issues."
        if request.include_network_waterfall
        else "Network waterfall capture is not requested for this analysis."
    )

    api_validation_text = """
## API Validation (FIRST STEP)

Before collecting data, run a SINGLE test request to verify APIs are working:

1. Test PageSpeed Insights API with the first URL
2. If 403/401 error → STOP IMMEDIATELY and report API configuration error
3. If successful → proceed with full analysis

This prevents wasting time on a run that will fail due to API issues.

**If you encounter a 403 or 401 error from PageSpeed Insights or CrUX API:**
- Do NOT continue with partial data
- Report the error clearly with instructions to enable the API in Google Cloud Console
- Do NOT generate an Excel report with incomplete data
"""

    # Template-aware analysis (if any templates provided)
    template_mapping = request.get_template_mapping()
    multi_page_text = ""
    if template_mapping:
        template_json = json.dumps(template_mapping, indent=2)
        multi_page_text = f"""
## Template-Aware Analysis

The user has provided template groupings. Analyze issues at THREE levels:

1. **Site-Wide Issues** - Problems on ALL pages regardless of template
   (shared scripts, server config, fonts, CDN)

2. **Template-Specific Issues** - Problems affecting all pages of a specific template type
   (template JS/CSS, layout patterns, shared images)

3. **Page-Specific Issues** - Problems unique to individual pages
   (specific hero images, embedded content)

**Template Mapping:**
```json
{template_json}
```

Group your findings by template type. For template-specific issues, note which
template is affected and how many pages use that template.

**Output Structure for Template Analysis:**
```markdown
## Site-Wide Issues (All X Pages)
[Issues affecting every page]

## Template-Specific Issues

### Blog Posts (Y pages)
[Issues affecting all blog posts]

### Programs Category (Z pages)
[Issues affecting all program category pages]

## Page-Specific Issues
### [specific URL]
[Unique issues for this page]
```
"""
    elif len(request.get_urls()) > 1:
        multi_page_text = """
## Multi-Page Analysis

You are analyzing multiple pages. Look for patterns:
- **Template-level issues**: Problems that appear on ALL pages (shared CSS/JS, server config, fonts)
- **Page-specific issues**: Problems unique to one page (large hero image, embedded content)

Prioritize template-level fixes as they benefit all pages when fixed once.
"""

    # Resolve the Excel generation script path
    excel_script = PROJECT_ROOT / "cc-settings" / "skills" / "generate-excel-report" / "scripts" / "generate_excel.py"

    return f"""# Page Speed Analysis Task

Analyze the following URLs for Core Web Vitals and page speed issues:

{urls_list}

## Analysis Strategy
Analyze {strategy_text} performance.

{api_validation_text}

## Instructions (Follow EXACTLY in Order)

### Step 1: Gather Data
- Run `pagespeed-insights` for each URL with strategy "{request.strategy}"
- Run `crux-data` for each URL to get real user metrics (it's OK if some URLs aren't in CrUX)
- {network_text}
- {screenshot_text}

### Step 2: Generate Excel Report (MANDATORY)
After collecting ALL data, you MUST generate an Excel report before writing markdown:

1. Use the Write tool to save collected data to `collected_data.json`.

   **CRITICAL FORMAT REQUIREMENT:** The JSON must contain the ACTUAL DATA inline (not file paths).
   Read each saved PSI/network JSON file and combine the data into this exact structure:

   ```json
   {{
     "urls": ["https://example.com", "https://example.com/page"],
     "psi_results": [
       {{
         "url": "https://example.com",
         "strategies": {{
           "mobile": {{
             "performance_score": 65,
             "core_web_vitals": {{ "lcp": {{ "value": 4.2, "unit": "s", "status": "poor" }} }},
             "field_metrics": {{ "lcp_p75": 2.5 }},
             "opportunities": [{{ "title": "...", "savings_ms": 1200 }}]
           }},
           "desktop": {{ ... }}
         }}
       }}
     ],
     "network_results": [
       {{
         "url": "https://example.com",
         "total_requests": 45,
         "total_transfer_bytes": 1524000,
         "by_type": {{ "script": {{ "count": 15, "transfer_bytes": 500000 }} }},
         "largest_resources": [{{ "url": "...", "transfer_bytes": 200000 }}]
       }}
     ]
   }}
   ```

   **DO NOT write file paths** (like `"./psi_homepage.json"`) - include the actual data objects.
   The Excel script parses `psi_results` and `network_results` arrays directly.

2. Run the Excel generation script:
   ```bash
   python {excel_script} --data ./collected_data.json --output-dir ./output
   ```

3. Verify the output shows `"success": true` and a `file_path`. If not, debug before proceeding.

### Prerequisite Check (BEFORE writing report)
Answer these before proceeding to the report:
1. Do you have PSI data for all URLs? (Yes/No)
2. Do you have Network waterfall data for all URLs? (Yes/No)
3. Did you write `collected_data.json` with inline data (not file paths)? (Yes/No)
4. Did you run the Excel generation script? (Yes/No)
5. Do you have a local `.xlsx` file path in `./output/`? (Yes/No)

**If ANY answer is "No", STOP and complete the missing step. Do not write the report.**

### Step 3: Analyze Root Causes
- Don't just report metrics - explain WHY each metric is good or bad
- Connect specific resources (images, scripts) to specific metrics (LCP, TBT)
- Compare lab data vs field data to understand real user experience

### Step 4: Prioritize Recommendations
- Order by estimated impact (use savings_ms from PSI opportunities)
- Indicate effort level (simple vs complex)
- Be specific: "Compress hero.jpg from 2.3MB to ~400KB" not "optimize images"
{multi_page_text}
## Output Format

**CRITICAL OUTPUT RULES:**
1. **NO PREAMBLE** - Do NOT start with "Perfect!", "I've completed...", "Here's what was delivered"
2. **START DIRECTLY** with: `# [Site] Page Speed Analysis Report`
3. **OUTPUT THE FULL REPORT** - Not a summary of findings

Your response = The complete markdown report. No conversational text.

**Minimum required elements:**
- Executive Summary with overall health assessment
- Excel Report reference: `**[Download Full Excel Report](./output/filename.xlsx)**`
- Core Web Vitals data for all URLs (lab and field if available)
- Root cause analysis of key issues
- Prioritized recommendations with estimated impact

**Structure guidelines:**
- Adapt based on your findings - add sections for unique insights
- Group issues by scope (site-wide vs template-specific vs page-specific) when patterns emerge
- Include Technical Details when network analysis reveals specific blocking resources
- See `references/ANALYSIS_REFERENCE.md` for example report templates

**The report should be comprehensive (2000-4000 words for multi-URL analysis).**
Include ALL relevant data, ALL URLs, ALL actionable recommendations.

Focus on actionable insights, not just data dumps. A developer reading your report
should know exactly what to fix first and why.
"""


def _extract_excel_path(markdown: str) -> Optional[str]:
    """Extract Excel file path from markdown report.

    Looks for local .xlsx file paths in the report content.

    Args:
        markdown: The markdown report content

    Returns:
        Excel file path if found, None otherwise
    """
    # Match local .xlsx paths like ./output/page_speed_analysis_20260209.xlsx
    pattern = r'[./\w-]+\.xlsx'
    match = re.search(pattern, markdown)
    return match.group(0) if match else None


def _build_cost_table(result: ClaudeCodeResult) -> str:
    """Build cost/metrics table for report header.

    Args:
        result: SDK execution result with metadata

    Returns:
        Formatted markdown cost table
    """
    cost = result.total_cost_usd or 0
    turns = result.num_turns or 0
    duration_ms = result.duration_ms or 0
    duration_sec = duration_ms / 1000 if duration_ms else 0

    return f"""---
## Analysis Metrics

| Metric | Value |
|--------|-------|
| **API Cost** | ${cost:.4f} |
| **Agent Turns** | {turns} |
| **Processing Time** | {duration_sec:.1f}s |

---"""


async def analyze_pages(request: PageSpeedRequest) -> Dict[str, Any]:
    """Run page speed analysis using Claude Code SDK.

    This is the main entry point. It:
    1. Builds the task prompt from the request
    2. Invokes the Claude Code SDK with custom skills
    3. Post-processes the result (cost table, Excel path extraction)
    4. Saves the markdown report to ./output/

    Args:
        request: Page speed analysis request with URLs and options

    Returns:
        Dict with keys: markdown, markdown_path, excel_path, cost_usd, duration_sec
    """
    cc_settings_dir = PROJECT_ROOT / "cc-settings"
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)

    # Build task prompt
    prompt = build_task_prompt(request)

    urls = request.get_urls()
    urls_str = ", ".join(urls[:3])
    if len(urls) > 3:
        urls_str += f" (+{len(urls) - 3} more)"

    logger.info(f"Starting page speed analysis for: {urls_str}")

    # Run Claude Code SDK
    result = await run_claude_code(
        prompt=prompt,
        cc_settings_dir=cc_settings_dir,
        working_dir=PROJECT_ROOT,
        allowed_tools=["Skill", "Read", "Write", "Bash", "Glob", "Grep", "TodoWrite"],
        max_turns=150,
        model=request.model_override or "claude-sonnet-4-5",
    )

    if result.is_error:
        raise RuntimeError(f"Page speed analysis failed: {result.result}")

    # Check for skill execution failure marker
    if result.result.strip().startswith("SKILL_EXECUTION_FAILED:"):
        raise RuntimeError(f"Skill execution failed: {result.result}")

    raw_markdown = result.result

    # Post-process: extract Excel path
    excel_path = _extract_excel_path(raw_markdown)
    if not excel_path:
        logger.warning("Excel file path not found in report")

    # Post-process: validate report
    if len(raw_markdown) < 500:
        raise RuntimeError("Report too short - analysis may have failed")

    word_count = len(raw_markdown.split())
    if word_count < 1500:
        logger.warning(f"Report may be truncated: only {word_count} words (expected 2000+)")

    # Build cost table and prepend
    cost_table = _build_cost_table(result)
    final_markdown = f"{cost_table}\n\n{raw_markdown}"

    # Save markdown report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"page_speed_report_{timestamp}.md"
    report_path = output_dir / report_filename
    report_path.write_text(final_markdown, encoding="utf-8")

    logger.info(
        f"Analysis complete. Turns: {result.num_turns}, "
        f"Cost: ${result.total_cost_usd or 0:.4f}, "
        f"Report: {report_path}"
    )

    return {
        "markdown": final_markdown,
        "markdown_path": str(report_path),
        "excel_path": excel_path,
        "cost_usd": result.total_cost_usd or 0,
        "duration_sec": (result.duration_ms or 0) / 1000,
    }
