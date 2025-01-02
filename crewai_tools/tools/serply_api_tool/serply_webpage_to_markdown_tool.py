from typing import Any, Optional, Type

import requests
from pydantic import BaseModel, Field

from crewai_tools.tools.serply_api_tool.serply_base_tool import SerplyBaseTool


class SerplyWebpageToMarkdownToolSchema(BaseModel):
    """Input for Serply Search."""

    url: str = Field(
        ...,
        description="Mandatory url you want to use to fetch and convert to markdown",
    )


class SerplyWebpageToMarkdownTool(SerplyBaseTool):
    name: str = "Webpage to Markdown"
    description: str = "A tool to perform convert a webpage to markdown to make it easier for LLMs to understand"
    args_schema: Type[BaseModel] = SerplyWebpageToMarkdownToolSchema
    request_url: str = "https://api.serply.io/v1/request"
    # Headers and proxy_location are handled by SerplyBaseTool

    def __init__(self, proxy_location: Optional[str] = "US", **kwargs):
        """
        proxy_location: (str): Where to perform the search, specifically for a specific country results.
             ['US', 'CA', 'IE', 'GB', 'FR', 'DE', 'SE', 'IN', 'JP', 'KR', 'SG', 'AU', 'BR'] (defaults to US)
        """
        super().__init__(**kwargs)
        self.proxy_location = proxy_location
        # Headers are handled by SerplyBaseTool

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        data = {"url": kwargs["url"], "method": "GET", "response_type": "markdown"}
        response = requests.request(
            "POST", self.request_url, headers=self.headers, json=data
        )
        return response.text
