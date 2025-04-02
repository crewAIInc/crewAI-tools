from typing import TYPE_CHECKING, Optional, Type

from pydantic import BaseModel

if TYPE_CHECKING:
    from hyperbrowser.models import (
        CreateSessionParams,
        CuaTaskResponse,
        StartCuaTaskParams,
    )

try:
    from hyperbrowser.models import (
        CreateSessionParams,
        CuaTaskResponse,
        StartCuaTaskParams,
    )
except ImportError:
    pass


from ..common.errors import NOT_INITIALIZED_ERROR
from ..common.base import HyperBrowserBase


class HyperbrowserOpenAICuaTool(HyperBrowserBase):
    name: str = "Hyperbrowser OpenAI CUA tool"
    description: str = (
        "Use a browser to interact with a webpage using Hyperbrowser and return the results"
    )
    args_schema: Type[BaseModel] = StartCuaTaskParams

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    def _run(
        self,
        task: str,
        session_id: Optional[str] = None,
        max_failures: Optional[int] = None,
        max_steps: Optional[int] = None,
        keep_browser_open: Optional[bool] = None,
        session_options: Optional[CreateSessionParams] = None,
    ) -> CuaTaskResponse:
        if not self._hyperbrowser:
            raise NOT_INITIALIZED_ERROR

        if session_options is not None:
            session_options = CreateSessionParams.model_validate(session_options)

        return self._hyperbrowser.agents.cua.start_and_wait(
            StartCuaTaskParams(
                task=task,
                session_id=session_id,
                max_failures=max_failures,
                max_steps=max_steps,
                keep_browser_open=keep_browser_open,
                session_options=session_options,
            )
        )
