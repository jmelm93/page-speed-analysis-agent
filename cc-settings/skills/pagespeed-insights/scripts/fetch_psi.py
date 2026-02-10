#!/usr/bin/env python3
"""PageSpeed Insights API skill.

Fetches Core Web Vitals and performance data from Google's PageSpeed Insights API.
Returns lab data (Lighthouse), field data (CrUX), and optimization opportunities.

Usage:
    python fetch_psi.py --url "https://example.com" --strategy "mobile"
    python fetch_psi.py --url "https://example.com" --strategy "both" --output results.json
"""
import argparse
import json
import os
import sys
from typing import Any
from urllib.parse import urlencode

import aiohttp
import asyncio


# Core Web Vitals thresholds
CWV_THRESHOLDS = {
    "lcp": {"good": 2500, "poor": 4000, "unit": "ms"},  # Milliseconds
    "inp": {"good": 200, "poor": 500, "unit": "ms"},
    "cls": {"good": 0.1, "poor": 0.25, "unit": ""},
    "fcp": {"good": 1800, "poor": 3000, "unit": "ms"},
    "ttfb": {"good": 800, "poor": 1800, "unit": "ms"},
}


def get_status(metric: str, value: float) -> str:
    """Determine status (good/needs_improvement/poor) for a metric value."""
    thresholds = CWV_THRESHOLDS.get(metric.lower(), {})
    good = thresholds.get("good", float("inf"))
    poor = thresholds.get("poor", float("inf"))

    if value <= good:
        return "good"
    elif value <= poor:
        return "needs_improvement"
    else:
        return "poor"


def convert_to_display_unit(metric: str, value_ms: float) -> tuple[float, str]:
    """Convert milliseconds to appropriate display unit."""
    if metric.lower() in ("lcp", "fcp", "ttfb"):
        # Convert to seconds for display
        return round(value_ms / 1000, 2), "s"
    elif metric.lower() in ("inp", "tbt"):
        return round(value_ms, 0), "ms"
    elif metric.lower() == "cls":
        return round(value_ms, 3), ""
    else:
        return round(value_ms, 2), "ms"


def parse_lighthouse_metrics(lighthouse_result: dict) -> dict:
    """Extract Core Web Vitals and other metrics from Lighthouse result."""
    audits = lighthouse_result.get("audits", {})

    metrics = {}

    # Largest Contentful Paint
    if "largest-contentful-paint" in audits:
        lcp_ms = audits["largest-contentful-paint"].get("numericValue", 0)
        value, unit = convert_to_display_unit("lcp", lcp_ms)
        metrics["lcp"] = {
            "value": value,
            "unit": unit,
            "raw_ms": lcp_ms,
            "status": get_status("lcp", lcp_ms),
        }

    # Interaction to Next Paint (replaces FID)
    if "experimental-interaction-to-next-paint" in audits:
        inp_ms = audits["experimental-interaction-to-next-paint"].get("numericValue", 0)
        value, unit = convert_to_display_unit("inp", inp_ms)
        metrics["inp"] = {
            "value": value,
            "unit": unit,
            "raw_ms": inp_ms,
            "status": get_status("inp", inp_ms),
        }

    # Cumulative Layout Shift
    if "cumulative-layout-shift" in audits:
        cls_value = audits["cumulative-layout-shift"].get("numericValue", 0)
        metrics["cls"] = {
            "value": round(cls_value, 3),
            "unit": "",
            "raw_ms": cls_value,  # CLS is unitless
            "status": get_status("cls", cls_value),
        }

    # First Contentful Paint
    if "first-contentful-paint" in audits:
        fcp_ms = audits["first-contentful-paint"].get("numericValue", 0)
        value, unit = convert_to_display_unit("fcp", fcp_ms)
        metrics["fcp"] = {
            "value": value,
            "unit": unit,
            "raw_ms": fcp_ms,
            "status": get_status("fcp", fcp_ms),
        }

    # Time to First Byte (from server-response-time)
    if "server-response-time" in audits:
        ttfb_ms = audits["server-response-time"].get("numericValue", 0)
        value, unit = convert_to_display_unit("ttfb", ttfb_ms)
        metrics["ttfb"] = {
            "value": value,
            "unit": unit,
            "raw_ms": ttfb_ms,
            "status": get_status("ttfb", ttfb_ms),
        }

    # Total Blocking Time
    if "total-blocking-time" in audits:
        tbt_ms = audits["total-blocking-time"].get("numericValue", 0)
        value, unit = convert_to_display_unit("tbt", tbt_ms)
        metrics["tbt"] = {
            "value": value,
            "unit": unit,
            "raw_ms": tbt_ms,
        }

    # Speed Index
    if "speed-index" in audits:
        si_ms = audits["speed-index"].get("numericValue", 0)
        value, unit = convert_to_display_unit("speed_index", si_ms)
        metrics["speed_index"] = {
            "value": value,
            "unit": unit,
            "raw_ms": si_ms,
        }

    return metrics


