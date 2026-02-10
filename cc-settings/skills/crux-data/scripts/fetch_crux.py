#!/usr/bin/env python3
"""Chrome UX Report (CrUX) API skill.

Fetches real user metrics from Google's CrUX API. Returns 28-day rolling
average of actual user experience data collected from Chrome browsers.

Usage:
    python fetch_crux.py --url "https://example.com/page"
    python fetch_crux.py --origin "https://example.com" --form-factor "PHONE"
"""
import argparse
import json
import os
import sys
from typing import Any

import aiohttp
import asyncio


# Core Web Vitals thresholds (same as PSI)
CWV_THRESHOLDS = {
    "largest_contentful_paint": {"good": 2500, "poor": 4000, "unit": "ms", "display": "s"},
    "interaction_to_next_paint": {"good": 200, "poor": 500, "unit": "ms", "display": "ms"},
    "cumulative_layout_shift": {"good": 0.1, "poor": 0.25, "unit": "", "display": ""},
    "first_contentful_paint": {"good": 1800, "poor": 3000, "unit": "ms", "display": "s"},
    "experimental_time_to_first_byte": {"good": 800, "poor": 1800, "unit": "ms", "display": "s"},
    "first_input_delay": {"good": 100, "poor": 300, "unit": "ms", "display": "ms"},
}

# Map CrUX metric names to display names
METRIC_DISPLAY_NAMES = {
    "largest_contentful_paint": "lcp",
    "interaction_to_next_paint": "inp",
    "cumulative_layout_shift": "cls",
    "first_contentful_paint": "fcp",
    "experimental_time_to_first_byte": "ttfb",
    "first_input_delay": "fid",
}


def get_status(metric_key: str, p75_value: float) -> str:
    """Determine status (good/needs_improvement/poor) for a metric value."""
    thresholds = CWV_THRESHOLDS.get(metric_key, {})
    good = thresholds.get("good", float("inf"))
    poor = thresholds.get("poor", float("inf"))

    if p75_value <= good:
        return "good"
    elif p75_value <= poor:
        return "needs_improvement"
    else:
        return "poor"


def convert_p75(metric_key: str, value: float) -> tuple[float, str]:
    """Convert p75 value to display unit."""
    thresholds = CWV_THRESHOLDS.get(metric_key, {})
    display = thresholds.get("display", "ms")

    if display == "s":
        return round(value / 1000, 2), "s"
    elif display == "ms":
        return round(value, 0), "ms"
    else:
        return round(value, 3), ""


def parse_histogram(histogram: list[dict]) -> dict:
    """Parse CrUX histogram into good/needs_improvement/poor percentages."""
    if not histogram or len(histogram) < 3:
        return {}

    # CrUX API returns density values as strings - convert to float
    return {
        "good": round(float(histogram[0].get("density", 0)), 3),
        "needs_improvement": round(float(histogram[1].get("density", 0)), 3),
        "poor": round(float(histogram[2].get("density", 0)), 3),
    }


def parse_crux_metrics(record: dict) -> dict:
    """Parse CrUX record into structured metrics."""
    metrics_data = record.get("metrics", {})
    parsed = {}

    for metric_key, metric_data in metrics_data.items():
        metric_key_lower = metric_key.lower()

        if metric_key_lower not in METRIC_DISPLAY_NAMES:
            continue

        display_name = METRIC_DISPLAY_NAMES[metric_key_lower]

        # Get p75 percentile (CrUX API returns values as strings - convert to float)
        percentiles = metric_data.get("percentiles", {})
        p75_raw = float(percentiles.get("p75", 0))

        # Convert to display units
        p75_display, unit = convert_p75(metric_key_lower, p75_raw)

        # Get distribution
        histogram = metric_data.get("histogram", [])
        distribution = parse_histogram(histogram)

        # Determine status
        status = get_status(metric_key_lower, p75_raw)

        parsed[display_name] = {
            "p75": p75_display,
            "p75_raw": p75_raw,
            "unit": unit,
            "status": status,
            "distribution": distribution,
        }

    return parsed


async def fetch_crux(
    url: str | None,
    origin: str | None,
    form_factor: str,
    api_key: str | None,
) -> dict:
    """Fetch CrUX data for a URL or origin.

    Args:
        url: Specific URL to query (mutually exclusive with origin)
        origin: Origin (domain) to query (mutually exclusive with url)
        form_factor: PHONE, DESKTOP, TABLET, or ALL_FORM_FACTORS
        api_key: Google API key

    Returns:
        Dict with CrUX metrics and distributions
    """
    base_url = "https://chromeuxreport.googleapis.com/v1/records:queryRecord"

    # Build request body
    body: dict[str, Any] = {}

    if url:
        body["url"] = url
        query_type = "url"
        query_value = url
    elif origin:
        body["origin"] = origin
        query_type = "origin"
        query_value = origin
    else:
        return {
            "success": False,
            "error": "Either --url or --origin is required",
        }

    if form_factor != "ALL_FORM_FACTORS":
        body["formFactor"] = form_factor

    # Build URL with API key
    request_url = base_url
    if api_key:
        request_url = f"{base_url}?key={api_key}"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            request_url,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status == 404:
                # Not found in CrUX - this is normal for many sites
                return {
                    "success": True,
                    "query_type": query_type,
                    "query_value": query_value,
                    "form_factor": form_factor,
                    "in_crux": False,
                    "reason": "The requested URL or origin does not have enough data in CrUX",
                }

            if response.status != 200:
                error_text = await response.text()
                return {
                    "success": False,
                    "error": f"API request failed: {response.status} - {error_text[:200]}",
                }

            data = await response.json()

    record = data.get("record", {})

    # Extract collection period
    collection_period = record.get("collectionPeriod", {})
    first_date = collection_period.get("firstDate", {})
    last_date = collection_period.get("lastDate", {})

    period = {
        "first_date": f"{first_date.get('year', '')}-{first_date.get('month', ''):02d}-{first_date.get('day', ''):02d}",
        "last_date": f"{last_date.get('year', '')}-{last_date.get('month', ''):02d}-{last_date.get('day', ''):02d}",
    }

    # Parse metrics
    metrics = parse_crux_metrics(record)

    return {
        "success": True,
        "query_type": query_type,
        "query_value": query_value,
        "form_factor": form_factor,
        "in_crux": True,
        "collection_period": period,
        "metrics": metrics,
    }


async def main():
    """Main entry point for the CrUX skill."""
    parser = argparse.ArgumentParser(
        description="Fetch Chrome UX Report (CrUX) data"
    )
    parser.add_argument("--url", help="Specific URL to query")
    parser.add_argument("--origin", help="Origin (domain) to query")
    parser.add_argument(
        "--form-factor",
        default="PHONE",
        choices=["PHONE", "DESKTOP", "TABLET", "ALL_FORM_FACTORS"],
        help="Device form factor",
    )
    parser.add_argument("--output", help="Output file path for JSON results")
    parser.add_argument("--api-key", help="Google API key")
    args = parser.parse_args()

    if not args.url and not args.origin:
        print(json.dumps({
            "success": False,
            "error": "Either --url or --origin is required"
        }))
        return 1

    api_key = args.api_key or os.environ.get("GOOGLE_PAGESPEED_API_KEY")

    try:
        result = await fetch_crux(
            url=args.url,
            origin=args.origin,
            form_factor=args.form_factor,
            api_key=api_key,
        )
    except asyncio.TimeoutError:
        result = {"success": False, "error": "Request timed out"}
    except Exception as e:
        result = {"success": False, "error": str(e)}

    output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
