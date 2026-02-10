"""Page Speed Analyzer - Request models.

Simplified models for standalone usage (no BaseRequest dependency).
"""

from typing import Optional, List, Dict

from pydantic import BaseModel, Field


class UrlTemplate(BaseModel):
    """Single URL with its template type for page speed analysis."""

    url: str = Field(
        ...,
        description="URL to analyze",
    )
    template_type: str = Field(
        default="",
        description="Template type for this URL (e.g., 'homepage', 'blog-post'). Empty string if not categorized.",
    )


class PageSpeedRequest(BaseModel):
    """Request model for Page Speed Analyzer.

    Analyzes 1-10 URLs for Core Web Vitals and performance issues.
    Optimized for quality analysis over quantity - analyzing 3-4 pages
    from the same template enables detection of template-level vs
    page-specific issues.
    """

    url_templates: List[UrlTemplate] = Field(
        ...,
        description="List of URLs with their template types (1-10 URLs)",
        min_length=1,
        max_length=10,
    )
    include_screenshots: bool = Field(
        default=False,
        description="Include full-page screenshots (not fully supported in standalone mode)",
    )
    include_network_waterfall: bool = Field(
        default=True,
        description="Capture detailed network waterfall data using Playwright",
    )
    strategy: str = Field(
        default="both",
        description="Analysis strategy: 'mobile', 'desktop', or 'both'",
    )
    model_override: Optional[str] = Field(
        default=None,
        description="Override Claude Code model (e.g., 'claude-sonnet-4-5')",
    )

    def get_urls(self) -> List[str]:
        """Get URL list from url_templates."""
        return [item.url for item in self.url_templates]

    def get_template_mapping(self) -> Dict[str, str]:
        """Get template mapping (filters out empty template types)."""
        return {item.url: item.template_type for item in self.url_templates if item.template_type}
