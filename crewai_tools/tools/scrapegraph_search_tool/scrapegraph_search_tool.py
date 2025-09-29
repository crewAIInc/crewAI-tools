import os
from typing import Any, Optional, Type, TYPE_CHECKING
from uuid import UUID

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, model_validator, ConfigDict

# Type checking import
if TYPE_CHECKING:
    from scrapegraph_py import Client


class ScrapegraphError(Exception):
    """Base exception for Scrapegraph-related errors"""


class RateLimitError(ScrapegraphError):
    """Raised when API rate limits are exceeded"""


class ScrapegraphSearchToolSchema(BaseModel):
    """Input for ScrapegraphSearchTool."""
    
    user_prompt: str = Field(..., description="Search query or prompt")
    headers: Optional[dict[str, str]] = Field(
        None,
        description="Optional headers to send with the request"
    )
    output_schema: Optional[Type[BaseModel]] = Field(
        None,
        description="Optional Pydantic model to structure the output"
    )

    @model_validator(mode="after")
    def validate_user_prompt(cls, values):
        """Validate the user prompt"""
        if not values.user_prompt or not values.user_prompt.strip():
            raise ValueError("User prompt cannot be empty")
        if not any(c.isalnum() for c in values.user_prompt):
            raise ValueError("User prompt must contain a valid prompt")
        return values


class ScrapegraphSearchTool(BaseTool):
    """
    A tool that uses Scrapegraph AI's SearchScraper to perform intelligent web searches.

    Raises:
        ValueError: If API key is missing or prompt is invalid
        RateLimitError: If API rate limits are exceeded
        RuntimeError: If search operation fails
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "Scrapegraph search tool"
    description: str = (
        "A tool that uses Scrapegraph AI to perform intelligent web searches "
        "and extract relevant information from search results."
    )
    args_schema: Type[BaseModel] = ScrapegraphSearchToolSchema
    api_key: Optional[str] = None
    enable_logging: bool = False
    _client: Optional["Client"] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_logging: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        try:
            from scrapegraph_py import Client
            from scrapegraph_py.logger import sgai_logger
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'scrapegraph-py' package. Would you like to install it?"
            ):
                import subprocess
                subprocess.run(["uv", "add", "scrapegraph-py"], check=True)
                from scrapegraph_py import Client
                from scrapegraph_py.logger import sgai_logger
            else:
                raise ImportError(
                    "`scrapegraph-py` package not found, please run `uv add scrapegraph-py`"
                )

        self.api_key = api_key or os.getenv("SCRAPEGRAPH_API_KEY")
        if not self.api_key:
            raise ValueError("Scrapegraph API key is required")

        self._client = Client(api_key=self.api_key)
        self.enable_logging = enable_logging

        if self.enable_logging:
            sgai_logger.set_logging(level="INFO")

    def _handle_api_response(self, response: dict) -> Any:
        """Handle and validate API response"""
        if not response:
            raise RuntimeError("Empty response from Scrapegraph API")

        if "error" in response:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            if "rate limit" in error_msg.lower():
                raise RateLimitError(f"Rate limit exceeded: {error_msg}")
            raise RuntimeError(f"API error: {error_msg}")

        if "result" not in response:
            raise RuntimeError("Invalid response format from Scrapegraph API")

        return response["result"]

    def _run(
        self,
        user_prompt: str,
        headers: Optional[dict[str, str]] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> Any:
        try:
            # Make the SearchScraper request
            response = self._client.searchscraper(
                user_prompt=user_prompt,
                headers=headers,
                output_schema=output_schema.model_json_schema() if output_schema else None,
            )

            return self._handle_api_response(response)

        except RateLimitError:
            raise  # Re-raise rate limit errors
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")
        finally:
            # Always close the client
            self._client.close() 