import os
from typing import TYPE_CHECKING, Any, Optional, Type, List, Dict
from urllib.parse import urlparse
from enum import Enum

from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Type checking import
if TYPE_CHECKING:
    from scrapegraph_py import Client


class ScrapegraphError(Exception):
    """Base exception for Scrapegraph-related errors"""


class RateLimitError(ScrapegraphError):
    """Raised when API rate limits are exceeded"""


class ScrapingMode(str, Enum):
    """Available scraping modes"""
    SMARTSCRAPER = "smartscraper"
    SCRAPE = "scrape"
    SEARCHSCRAPER = "searchscraper"
    AGENTICSCRAPER = "agenticscraper"
    CRAWL = "crawl"
    MARKDOWNIFY = "markdownify"


class FixedScrapegraphScrapeToolSchema(BaseModel):
    """Input for ScrapegraphScrapeTool when website_url is fixed."""


class ScrapegraphScrapeToolSchema(FixedScrapegraphScrapeToolSchema):
    """Input for ScrapegraphScrapeTool."""

    website_url: str = Field(..., description="Mandatory website url to scrape")
    mode: ScrapingMode = Field(
        default=ScrapingMode.SMARTSCRAPER,
        description="Scraping mode to use (smartscraper, scrape, searchscraper, agenticscraper, crawl, markdownify)"
    )
    user_prompt: str = Field(
        default="Extract the main content of the webpage",
        description="Prompt to guide the extraction of content (for smartscraper, searchscraper, agenticscraper, crawl modes)",
    )
    render_heavy_js: bool = Field(
        default=False,
        description="Enable JavaScript rendering for dynamic content (for scrape mode)"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom HTTP headers for the request"
    )
    output_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON schema for structured output (for smartscraper, agenticscraper, crawl modes)"
    )
    steps: Optional[List[str]] = Field(
        default=None,
        description="Automation steps for agenticscraper mode"
    )
    use_session: bool = Field(
        default=False,
        description="Use session for agenticscraper mode"
    )
    ai_extraction: bool = Field(
        default=True,
        description="Enable AI extraction for agenticscraper mode"
    )
    num_results: int = Field(
        default=3,
        description="Number of search results for searchscraper mode (3-20)"
    )
    depth: int = Field(
        default=1,
        description="Crawl depth for crawl mode"
    )
    max_pages: int = Field(
        default=5,
        description="Maximum pages to crawl for crawl mode"
    )
    same_domain_only: bool = Field(
        default=True,
        description="Stay within same domain for crawl mode"
    )
    cache_website: bool = Field(
        default=False,
        description="Cache website content for crawl mode"
    )

    @field_validator("website_url")
    def validate_url(cls, v):
        """Validate URL format"""
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError
            return v
        except Exception:
            raise ValueError(
                "Invalid URL format. URL must include scheme (http/https) and domain"
            )


