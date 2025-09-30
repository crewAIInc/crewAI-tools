import os
import time
from typing import TYPE_CHECKING, Any, Optional, Type, List, Dict, Union
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


class ScrapeMethod(str, Enum):
    """Available scraping methods"""
    SMARTSCRAPER = "smartscraper"
    SEARCHSCRAPER = "searchscraper"
    AGENTICSCRAPER = "agenticscraper"
    CRAWL = "crawl"
    SCRAPE = "scrape"
    MARKDOWNIFY = "markdownify"


class FixedScrapegraphScrapeToolSchema(BaseModel):
    """Input for ScrapegraphScrapeTool when website_url is fixed."""

    method: ScrapeMethod = Field(
        default=ScrapeMethod.SMARTSCRAPER,
        description="Scraping method to use"
    )
    user_prompt: str = Field(
        default="Extract the main content of the webpage",
        description="Prompt to guide the extraction of content",
    )
    render_heavy_js: bool = Field(
        default=False,
        description="Enable JavaScript rendering for dynamic content"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Custom headers for the request"
    )
    data_schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON schema for structured data extraction"
    )
    steps: Optional[List[str]] = Field(
        default=None,
        description="List of steps for agentic scraping (e.g., ['click button', 'fill form'])"
    )
    num_results: Optional[int] = Field(
        default=3,
        description="Number of search results for searchscraper (3-20)"
    )
    depth: Optional[int] = Field(
        default=1,
        description="Crawling depth for crawl method"
    )
    max_pages: Optional[int] = Field(
        default=10,
        description="Maximum pages to crawl"
    )
    same_domain_only: bool = Field(
        default=True,
        description="Only crawl pages from the same domain"
    )
    cache_website: bool = Field(
        default=False,
        description="Cache website content for faster subsequent requests"
    )
    use_session: bool = Field(
        default=False,
        description="Use session for agentic scraping to maintain state"
    )
    ai_extraction: bool = Field(
        default=True,
        description="Enable AI extraction for agentic scraping"
    )
    timeout: Optional[int] = Field(
        default=300,
        description="Request timeout in seconds (max 600 for crawl operations)"
    )


