"""Base class for MultiOn tools with secure key handling."""

from pydantic import Field

from crewai_tools.tools.base.api_tool import APIBasedTool, APIKeyConfig


class MultiOnBaseTool(APIBasedTool):
    """Base class for all MultiOn API tools."""

    api_key_config: APIKeyConfig = Field(
        default=APIKeyConfig(
            env_var="MULTION_API_KEY",
            min_length=32,  # MultiOn API keys are typically long
        )
    )
    local: bool = Field(default=False, description="Whether to run MultiOn locally")
    max_steps: int = Field(
        default=3, description="Maximum number of steps for browser automation"
    )

    def __init__(self, local: bool = False, max_steps: int = 3, **kwargs):
        """Initialize the MultiOn base tool.

        Args:
            local (bool): Whether to run MultiOn locally. Defaults to False.
            max_steps (int): Maximum number of steps for browser automation. Defaults to 3.
        """
        super().__init__(**kwargs)
        self.local = local
        self.max_steps = max_steps
        if not self.local:
            self._validate_and_set_api_key()
