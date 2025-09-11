import os
from typing import Any, Dict, Optional, Type

import requests
from typing import List
from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, Field


class YouSearchToolSchema(BaseModel):
    """Input for You.com Web Search."""

    query: str = Field(..., description="Search query text")


class YouSearchTool(BaseTool):
    name: str = "You.com Web Search Tool"
    description: str = (
        "Perform a web search using You.com's Search API and return structured results "
        "(web/news) with snippets and URLs."
    )
    args_schema: Type[BaseModel] = YouSearchToolSchema

    env_vars: List[EnvVar] = [
        EnvVar(
            name="YOU_API_KEY",
            description="API key for You.com Search API (used as X-API-Key)",
            required=True,
        )
    ]
    package_dependencies: List[str] = ["requests"]

    base_url: str = "https://api.ydc-index.io/v1/search"

    def _run(self, query: str, **_: Any) -> str:
        api_key = os.environ.get("YOU_API_KEY")
        if not api_key:
            return "Error: YOU_API_KEY environment variable is required"

        headers = {"X-API-Key": api_key}
        params: Dict[str, Any] = {"query": query}

        try:
            resp = requests.get(self.base_url, headers=headers, params=params, timeout=20)
            if resp.status_code >= 300:
                return f"You.com Search API error: {resp.status_code} {resp.text[:200]}"
            data = resp.json()
            # Return JSON string so agents can consume directly
            try:
                import json

                return json.dumps(data, ensure_ascii=False)
            except Exception:
                return str(data)
        except requests.Timeout:
            return "You.com Search API timeout. Please try again later."
        except Exception as exc:  # noqa: BLE001
            return f"Unexpected error calling You.com Search API: {exc}"


