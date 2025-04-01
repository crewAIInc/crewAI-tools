from typing import TYPE_CHECKING, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, PrivateAttr

if TYPE_CHECKING:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        CreateSessionParams,
        CuaTaskResponse,
        StartCuaTaskParams,
    )


try:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        CreateSessionParams,
        CuaTaskResponse,
        StartCuaTaskParams,
    )

    HYPERBROWSER_AVAILABLE = True
except ImportError:
    HYPERBROWSER_AVAILABLE = False


class HyperbrowserOpenAICuaTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Hyperbrowser OpenAI CUA tool"
    description: str = "Use a browser to interact with a webpage using Hyperbrowser and return the results"
    args_schema: Type[BaseModel] = StartCuaTaskParams
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
        task: str,
        session_id: Optional[str] = None,
        max_failures: Optional[int] = None,
        max_steps: Optional[int] = None,
        keep_browser_open: Optional[bool] = None,
        session_options: Optional[CreateSessionParams] = None,
    ) -> CuaTaskResponse:
        if not self._hyperbrowser:
            raise RuntimeError("Hyperbrowser not properly initialized")

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
