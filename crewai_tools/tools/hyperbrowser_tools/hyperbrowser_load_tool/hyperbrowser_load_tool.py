from typing import Any, Optional, Type, Dict, Literal, Union

from pydantic import BaseModel, Field

try:
    from hyperbrowser.models.scrape import (
        ScrapeOptions,
        StartScrapeJobParams,
        ScrapeJobData,
    )
    from hyperbrowser.models.session import CreateSessionParams
    from hyperbrowser.models.crawl import StartCrawlJobParams, CrawledPage

except ImportError:
    pass

from ..common.errors import NOT_INITIALIZED_ERROR
from ..common.base import HyperBrowserBase
from ..common.validators import validate_url


class HyperbrowserLoadToolSchema(HyperBrowserBase):
    url: str = Field(description="Website URL")
    operation: Literal["scrape", "crawl"] = Field(
        description="Operation to perform on the website. Either 'scrape' or 'crawl'"
    )
    params: Optional[Dict] = Field(
        description="Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait"
    )


class HyperbrowserLoadTool(HyperBrowserBase):
    """HyperbrowserLoadTool.

    Scrape or crawl web pages and load the contents with optional parameters for configuring content extraction.
    Requires the `hyperbrowser` package.
    Get your API Key from https://app.hyperbrowser.ai/

    Args:
        api_key: The Hyperbrowser API key, can be set as an environment variable `HYPERBROWSER_API_KEY` or passed directly
    """

    name: str = "Hyperbrowser web load tool"
    description: str = (
        "Scrape or crawl a website using Hyperbrowser and return the contents in properly formatted markdown or html"
    )
    args_schema: Type[BaseModel] = HyperbrowserLoadToolSchema

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _prepare_params(self, params: Optional[Dict]) -> Dict:
        """Prepare session and scrape options parameters."""

        if params is not None:
            if "scrape_options" in params:
                if "formats" in params["scrape_options"]:
                    formats = params["scrape_options"]["formats"]
                    if not all(fmt in ["markdown", "html"] for fmt in formats):
                        raise ValueError(
                            "formats can only contain 'markdown' or 'html'"
                        )

            if "session_options" in params:
                params["session_options"] = CreateSessionParams.model_validate(
                    **params["session_options"]
                )
            if "scrape_options" in params:
                params["scrape_options"] = ScrapeOptions.model_validate(
                    **params["scrape_options"]
                )
        else:
            params = {}

        return params

    def _extract_content(self, data: Union[CrawledPage, ScrapeJobData]):
        """Extract content from response data."""
        content = ""
        if data:
            content = data.markdown or data.html or ""
        return content

    def _run(
        self,
        url: str,
        operation: Literal["scrape", "crawl"] = "scrape",
        params: Optional[Dict] = {},
    ):

        if not self._hyperbrowser:
            raise NOT_INITIALIZED_ERROR

        validate_url(url)

        params = self._prepare_params(params)

        if operation == "scrape":
            scrape_params = StartScrapeJobParams(url=url, **params)
            scrape_resp = self._hyperbrowser.scrape.start_and_wait(scrape_params)
            content = self._extract_content(scrape_resp.data)
            return content
        else:
            crawl_params = StartCrawlJobParams(url=url, **params)
            crawl_resp = self._hyperbrowser.crawl.start_and_wait(crawl_params)
            content = ""
            if crawl_resp.data:
                for page in crawl_resp.data:
                    page_content = self._extract_content(page)
                    if page_content:
                        content += (
                            f"\n{'-'*50}\nUrl: {page.url}\nContent:\n{page_content}\n"
                        )
            return content
