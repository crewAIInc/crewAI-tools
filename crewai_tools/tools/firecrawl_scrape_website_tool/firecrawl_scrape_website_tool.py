from typing import Any, Optional, Type, List, Dict

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = Any


class FirecrawlScrapeWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL")
    formats: Optional[List[str]] = Field(
        default=["markdown"],
        description="Formats to include in the output (markdown, html, rawHtml, links, screenshot)",
    )
    only_main_content: Optional[bool] = Field(
        default=True,
        description="Only return the main content of the page excluding headers, navs, footers, etc.",
    )
    include_tags: Optional[List[str]] = Field(
        default=None,
        description="Tags to include in the output",
    )
    exclude_tags: Optional[List[str]] = Field(
        default=None,
        description="Tags to exclude from the output",
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Headers to send with the request",
    )
    wait_for: Optional[int] = Field(
        default=0,
        description="Specify a delay in milliseconds before fetching the content",
    )
    mobile: Optional[bool] = Field(
        default=False,
        description="Set to true if you want to emulate scraping from a mobile device",
    )
    skip_tls_verification: Optional[bool] = Field(
        default=False,
        description="Skip TLS certificate verification when making requests",
    )
    timeout: Optional[int] = Field(
        default=30000,
        description="Timeout in milliseconds for the scraping operation",
    )
    json_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options for JSON extraction from the page",
    )
    location: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Location settings for the request",
    )
    remove_base64_images: Optional[bool] = Field(
        default=False,
        description="Removes all base 64 images from the output",
    )
    block_ads: Optional[bool] = Field(
        default=True,
        description="Enables ad-blocking and cookie popup blocking",
    )
    actions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Actions to perform on the page before grabbing the content",
    )
    proxy: Optional[str] = Field(
        default=None,
        description="Specifies the type of proxy to use",
    )


class FirecrawlScrapeWebsiteTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Firecrawl web scrape tool"
    description: str = "Scrape webpages using Firecrawl and return the contents"
    args_schema: Type[BaseModel] = FirecrawlScrapeWebsiteToolSchema
    api_key: Optional[str] = None
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        try:
            from firecrawl import FirecrawlApp  # type: ignore
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'firecrawl-py' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "firecrawl-py"], check=True)
                from firecrawl import (
                    FirecrawlApp,
                )
            else:
                raise ImportError(
                    "`firecrawl-py` package not found, please run `uv add firecrawl-py`"
                )

        self._firecrawl = FirecrawlApp(api_key=api_key)

    def _run(
        self,
        url: str,
        formats: Optional[List[str]] = ["markdown"],
        only_main_content: Optional[bool] = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: Optional[int] = 0,
        mobile: Optional[bool] = False,
        skip_tls_verification: Optional[bool] = False,
        timeout: Optional[int] = 30000,
        json_options: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, Any]] = None,
        remove_base64_images: Optional[bool] = False,
        block_ads: Optional[bool] = True,
        actions: Optional[List[Dict[str, Any]]] = None,
        proxy: Optional[str] = None,
    ):
        options = {
            "formats": formats,
            "onlyMainContent": only_main_content,
            "includeTags": include_tags or [],
            "excludeTags": exclude_tags or [],
            "headers": headers or {},
            "waitFor": wait_for,
            "mobile": mobile,
            "skipTlsVerification": skip_tls_verification,
            "timeout": timeout,
            "jsonOptions": json_options,
            "location": location,
            "removeBase64Images": remove_base64_images,
            "blockAds": block_ads,
            "actions": actions or [],
            "proxy": proxy,
        }
        return self._firecrawl.scrape_url(url, options)


try:
    from firecrawl import FirecrawlApp

    # Must rebuild model after class is defined
    if not hasattr(FirecrawlScrapeWebsiteTool, "_model_rebuilt"):
        FirecrawlScrapeWebsiteTool.model_rebuild()
        FirecrawlScrapeWebsiteTool._model_rebuilt = True
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """
