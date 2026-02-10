#!/usr/bin/env python3
"""Playwright network capture skill.

Captures network waterfall data and performance timing by loading a page
in a real headless browser. Provides actual load times and resource analysis.

Usage:
    python capture_network.py --url "https://example.com" --output network.json
"""
import argparse
import json
import sys
import asyncio
from dataclasses import dataclass, field

try:
    from playwright.async_api import async_playwright, Request, Response  # noqa: F401
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Playwright not installed. Run: pip install playwright && playwright install chromium"
    }))
    sys.exit(1)


@dataclass
class RequestData:
    """Data captured for a network request."""
    url: str
    resource_type: str
    start_time: float = 0
    end_time: float = 0
    duration_ms: float = 0
    size_bytes: int = 0
    status: int = 0
    from_cache: bool = False


def get_resource_type(request: Request) -> str:
    """Map Playwright resource type to simplified category."""
    resource_type = request.resource_type

    type_map = {
        "document": "document",
        "script": "script",
        "stylesheet": "stylesheet",
        "image": "image",
        "font": "font",
        "xhr": "xhr",
        "fetch": "xhr",
        "media": "media",
        "websocket": "websocket",
        "manifest": "other",
        "other": "other",
    }

    return type_map.get(resource_type, "other")


async def capture_network(
    url: str,
    timeout: int = 30000,
    viewport_width: int = 1280,
    viewport_height: int = 720,
) -> dict:
    """Capture network activity and timing for a URL.

    Args:
        url: URL to load and analyze
        timeout: Page load timeout in milliseconds
        viewport_width: Browser viewport width
        viewport_height: Browser viewport height

    Returns:
        Dict with timing, summary, resources, and waterfall data
    """
    request_map: dict[str, RequestData] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height}
        )
        page = await context.new_page()

        # Track requests
        def on_request(request: Request):
            req_data = RequestData(
                url=request.url,
                resource_type=get_resource_type(request),
            )
            request_map[request.url] = req_data

        # Track responses
        def on_response(response: Response):
            req_url = response.request.url
            if req_url in request_map:
                req_data = request_map[req_url]
                req_data.status = response.status
                req_data.from_cache = response.from_service_worker

                # Try to get content length from headers
                content_length = response.headers.get("content-length")
                if content_length:
                    try:
                        req_data.size_bytes = int(content_length)
                    except ValueError:
                        pass

        page.on("request", on_request)
        page.on("response", on_response)

        try:
            # Navigate and wait for load
            await page.goto(url, timeout=timeout, wait_until="load")

            # Get performance timing from the page
            timing = await page.evaluate('''() => {
                const t = performance.timing;
                const nav = performance.getEntriesByType("navigation")[0];

                return {
                    navigation_start: t.navigationStart,
                    response_start: t.responseStart,
                    dom_content_loaded: t.domContentLoadedEventEnd,
                    dom_interactive: t.domInteractive,
                    load_event: t.loadEventEnd,
                    // Computed metrics
                    time_to_first_byte: t.responseStart - t.navigationStart,
                    dom_content_loaded_time: t.domContentLoadedEventEnd - t.navigationStart,
                    dom_interactive_time: t.domInteractive - t.navigationStart,
                    total_load_time_ms: t.loadEventEnd - t.navigationStart,
                }
            }''')

            # Get resource timing entries
            resource_timing = await page.evaluate('''() => {
                const entries = performance.getEntriesByType("resource");
                return entries.map(e => ({
                    name: e.name,
                    start_time: e.startTime,
                    duration: e.duration,
                    transfer_size: e.transferSize || 0,
                    encoded_body_size: e.encodedBodySize || 0,
                    initiator_type: e.initiatorType,
                }));
            }''')

            # Update request data with resource timing
            for entry in resource_timing:
                entry_url = entry["name"]
                if entry_url in request_map:
                    req_data = request_map[entry_url]
                    req_data.start_time = entry["start_time"]
                    req_data.duration_ms = entry["duration"]
                    if entry["transfer_size"] > 0:
                        req_data.size_bytes = entry["transfer_size"]
                    elif entry["encoded_body_size"] > 0:
                        req_data.size_bytes = entry["encoded_body_size"]

            # Build response
            requests_list = list(request_map.values())

            # Summary by type
            by_type: dict[str, dict] = {}
            total_bytes = 0

            for req in requests_list:
                rtype = req.resource_type
                if rtype not in by_type:
                    by_type[rtype] = {"count": 0, "bytes": 0}
                by_type[rtype]["count"] += 1
                by_type[rtype]["bytes"] += req.size_bytes
                total_bytes += req.size_bytes

            # Largest resources (top 10)
            sorted_by_size = sorted(requests_list, key=lambda r: r.size_bytes, reverse=True)
            largest = [
                {
                    "url": r.url,
                    "type": r.resource_type,
                    "size_bytes": r.size_bytes,
                    "size_kb": round(r.size_bytes / 1024, 1),
                    "duration_ms": round(r.duration_ms, 0),
                }
                for r in sorted_by_size[:10]
                if r.size_bytes > 0
            ]

            # Potential blocking resources (CSS/JS loaded early)
            blocking = []
            for req in requests_list:
                if req.resource_type in ("stylesheet", "script") and req.start_time < 500:
                    blocking.append({
                        "url": req.url,
                        "type": req.resource_type,
                        "size_bytes": req.size_bytes,
                        "blocks": "render" if req.resource_type == "stylesheet" else "parser",
                    })

            # Waterfall (sorted by start time, limited to 100)
            sorted_by_time = sorted(requests_list, key=lambda r: r.start_time)[:100]
            waterfall = [
                {
                    "url": r.url,
                    "type": r.resource_type,
                    "start_time": round(r.start_time, 0),
                    "duration_ms": round(r.duration_ms, 0),
                    "size_bytes": r.size_bytes,
                    "status": r.status,
                }
                for r in sorted_by_time
            ]

            return {
                "success": True,
                "url": url,
                "timing": {
                    "navigation_start": 0,
                    "time_to_first_byte": timing.get("time_to_first_byte", 0),
                    "dom_interactive": timing.get("dom_interactive_time", 0),
                    "dom_content_loaded": timing.get("dom_content_loaded_time", 0),
                    "load_event": timing.get("total_load_time_ms", 0),
                    "total_load_time_ms": timing.get("total_load_time_ms", 0),
                },
                "summary": {
                    "total_requests": len(requests_list),
                    "total_transfer_bytes": total_bytes,
                    "total_transfer_mb": round(total_bytes / (1024 * 1024), 2),
                    "by_type": by_type,
                },
                "largest_resources": largest,
                "blocking_resources": blocking,
                "waterfall": waterfall,
            }

        except Exception as e:
            error_msg = str(e)
            if "Timeout" in error_msg:
                error_msg = f"Navigation timeout: page did not load within {timeout}ms"

            return {
                "success": False,
                "url": url,
                "error": error_msg,
            }

        finally:
            await browser.close()


async def main():
    """Main entry point for the network capture skill."""
    parser = argparse.ArgumentParser(
        description="Capture network waterfall and timing data"
    )
    parser.add_argument("--url", required=True, help="URL to analyze")
    parser.add_argument("--output", help="Output file path for JSON results")
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Page load timeout in ms"
    )
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=1280,
        help="Browser viewport width"
    )
    parser.add_argument(
        "--viewport-height",
        type=int,
        default=720,
        help="Browser viewport height"
    )
    args = parser.parse_args()

    result = await capture_network(
        url=args.url,
        timeout=args.timeout,
        viewport_width=args.viewport_width,
        viewport_height=args.viewport_height,
    )

    output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
