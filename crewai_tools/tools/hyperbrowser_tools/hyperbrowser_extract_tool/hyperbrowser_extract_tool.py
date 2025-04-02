from typing import TYPE_CHECKING, Any, List, Optional, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from hyperbrowser.models import (
        CreateSessionParams,
        ExtractJobResponse,
        StartExtractJobParams,
    )

try:
    from hyperbrowser.models import (
        CreateSessionParams,
        ExtractJobResponse,
        StartExtractJobParams,
    )
except ImportError:
    pass

from ..common.errors import NOT_INITIALIZED_ERROR
from ..common.base import HyperBrowserBase
from ..common.validators import validate_url


class HyperbrowserExtractTool(HyperBrowserBase):
    name: str = "Hyperbrowser web extract tool"
    description: str = (
        "Extract data from webpages using Hyperbrowser and return the results"
    )
    args_schema: Type[BaseModel] = StartExtractJobParams

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(
        self,
        urls: List[str],
        system_prompt: Optional[str] = None,
        prompt: Optional[str] = None,
        schema_: Optional[Any] = None,
        wait_for: Optional[int] = None,
        session_options: Optional[CreateSessionParams] = None,
        max_links: Optional[int] = None,
    ) -> ExtractJobResponse:
        if not self._hyperbrowser:
            raise NOT_INITIALIZED_ERROR

        for url in urls:
            validate_url(url)

        if session_options is not None:
            session_options = CreateSessionParams.model_validate(session_options)

        return self._hyperbrowser.extract.start_and_wait(
            StartExtractJobParams(
                urls=urls,
                system_prompt=system_prompt,
                prompt=prompt,
                schema=schema_,
                wait_for=wait_for,
                session_options=session_options,
                max_links=max_links,
            )
        )
