from typing import Any, Dict, Optional, Type, List, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = Any


class FirecrawlCrawlWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL")
    exclude_paths: Optional[List[str]] = Field(
        default=None,
        description="URL patterns to exclude from the crawl",
    )
    include_paths: Optional[List[str]] = Field(
        default=None,
        description="URL patterns to include in the crawl",
    )
    max_depth: Optional[int] = Field(
        default=2,
        description="Maximum depth to crawl relative to the entered URL",
    )
    ignore_sitemap: Optional[bool] = Field(
        default=False,
        description="Ignore the website sitemap when crawling",
    )
    ignore_query_parameters: Optional[bool] = Field(
        default=False,
        description="Do not re-scrape the same path with different (or none) query parameters",
    )
    limit: Optional[int] = Field(
        default=10000,
        description="Maximum number of pages to crawl",
    )
    allow_backward_links: Optional[bool] = Field(
        default=False,
        description="Enables the crawler to navigate from a specific URL to previously linked pages",
    )
    allow_external_links: Optional[bool] = Field(
        default=False,
        description="Allows the crawler to follow links to external websites",
    )
    webhook: Optional[Union[str, Dict[str, Any]]] = Field(
        default=None,
        description="Webhook configuration for crawl notifications",
    )
    scrape_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options for scraping pages during crawl",
    )


class FirecrawlCrawlWebsiteTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Firecrawl web crawl tool"
    description: str = "Crawl webpages using Firecrawl and return the contents"
    args_schema: Type[BaseModel] = FirecrawlCrawlWebsiteToolSchema
    api_key: Optional[str] = None
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self._initialize_firecrawl()

    def _initialize_firecrawl(self) -> None:
        try:
            from firecrawl import FirecrawlApp  # type: ignore

            self._firecrawl = FirecrawlApp(api_key=self.api_key)
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'firecrawl-py' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "firecrawl-py"], check=True)
                    from firecrawl import FirecrawlApp

                    self._firecrawl = FirecrawlApp(api_key=self.api_key)
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install firecrawl-py package")
            else:
                raise ImportError(
                    "`firecrawl-py` package not found, please run `uv add firecrawl-py`"
                )

    def _run(
        self,
        url: str,
        exclude_paths: Optional[List[str]] = None,
        include_paths: Optional[List[str]] = None,
        max_depth: Optional[int] = 2,
        ignore_sitemap: Optional[bool] = False,
        ignore_query_parameters: Optional[bool] = False,
        limit: Optional[int] = 10000,
        allow_backward_links: Optional[bool] = False,
        allow_external_links: Optional[bool] = False,
        webhook: Optional[Union[str, Dict[str, Any]]] = None,
        scrape_options: Optional[Dict[str, Any]] = None
    ):
        options = {
            "excludePaths": exclude_paths or [],
            "includePaths": include_paths or [],
            "maxDepth": max_depth,
            "ignoreSitemap": ignore_sitemap,
            "ignoreQueryParameters": ignore_query_parameters,
            "limit": limit,
            "allowBackwardLinks": allow_backward_links,
            "allowExternalLinks": allow_external_links,
            "webhook": webhook,
            "scrapeOptions": scrape_options or {},
        }
        return self._firecrawl.crawl_url(url, options)


try:
    from firecrawl import FirecrawlApp

    # Only rebuild if the class hasn't been initialized yet
    if not hasattr(FirecrawlCrawlWebsiteTool, "_model_rebuilt"):
        FirecrawlCrawlWebsiteTool.model_rebuild()
        FirecrawlCrawlWebsiteTool._model_rebuilt = True
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """