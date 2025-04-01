from typing import TYPE_CHECKING, List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        CrawlJobResponse,
        CreateSessionParams,
        ScrapeOptions,
        StartCrawlJobParams,
    )


try:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        CrawlJobResponse,
        CreateSessionParams,
        ScrapeOptions,
        StartCrawlJobParams,
    )

    HYPERBROWSER_AVAILABLE = True
except ImportError:
    HYPERBROWSER_AVAILABLE = False


class HyperbrowserCrawlTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Hyperbrowser web crawl tool"
    description: str = "Crawl webpages using Hyperbrowser and return the results"
    args_schema: Type[BaseModel] = StartCrawlJobParams
    api_key: Optional[str] = None
    _hyperbrowser: Optional["Hyperbrowser"] = PrivateAttr(None)

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self._initialize_hyperbrowser()

    def _initialize_hyperbrowser(self) -> None:
        try:
            if HYPERBROWSER_AVAILABLE:
                self._hyperbrowser = Hyperbrowser(api_key=self.api_key)
            else:
                raise ImportError
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'hyperbrowser' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "hyperbrowser"], check=True)
                    from hyperbrowser import Hyperbrowser

                    self._hyperbrowser = Hyperbrowser(api_key=self.api_key)
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install hyperbrowser package")
            else:
                raise ImportError(
                    "`hyperbrowser` package not found, please run `uv add hyperbrowser`"
                )

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
            raise RuntimeError("Hyperbrowser not properly initialized")

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