class ScrapegraphScrapeTool(BaseTool):
    """
    A tool that uses Scrapegraph AI to intelligently scrape website content.

    Raises:
        ValueError: If API key is missing or URL format is invalid
        RateLimitError: If API rate limits are exceeded
        RuntimeError: If scraping operation fails
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "Scrapegraph website scraper"
    description: str = (
        "A comprehensive tool that uses Scrapegraph AI for various web scraping tasks: "
        "basic HTML scraping, AI-powered content extraction, search & scrape, automated interactions, "
        "multi-page crawling, and markdown conversion."
    )
    args_schema: Type[BaseModel] = ScrapegraphScrapeToolSchema
    website_url: Optional[str] = None
    user_prompt: Optional[str] = None
    api_key: Optional[str] = None
    enable_logging: bool = False
    _client: Optional["Client"] = None
    package_dependencies: List[str] = ["scrapegraph-py"]
    env_vars: List[EnvVar] = [
        EnvVar(name="SCRAPEGRAPH_API_KEY", description="API key for Scrapegraph AI services", required=False),
    ]

    def __init__(
        self,
        website_url: Optional[str] = None,
        mode: ScrapingMode = ScrapingMode.SMARTSCRAPER,
        user_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        enable_logging: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        try:
            from scrapegraph_py import Client
            from scrapegraph_py.logger import sgai_logger

        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'scrapegraph-py' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "scrapegraph-py"], check=True)
                from scrapegraph_py import Client
                from scrapegraph_py.logger import sgai_logger

            else:
                raise ImportError(
                    "`scrapegraph-py` package not found, please run `uv add scrapegraph-py`"
                )

        self.api_key = api_key or os.getenv("SCRAPEGRAPH_API_KEY")
        self._client = Client(api_key=self.api_key)

        if not self.api_key:
            raise ValueError("Scrapegraph API key is required")

        if website_url is not None:
            self._validate_url(website_url)
            self.website_url = website_url
            self.description = f"A tool that uses Scrapegraph AI to intelligently scrape {website_url}'s content."
            self.args_schema = FixedScrapegraphScrapeToolSchema

        if user_prompt is not None:
            self.user_prompt = user_prompt

        self.mode = mode

        # Configure logging only if enabled
        if self.enable_logging:
            sgai_logger.set_logging(level="INFO")

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate URL format"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError
        except Exception:
            raise ValueError(
                "Invalid URL format. URL must include scheme (http/https) and domain"
            )

    def _handle_api_response(self, response: dict) -> str:
        """Handle and validate API response"""
        if not response:
            raise RuntimeError("Empty response from Scrapegraph API")

        if "error" in response:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            if "rate limit" in error_msg.lower():
                raise RateLimitError(f"Rate limit exceeded: {error_msg}")
            raise RuntimeError(f"API error: {error_msg}")

        if "result" not in response:
            raise RuntimeError("Invalid response format from Scrapegraph API")

        return response["result"]

    def _scrape_basic(self, website_url: str, **kwargs) -> Dict[str, Any]:
        """Basic HTML scraping without AI extraction"""
        render_heavy_js = kwargs.get("render_heavy_js", False)
        headers = kwargs.get("headers")

        scrape_kwargs = {
            "website_url": website_url,
            "render_heavy_js": render_heavy_js
        }

        if headers:
            scrape_kwargs["headers"] = headers

        return self._client.scrape(**scrape_kwargs)

    def _smartscraper(self, website_url: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """AI-powered content extraction"""
        output_schema = kwargs.get("output_schema")

        smartscraper_kwargs = {
            "website_url": website_url,
            "user_prompt": user_prompt
        }

        if output_schema:
            smartscraper_kwargs["output_schema"] = output_schema

        return self._client.smartscraper(**smartscraper_kwargs)

    def _searchscraper(self, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """Search and scrape functionality"""
        num_results = kwargs.get("num_results", 3)

        return self._client.searchscraper(
            user_prompt=user_prompt,
            num_results=num_results
        )

    def _agenticscraper(self, website_url: str, **kwargs) -> Dict[str, Any]:
        """Automated interaction scraping"""
        steps = kwargs.get("steps", [])
        use_session = kwargs.get("use_session", False)
        ai_extraction = kwargs.get("ai_extraction", True)
        user_prompt = kwargs.get("user_prompt")
        output_schema = kwargs.get("output_schema")

        agenticscraper_kwargs = {
            "url": website_url,
            "steps": steps,
            "use_session": use_session,
            "ai_extraction": ai_extraction
        }

        if user_prompt and ai_extraction:
            agenticscraper_kwargs["user_prompt"] = user_prompt

        if output_schema and ai_extraction:
            agenticscraper_kwargs["output_schema"] = output_schema

        return self._client.agenticscraper(**agenticscraper_kwargs)

    def _crawl(self, website_url: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        """Multi-page crawling with AI extraction"""
        depth = kwargs.get("depth", 1)
        max_pages = kwargs.get("max_pages", 5)
        same_domain_only = kwargs.get("same_domain_only", True)
        cache_website = kwargs.get("cache_website", False)
        output_schema = kwargs.get("output_schema")

        crawl_kwargs = {
            "url": website_url,
            "prompt": user_prompt,
            "depth": depth,
            "max_pages": max_pages,
            "same_domain_only": same_domain_only,
            "cache_website": cache_website
        }

        if output_schema:
            crawl_kwargs["data_schema"] = output_schema

        return self._client.crawl(**crawl_kwargs)

    def _markdownify(self, website_url: str, **kwargs) -> Dict[str, Any]:
        """Convert webpage to markdown format"""
        return self._client.markdownify(website_url=website_url)

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        website_url = kwargs.get("website_url", self.website_url)
        mode = kwargs.get("mode", getattr(self, "mode", ScrapingMode.SMARTSCRAPER))
        user_prompt = (
            kwargs.get("user_prompt", self.user_prompt)
            or "Extract the main content of the webpage"
        )

        # Validate inputs based on mode
        if mode == ScrapingMode.SEARCHSCRAPER:
            # For searchscraper, we don't need a website_url, just the user_prompt
            if not user_prompt:
                raise ValueError("user_prompt is required for searchscraper mode")
        else:
            if not website_url:
                raise ValueError("website_url is required for this mode")
            # Validate URL format
            self._validate_url(website_url)

        try:
            # Route to appropriate scraping method based on mode
            if mode == ScrapingMode.SCRAPE:
                response = self._scrape_basic(website_url, **kwargs)
            elif mode == ScrapingMode.SMARTSCRAPER:
                response = self._smartscraper(website_url, user_prompt, **kwargs)
            elif mode == ScrapingMode.SEARCHSCRAPER:
                response = self._searchscraper(user_prompt, **kwargs)
            elif mode == ScrapingMode.AGENTICSCRAPER:
                response = self._agenticscraper(website_url, **kwargs)
            elif mode == ScrapingMode.CRAWL:
                response = self._crawl(website_url, user_prompt, **kwargs)
            elif mode == ScrapingMode.MARKDOWNIFY:
                response = self._markdownify(website_url, **kwargs)
            else:
                raise ValueError(f"Unsupported scraping mode: {mode}")

            return self._handle_api_response(response)

        except RateLimitError:
            raise  # Re-raise rate limit errors
        except Exception as e:
            raise RuntimeError(f"Scraping failed: {str(e)}")
        finally:
            # Always close the client
            if self._client:
                self._client.close()
