"""Base class for Serply API tools with secure key handling."""
from typing import Optional

from pydantic import Field

from crewai_tools.tools.base.api_tool import APIBasedTool, APIKeyConfig


class SerplyBaseTool(APIBasedTool):
    """Base class for all Serply API tools."""

    api_key_config: APIKeyConfig = Field(
        default=APIKeyConfig(
            env_var="SERPLY_API_KEY",
            min_length=32,  # Serply API keys are typically long
        )
    )
    proxy_location: Optional[str] = Field(
        default="US",
        description="Where to perform the search. Options: ['US', 'CA', 'IE', 'GB', 'FR', 'DE', 'SE', 'IN', 'JP', 'KR', 'SG', 'AU', 'BR']",
    )

    def __init__(self, proxy_location: Optional[str] = "US", **kwargs):
        """Initialize the Serply base tool.

        Args:
            proxy_location (str): Where to perform operations. Defaults to "US".
        """
        super().__init__(**kwargs)
        self.proxy_location = proxy_location
        self._validate_and_set_api_key()

    @property
    def headers(self) -> dict:
        """Get the headers for Serply API requests.

        Returns:
            dict: Headers including API key and proxy location.
        """
        return {
            "X-API-KEY": self.get_api_key().get_secret_value(),
            "User-Agent": "crew-tools",
            "X-Proxy-Location": self.proxy_location,
        }
