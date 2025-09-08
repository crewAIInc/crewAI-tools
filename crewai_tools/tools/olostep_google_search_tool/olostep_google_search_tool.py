import os
import json
from typing import Any, Optional, Type
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, EnvVar

class OlostepGoogleSearchToolSchema(BaseModel):
    """Input for Olostep Google Search."""
    search_query: str = Field(..., description="The search query for Google.")
    location: Optional[str] = Field(default="us", description="The country to search from. It must be a two-letter country code. (ISO 3166-1 alpha-2)")
    language: Optional[str] = Field(default="en", description="The language to search in. It must be a two-letter language code. (ISO 639-1)")

class OlostepGoogleSearchTool(BaseTool):
    name: str = "Olostep Google Search"
    description: str = "A tool to perform a Google search using the Olostep API and get structured results."
    args_schema: Type[BaseModel] = OlostepGoogleSearchToolSchema
    
    env_vars: list[EnvVar] = [
        EnvVar(
            name="OLOSTEP_API_KEY",
            description="API key for Olostep API.",
            required=True,
        ),
    ]
    package_dependencies: list[str] = ["requests"]

    base_url: str = "https://api.olostep.com/v1/scrapes"
    api_key: Optional[str] = None

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get("OLOSTEP_API_KEY")
        if not self.api_key:
            raise ValueError("OLOSTEP_API_KEY environment variable is required for OlostepGoogleSearchTool.")

    def _run(self, search_query: str, location: str = "us", language: str = "en", **_: Any) -> str:
        """Synchronous execution."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        url = f"https://www.google.com/search?q={search_query}&gl={location}&hl={language}"

        data = {
            "url_to_scrape": url,
            "formats": ["json"],
            "parser": {"id": "@olostep/google-search"},
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            if "result" in result and result["result"].get("json_content"):
                return json.loads(result["result"]["json_content"])
            else:
                return "No JSON content found in the response."

        except requests.Timeout:
            return "Olostep API request timed out. Please try again later."
        except requests.HTTPError as e:
            return f"Olostep API request failed with status {e.response.status_code}: {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