class ScrapegraphScrapeToolSchema(FixedScrapegraphScrapeToolSchema):
    """Input for ScrapegraphScrapeTool."""

    website_url: str = Field(..., description="Mandatory website url to scrape")

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

    @field_validator("num_results")
    def validate_num_results(cls, v):
        """Validate number of results for searchscraper"""
        if v is not None and (v < 1 or v > 20):
            raise ValueError("num_results must be between 1 and 20")
        return v

    @field_validator("depth")
    def validate_depth(cls, v):
        """Validate crawling depth"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError("depth must be between 1 and 5")
        return v

    @field_validator("timeout")
    def validate_timeout(cls, v):
        """Validate timeout"""
        if v is not None and (v < 10 or v > 600):
            raise ValueError("timeout must be between 10 and 600 seconds")
        return v


class ScrapegraphScrapeTool(BaseTool):
    """
    A comprehensive tool that uses ScrapeGraph AI to intelligently scrape website content.

    Supports multiple scraping methods:
    - smartscraper: Basic intelligent content extraction
    - searchscraper: Search-based content gathering from multiple sources
    - agenticscraper: Interactive scraping with automated actions (clicking, typing, etc.)
    - crawl: Multi-page crawling with depth control
    - scrape: Raw HTML extraction with JS rendering support
    - markdownify: Convert web content to markdown format

    Raises:
        ValueError: If API key is missing or URL format is invalid
        RateLimitError: If API rate limits are exceeded
        RuntimeError: If scraping operation fails
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "ScrapeGraph AI Multi-Method Scraper"
    description: str = (
        "A comprehensive scraping tool using ScrapeGraph AI. Supports smartscraper (intelligent extraction), "
        "searchscraper (multi-source search), agenticscraper (interactive automation), crawl (multi-page), "
        "scrape (raw HTML), and markdownify (markdown conversion) methods."
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
        user_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
        enable_logging: bool = False,
        method: ScrapeMethod = ScrapeMethod.SMARTSCRAPER,
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
            self.description = f"A tool that uses ScrapeGraph AI to scrape {website_url}'s content using {method.value} method."
            self.args_schema = FixedScrapegraphScrapeToolSchema

        if user_prompt is not None:
            self.user_prompt = user_prompt

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

    def _handle_api_response(self, response: dict, method: ScrapeMethod) -> Any:
        """Handle and validate API response"""
        if not response:
            raise RuntimeError("Empty response from ScrapeGraph API")

        if "error" in response:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            if "rate limit" in error_msg.lower():
                raise RateLimitError(f"Rate limit exceeded: {error_msg}")
            raise RuntimeError(f"API error: {error_msg}")

        # Handle different response formats based on method
        if method == ScrapeMethod.CRAWL:
            # Crawl may return async operation ID
            if "id" in response or "task_id" in response:
                return self._handle_async_crawl(response)
            elif "result" in response:
                return response["result"]
        elif method == ScrapeMethod.SEARCHSCRAPER:
            # SearchScraper returns result and reference_urls
            if "result" in response:
                return {
                    "result": response["result"],
                    "reference_urls": response.get("reference_urls", [])
                }
        elif method == ScrapeMethod.SCRAPE:
            # Scrape returns HTML content
            if "html" in response:
                return response["html"]

        # Default handling for other methods
        if "result" not in response:
            raise RuntimeError("Invalid response format from ScrapeGraph API")

        return response["result"]

    def _handle_async_crawl(self, initial_response: dict) -> Any:
        """Handle asynchronous crawl operations"""
        crawl_id = initial_response.get("id") or initial_response.get("task_id")
        if not crawl_id:
            return initial_response

        # Poll for result with timeout
        max_iterations = 60  # 5 minutes with 5-second intervals
        for i in range(max_iterations):
            time.sleep(5)
            try:
                result = self._client.get_crawl(crawl_id)
                status = result.get("status")

                if status == "success" and result.get("result"):
                    return result["result"].get("llm_result", result["result"])
                elif status == "failed":
                    raise RuntimeError(f"Crawl operation failed: {result.get('error', 'Unknown error')}")
                elif status in ["completed", "finished"]:
                    return result.get("result", result)

            except Exception as e:
                if i == max_iterations - 1:  # Last iteration
                    raise RuntimeError(f"Failed to get crawl result: {str(e)}")
                continue

        raise RuntimeError("Crawl operation timed out after 5 minutes")

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        website_url = kwargs.get("website_url", self.website_url)
        method = kwargs.get("method", ScrapeMethod.SMARTSCRAPER)
        user_prompt = (
            kwargs.get("user_prompt", self.user_prompt)
            or "Extract the main content of the webpage"
        )

        # Extract additional parameters
        render_heavy_js = kwargs.get("render_heavy_js", False)
        headers = kwargs.get("headers")
        data_schema = kwargs.get("data_schema")
        steps = kwargs.get("steps")
        num_results = kwargs.get("num_results", 3)
        depth = kwargs.get("depth", 1)
        max_pages = kwargs.get("max_pages", 10)
        same_domain_only = kwargs.get("same_domain_only", True)
        cache_website = kwargs.get("cache_website", False)
        use_session = kwargs.get("use_session", False)
        ai_extraction = kwargs.get("ai_extraction", True)
        timeout = kwargs.get("timeout", 300)

        # Validate required parameters based on method
        if method != ScrapeMethod.SEARCHSCRAPER and not website_url:
            raise ValueError("website_url is required for this method")

        if method == ScrapeMethod.AGENTICSCRAPER and not steps:
            raise ValueError("steps parameter is required for agentic scraping")

        if website_url:
            self._validate_url(website_url)

        try:
            # Route to appropriate method
            if method == ScrapeMethod.SMARTSCRAPER:
                response = self._client.smartscraper(
                    website_url=website_url,
                    user_prompt=user_prompt,
                    data_schema=data_schema
                )

            elif method == ScrapeMethod.SEARCHSCRAPER:
                response = self._client.searchscraper(
                    user_prompt=user_prompt,
                    num_results=num_results
                )

            elif method == ScrapeMethod.AGENTICSCRAPER:
                agenticscraper_kwargs = {
                    "url": website_url,
                    "steps": steps,
                    "use_session": use_session,
                    "ai_extraction": ai_extraction
                }
                if ai_extraction:
                    agenticscraper_kwargs["user_prompt"] = user_prompt
                if data_schema:
                    agenticscraper_kwargs["output_schema"] = data_schema

                response = self._client.agenticscraper(**agenticscraper_kwargs)

            elif method == ScrapeMethod.CRAWL:
                crawl_kwargs = {
                    "url": website_url,
                    "prompt": user_prompt,
                    "depth": depth,
                    "max_pages": max_pages,
                    "same_domain_only": same_domain_only,
                    "cache_website": cache_website
                }
                if data_schema:
                    crawl_kwargs["data_schema"] = data_schema

                response = self._client.crawl(**crawl_kwargs)

            elif method == ScrapeMethod.SCRAPE:
                scrape_kwargs = {
                    "website_url": website_url,
                    "render_heavy_js": render_heavy_js
                }
                if headers:
                    scrape_kwargs["headers"] = headers

                response = self._client.scrape(**scrape_kwargs)

            elif method == ScrapeMethod.MARKDOWNIFY:
                response = self._client.markdownify(website_url=website_url)

            else:
                raise ValueError(f"Unsupported scraping method: {method}")

            return self._handle_api_response(response, method)

        except RateLimitError:
            raise  # Re-raise rate limit errors
        except Exception as e:
            raise RuntimeError(f"Scraping failed with {method.value}: {str(e)}")
        finally:
            # Always close the client
            if hasattr(self, '_client') and self._client:
                self._client.close()
