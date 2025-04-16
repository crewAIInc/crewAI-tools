from typing import TYPE_CHECKING, Optional, Type
from urllib.parse import urlparse

from pydantic import BaseModel

if TYPE_CHECKING:
    from hyperbrowser.models import (
        CreateSessionParams,
        ScrapeJobResponse,
        ScrapeOptions,
        StartScrapeJobParams,
    )

try:
    from hyperbrowser.models import (
        CreateSessionParams,
        ScrapeJobResponse,
        ScrapeOptions,
        StartScrapeJobParams,
    )
except ImportError:
    pass

from ..common.errors import NOT_INITIALIZED_ERROR
from ..common.base import HyperBrowserBase
from ..common.validators import validate_url


class HyperbrowserScrapeTool(HyperBrowserBase):

    name: str = "Hyperbrowser web scrape tool"
    description: str = "Scrape webpages using Hyperbrowser and return the results"
    args_schema: Type[BaseModel] = StartScrapeJobParams

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(
        self,
        url: str,
        session_options: Optional[CreateSessionParams] = None,
        scrape_options: Optional[ScrapeOptions] = None,
    ) -> ScrapeJobResponse:
        if not self._hyperbrowser:
            raise NOT_INITIALIZED_ERROR

        validate_url(url)

        # Validate if URL is valid
        if not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL. URL must start with 'http://' or 'https://'")

        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            raise ValueError("Invalid URL. URL must contain a valid domain")

        if session_options is not None:
            CreateSessionParams.model_validate(session_options)

        if scrape_options is not None:
            ScrapeOptions.model_validate(scrape_options)

        return self._hyperbrowser.scrape.start_and_wait(
            StartScrapeJobParams(
                url=url,
                session_options=session_options,
                scrape_options=scrape_options,
            )
        )
