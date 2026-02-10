"""Page Speed Analyzer - Standalone Tool

Configure URLs in config.yaml, then run: python run.py

Prerequisites:
    1. Copy .env.example to .env and add your API keys
    2. Copy config.example.yaml to config.yaml and add your URLs
    3. pip install -r requirements.txt
    4. playwright install chromium
    5. npm install -g @anthropic-ai/claude-code
"""

import asyncio
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from analyzer.engine import analyze_pages
from analyzer.models import PageSpeedRequest, UrlTemplate

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> PageSpeedRequest:
    """Load configuration from config.yaml."""
    if not CONFIG_PATH.exists():
        print(f"Error: {CONFIG_PATH} not found.")
        print("Copy config.example.yaml to config.yaml and edit your URLs.")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    if not config or not config.get("urls"):
        print("Error: No URLs found in config.yaml")
        sys.exit(1)

    url_templates = [
        UrlTemplate(
            url=entry["url"],
            template_type=entry.get("template_type", ""),
        )
        for entry in config["urls"]
    ]

    return PageSpeedRequest(
        url_templates=url_templates,
        strategy=config.get("strategy", "both"),
        include_network_waterfall=config.get("include_network_waterfall", True),
        include_screenshots=config.get("include_screenshots", False),
        model_override=config.get("model_override"),
    )


async def main():
    request = load_config()
    urls = request.get_urls()

    print(f"Analyzing {len(urls)} URL(s) with strategy '{request.strategy}'...")
    print("This may take several minutes depending on the number of URLs.\n")

    result = await analyze_pages(request)

    print(f"\nReport saved to: {result['markdown_path']}")
    if result.get("excel_path"):
        print(f"Excel saved to: {result['excel_path']}")
    print(f"Cost: ${result['cost_usd']:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
