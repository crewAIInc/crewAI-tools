import os
from typing import Any, Optional, Type, Dict, List, Union
from pydantic import BaseModel, Field, ConfigDict
from crewai.tools import BaseTool
# Type checking import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scrapegraph_py import Client


class ScrapegraphError(Exception):
    """Base exception for Scrapegraph-related errors"""


class RateLimitError(ScrapegraphError):
    """Raised when API rate limits are exceeded"""


class ScrapegraphSearchToolSchema(BaseModel):
    """Input for ScrapegraphSearchTool."""

    user_prompt: str = Field(
        ..., 
        description="The search query or prompt to guide the information extraction"
    )
    output_schema: Optional[Type[BaseModel]] = Field(
        None,
        description="Optional Pydantic model to structure the output data"
    )


class ScrapegraphSearchTool(BaseTool):
    """
    A tool that uses Scrapegraph AI to search and extract structured information from the web.

    This tool supports custom output schemas through Pydantic models for structured data extraction.

    Raises:
        ValueError: If API key is missing
        RateLimitError: If API rate limits are exceeded
        RuntimeError: If search operation fails
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "Scrapegraph web searcher"
    description: str = (
        "A tool that uses Scrapegraph AI to search and extract structured information from the web."
    )
    args_schema: Type[BaseModel] = ScrapegraphSearchToolSchema
    user_prompt: Optional[str] = None
    output_schema: Optional[Type[BaseModel]] = None
    api_key: Optional[str] = None
    enable_logging: bool = False
    _client: Optional["Client"] = None

    def __init__(
        self,
        user_prompt: Optional[str] = None,
        output_schema: Optional[Type[BaseModel]] = None,
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

        self._client = Client(api_key=api_key)

        self.api_key = api_key or os.getenv("SCRAPEGRAPH_API_KEY")

        if not self.api_key:
            raise ValueError("Scrapegraph API key is required")

        if user_prompt is not None:
            self.user_prompt = user_prompt
            self.description = f"A tool that uses Scrapegraph AI to search for: {user_prompt}"

        if output_schema is not None:
            if not issubclass(output_schema, BaseModel):
                raise ValueError("output_schema must be a Pydantic BaseModel class")
            self.output_schema = output_schema

        # Configure logging only if enabled
        if self.enable_logging:
            sgai_logger.set_logging(level="INFO")

    def _handle_api_response(self, response: dict) -> Dict[str, Any]:
        """Handle and validate API response"""
        if not response:
            raise RuntimeError("Empty response from Scrapegraph API")

        if "error" in response:
            error_msg = response.get("error", {}).get("message", "Unknown error")
            if "rate limit" in error_msg.lower():
                raise RateLimitError(f"Rate limit exceeded: {error_msg}")
            raise RuntimeError(f"API error: {error_msg}")

        if "result" not in response or "reference_urls" not in response:
            raise RuntimeError("Invalid response format from Scrapegraph API")

        return {
            "result": response["result"],
            "reference_urls": response["reference_urls"],
            "request_id": response.get("request_id")
        }

    def _run(
        self,
        **kwargs: Any,
    ) -> Dict[str, Union[Any, List[str]]]:
        user_prompt = kwargs.get("user_prompt", self.user_prompt)
        output_schema = kwargs.get("output_schema", self.output_schema)

        if not user_prompt:
            raise ValueError("user_prompt is required")

        try:
            # Make the SearchScraper request
            response = self._client.searchscraper(
                user_prompt=user_prompt,
                output_schema=output_schema,
            )

            return self._handle_api_response(response)

        except RateLimitError:
            raise  # Re-raise rate limit errors
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")
        finally:
            # Always close the client
            self._client.close()
