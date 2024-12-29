from typing import Optional, Type

from pydantic import BaseModel, Field

from crewai_tools.tools.base.api_tool import APIBasedTool, APIKeyConfig


class EXABaseToolToolSchema(BaseModel):
    """Input for EXABaseTool."""

    search_query: str = Field(
        ..., description="Mandatory search query you want to use to search the internet"
    )


class EXABaseTool(APIBasedTool):
    name: str = "Search the internet"
    description: str = (
        "A tool that can be used to search the internet from a search_query"
    )
    args_schema: Type[BaseModel] = EXABaseToolToolSchema
    search_url: str = "https://api.exa.ai/search"
    n_results: Optional[int] = None
    api_key_config: APIKeyConfig = Field(
        default=APIKeyConfig(
            env_var="EXA_API_KEY",
            min_length=32,  # EXA API keys are typically long
        )
    )
    _base_headers: dict = {
        "accept": "application/json",
        "content-type": "application/json",
    }

    def __init__(self, **kwargs):
        """Initialize with secure API key validation."""
        super().__init__(**kwargs)
        self._validate_and_set_api_key()

    @property
    def headers(self) -> dict:
        """Get headers with API key safely included."""
        headers = self._base_headers.copy()
        headers["x-api-key"] = self.get_api_key().get_secret_value()
        return headers

    def _parse_results(self, results):
        string = []
        for result in results:
            try:
                string.append(
                    "\n".join(
                        [
                            f"Title: {result['title']}",
                            f"Score: {result['score']}",
                            f"Url: {result['url']}",
                            f"ID: {result['id']}",
                            "---",
                        ]
                    )
                )
            except KeyError:
                continue

        content = "\n".join(string)
        return f"\nSearch results: {content}\n"
