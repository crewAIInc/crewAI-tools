"""Base class for API-based tools with secure key handling."""
import os
from typing import Optional

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, SecretStr


class APIKeyConfig(BaseModel):
    """Configuration for API keys with secure handling."""

    env_var: str = Field(
        ..., description="Environment variable name containing the API key"
    )
    key_prefix: Optional[str] = Field(
        None, description="Expected prefix for API key validation"
    )
    min_length: int = Field(default=20, description="Minimum length for API key")


class APIBasedTool(BaseTool):
    """Base class for tools that require API keys."""

    api_key_config: APIKeyConfig
    _api_key: SecretStr = None

    def __init__(self, **kwargs):
        """Initialize with secure API key validation."""
        super().__init__(**kwargs)
        self._validate_and_set_api_key()

    def _validate_and_set_api_key(self) -> None:
        """Securely validate and set API key."""
        api_key = os.getenv(self.api_key_config.env_var)

        if not api_key:
            raise ValueError(
                f"Missing API key. Please set the {self.api_key_config.env_var} environment variable."
            )

        if len(api_key) < self.api_key_config.min_length:
            raise ValueError(
                f"API key length below minimum requirement. Please check your {self.api_key_config.env_var} configuration."
            )

        if self.api_key_config.key_prefix and not api_key.startswith(
            self.api_key_config.key_prefix
        ):
            raise ValueError(
                f"Invalid API key format. Please check your {self.api_key_config.env_var} configuration."
            )

        self._api_key = SecretStr(api_key)

    def get_api_key(self) -> SecretStr:
        """Safely retrieve API key."""
        if not self._api_key:
            self._validate_and_set_api_key()
        return self._api_key

    def _get_headers(self, **kwargs) -> dict:
        """Get headers with API key safely included."""
        headers = kwargs.get("headers", {})
        return headers