def parse_opportunities(lighthouse_result: dict) -> list[dict]:
    """Extract optimization opportunities from Lighthouse result."""
    audits = lighthouse_result.get("audits", {})
    categories = lighthouse_result.get("categories", {})

    # Get the performance audit refs to know which audits are opportunities
    perf_audits = categories.get("performance", {}).get("auditRefs", [])
    opportunity_ids = {
        ref["id"] for ref in perf_audits
        if ref.get("group") == "load-opportunities"
    }

    opportunities = []
    for audit_id, audit in audits.items():
        if audit_id not in opportunity_ids:
            continue

        score = audit.get("score")
        if score is None or score >= 0.9:  # Skip passing audits
            continue

        details = audit.get("details", {})

        opportunity = {
            "id": audit_id,
            "title": audit.get("title", ""),
            "description": audit.get("description", ""),
        }

        # Extract potential savings
        if "overallSavingsMs" in details:
            opportunity["savings_ms"] = round(details["overallSavingsMs"])
        if "overallSavingsBytes" in details:
            opportunity["savings_bytes"] = details["overallSavingsBytes"]

        opportunities.append(opportunity)

    # Sort by potential savings (highest first)
    opportunities.sort(key=lambda x: x.get("savings_ms", 0), reverse=True)

    return opportunities


def parse_diagnostics(lighthouse_result: dict) -> list[dict]:
    """Extract diagnostic information from Lighthouse result."""
    audits = lighthouse_result.get("audits", {})

    diagnostic_ids = [
        "largest-contentful-paint-element",
        "layout-shift-elements",
        "long-tasks",
        "render-blocking-resources",
        "unused-javascript",
        "unused-css-rules",
        "modern-image-formats",
        "uses-responsive-images",
        "offscreen-images",
    ]

    diagnostics = []
    for audit_id in diagnostic_ids:
        if audit_id not in audits:
            continue

        audit = audits[audit_id]
        score = audit.get("score")

        # Include diagnostics that have issues or useful info
        if score is None or score < 0.9:
            diagnostic = {
                "id": audit_id,
                "title": audit.get("title", ""),
                "description": audit.get("description", ""),
            }

            # Try to extract the problematic element
            details = audit.get("details", {})
            items = details.get("items", [])
            if items:
                first_item = items[0]
                if "node" in first_item:
                    diagnostic["element"] = first_item["node"].get("selector", "")
                elif "url" in first_item:
                    diagnostic["resource"] = first_item["url"]

            diagnostics.append(diagnostic)

    return diagnostics


