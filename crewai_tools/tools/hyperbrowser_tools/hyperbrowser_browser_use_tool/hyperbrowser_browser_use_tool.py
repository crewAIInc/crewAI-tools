from typing import TYPE_CHECKING, Optional, Type

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from hyperbrowser.models import (
        BrowserUseTaskResponse,
        CreateSessionParams,
        StartBrowserUseTaskParams,
    )


try:
    from hyperbrowser.models import (
        BrowserUseTaskResponse,
        CreateSessionParams,
        StartBrowserUseTaskParams,
    )
except ImportError:
    pass

from ..common.errors import NOT_INITIALIZED_ERROR
from ..common.base import HyperBrowserBase


class HyperbrowserBrowserUseToolSchema(BaseModel):
    """
    Parameters for creating a new browser use task.
    """

    model_config = ConfigDict(
        populate_by_alias=True,  # type: ignore
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


class HyperbrowserBrowserUseTool(HyperBrowserBase):
    name: str = "Hyperbrowser web browser use tool"
    description: str = (
        "Use a browser to interact with a webpage using Hyperbrowser and return the results"
    )
    args_schema: Type[BaseModel] = HyperbrowserBrowserUseToolSchema

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

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
            raise NOT_INITIALIZED_ERROR

        if session_options is not None:
            session_options = CreateSessionParams.model_validate(session_options)

        result = self._hyperbrowser.agents.browser_use.start_and_wait(
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

        return result
