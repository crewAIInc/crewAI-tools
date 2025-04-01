from typing import TYPE_CHECKING, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        BrowserUseTaskResponse,
        CreateSessionParams,
        StartBrowserUseTaskParams,
    )


try:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        BrowserUseTaskResponse,
        CreateSessionParams,
        StartBrowserUseTaskParams,
    )

    HYPERBROWSER_AVAILABLE = True
except ImportError:
    HYPERBROWSER_AVAILABLE = False


class HyperbrowserBrowserUseToolSchema(BaseModel):
    """
    Parameters for creating a new browser use task.
    """

    model_config = ConfigDict(
        populate_by_alias=True,
    )

    task: str
    validate_output: Optional[bool] = Field(
        default=None, serialization_alias="validateOutput"
    )
    use_vision: Optional[bool] = Field(default=None, serialization_alias="useVision")
    use_vision_for_planner: Optional[bool] = Field(
        default=None, serialization_alias="useVisionForPlanner"
    )
    max_actions_per_step: Optional[int] = Field(
        default=None, serialization_alias="maxActionsPerStep"
    )
    max_input_tokens: Optional[int] = Field(
        default=None, serialization_alias="maxInputTokens"
    )
    planner_interval: Optional[int] = Field(
        default=None, serialization_alias="plannerInterval"
    )
    max_steps: Optional[int] = Field(default=None, serialization_alias="maxSteps")
    session_options: Optional[CreateSessionParams] = Field(
        default=None, serialization_alias="sessionOptions"
    )


class HyperbrowserBrowserUseTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Hyperbrowser web browser use tool"
    description: str = "Use a browser to interact with a webpage using Hyperbrowser and return the results"
    args_schema: Type[BaseModel] = HyperbrowserBrowserUseToolSchema
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
        use_vision: Optional[bool] = None,
        use_vision_for_planner: Optional[bool] = None,
        max_actions_per_step: Optional[int] = None,
        max_input_tokens: Optional[int] = None,
        planner_interval: Optional[int] = None,
        max_steps: Optional[int] = None,
        session_options: Optional[CreateSessionParams] = None,
    ) -> BrowserUseTaskResponse:
        if not self._hyperbrowser:
            raise RuntimeError("Hyperbrowser not properly initialized")

        return self._hyperbrowser.agents.browser_use.start_and_wait(
            StartBrowserUseTaskParams(
                task=task,
                use_vision=use_vision,
                use_vision_for_planner=use_vision_for_planner,
                max_actions_per_step=max_actions_per_step,
                max_input_tokens=max_input_tokens,
                planner_interval=planner_interval,
                max_steps=max_steps,
                session_options=session_options,
            )
        )