def parse_field_data(loading_experience: dict) -> dict | None:
    """Extract real user metrics from CrUX field data."""
    if not loading_experience:
        return None

    metrics = loading_experience.get("metrics", {})
    if not metrics:
        return None

    field_data = {}

    # LCP
    if "LARGEST_CONTENTFUL_PAINT_MS" in metrics:
        lcp = metrics["LARGEST_CONTENTFUL_PAINT_MS"]
        percentile = lcp.get("percentile", 0)
        field_data["lcp_p75"] = round(percentile / 1000, 2)  # Convert to seconds

    # INP (replaces FID)
    if "INTERACTION_TO_NEXT_PAINT" in metrics:
        inp = metrics["INTERACTION_TO_NEXT_PAINT"]
        field_data["inp_p75"] = inp.get("percentile", 0)
    elif "FIRST_INPUT_DELAY_MS" in metrics:  # Fallback to FID
        fid = metrics["FIRST_INPUT_DELAY_MS"]
        field_data["fid_p75"] = fid.get("percentile", 0)

    # CLS
    if "CUMULATIVE_LAYOUT_SHIFT_SCORE" in metrics:
        cls = metrics["CUMULATIVE_LAYOUT_SHIFT_SCORE"]
        field_data["cls_p75"] = round(cls.get("percentile", 0) / 100, 3)  # CLS is reported as integer

    # TTFB
    if "EXPERIMENTAL_TIME_TO_FIRST_BYTE" in metrics:
        ttfb = metrics["EXPERIMENTAL_TIME_TO_FIRST_BYTE"]
        field_data["ttfb_p75"] = round(ttfb.get("percentile", 0) / 1000, 2)

    # FCP
    if "FIRST_CONTENTFUL_PAINT_MS" in metrics:
        fcp = metrics["FIRST_CONTENTFUL_PAINT_MS"]
        field_data["fcp_p75"] = round(fcp.get("percentile", 0) / 1000, 2)

    return field_data if field_data else None


async def fetch_psi(url: str, strategy: str, api_key: str | None) -> dict:
    """Fetch PageSpeed Insights data for a URL.

    Args:
        url: URL to analyze
        strategy: 'mobile' or 'desktop'
        api_key: Google API key (optional if using env var)

    Returns:
        Dict with metrics, opportunities, diagnostics, and field data
    """
    base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
    }

    if api_key:
        params["key"] = api_key

    api_url = f"{base_url}?{urlencode(params)}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status != 200:
                error_text = await response.text()
                return {
                    "success": False,
                    "strategy": strategy,
                    "error": f"API request failed: {response.status} - {error_text[:200]}",
                }

            data = await response.json()

    # Extract Lighthouse results
    lighthouse_result = data.get("lighthouseResult", {})
    categories = lighthouse_result.get("categories", {})
    performance = categories.get("performance", {})

    # Parse all the data
    core_web_vitals = parse_lighthouse_metrics(lighthouse_result)
    opportunities = parse_opportunities(lighthouse_result)
    diagnostics = parse_diagnostics(lighthouse_result)

    # Field data (real user metrics)
    loading_experience = data.get("loadingExperience", {})
    origin_loading_experience = data.get("originLoadingExperience", {})

    field_data = parse_field_data(loading_experience)
    origin_field_data = parse_field_data(origin_loading_experience)

    return {
        "success": True,
        "strategy": strategy,
        "performance_score": round((performance.get("score", 0) or 0) * 100),
        "core_web_vitals": core_web_vitals,
        "field_data_available": field_data is not None,
        "field_metrics": field_data,
        "origin_field_metrics": origin_field_data,
        "opportunities": opportunities,
        "diagnostics": diagnostics,
    }


async def main():
    """Main entry point for the PageSpeed Insights skill."""
    parser = argparse.ArgumentParser(
        description="Fetch PageSpeed Insights data for a URL"
    )
    parser.add_argument("--url", required=True, help="URL to analyze")
    parser.add_argument(
        "--strategy",
        default="mobile",
        choices=["mobile", "desktop", "both"],
        help="Analysis strategy",
    )
    parser.add_argument("--output", help="Output file path for JSON results")
    parser.add_argument("--api-key", help="Google API key (uses GOOGLE_API_KEY env var if not provided)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GOOGLE_PAGESPEED_API_KEY")

    result = {
        "success": True,
        "url": args.url,
        "strategies": {},
    }

    strategies = ["mobile", "desktop"] if args.strategy == "both" else [args.strategy]

    for strategy in strategies:
        try:
            strategy_result = await fetch_psi(args.url, strategy, api_key)

            if not strategy_result.get("success"):
                result["success"] = False
                result["error"] = strategy_result.get("error")
                break

            result["strategies"][strategy] = strategy_result

        except asyncio.TimeoutError:
            result["success"] = False
            result["error"] = f"Timeout fetching {strategy} data"
            break
        except Exception as e:
            result["success"] = False
            result["error"] = f"Error fetching {strategy} data: {str(e)}"
            break

    output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
