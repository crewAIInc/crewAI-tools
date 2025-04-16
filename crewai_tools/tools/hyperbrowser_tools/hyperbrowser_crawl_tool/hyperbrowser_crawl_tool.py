from typing import TYPE_CHECKING, List, Optional, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from hyperbrowser.models import (
        CrawlJobResponse,
        CreateSessionParams,
        ScrapeOptions,
        StartCrawlJobParams,
    )

try:
    from hyperbrowser.models import (
        CrawlJobResponse,
        CreateSessionParams,
        ScrapeOptions,
        StartCrawlJobParams,
    )
except ImportError:
    pass

from ..common.errors import NOT_INITIALIZED_ERROR
from ..common.base import HyperBrowserBase
from ..common.validators import validate_url


class HyperbrowserCrawlTool(HyperBrowserBase):
    name: str = "Hyperbrowser web crawl tool"
    description: str = "Crawl webpages using Hyperbrowser and return the results"
    args_schema: Type[BaseModel] = StartCrawlJobParams

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(
        self,
        url: str,
        max_pages: Optional[int] = None,
        follow_links: bool = True,
        ignore_sitemap: bool = False,
        exclude_patterns: List[str] = [],
        include_patterns: List[str] = [],
        session_options: Optional[CreateSessionParams] = None,
        scrape_options: Optional[ScrapeOptions] = None,
    ) -> CrawlJobResponse:
        if not self._hyperbrowser:
            raise NOT_INITIALIZED_ERROR

        validate_url(url)

        if session_options is not None:
            session_options = CreateSessionParams.model_validate(session_options)

        if scrape_options is not None:
            scrape_options = ScrapeOptions.model_validate(scrape_options)

        return self._hyperbrowser.crawl.start_and_wait(
            StartCrawlJobParams(
                url=url,
                max_pages=max_pages,
                follow_links=follow_links,
                ignore_sitemap=ignore_sitemap,
                exclude_patterns=exclude_patterns,
                include_patterns=include_patterns,
                session_options=session_options,
                scrape_options=scrape_options,
            )
        )
