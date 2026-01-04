from typing import Any, List, Optional, Type
import os
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, EnvVar

class OlostepWebScraperToolInput(BaseModel):
    """Input schema for OlostepWebScraperTool."""
    url_to_scrape: str = Field(..., description="The URL of the webpage to scrape.")
    formats: Optional[List[str]] = Field(default=["markdown"], description="List of formats to return. Can be 'html', 'markdown' or both.")

class OlostepWebScraperTool(BaseTool):
    name: str = "Olostep Web Scraper"
    description: str = "Scrapes a webpage using Olostep API and returns the content in specified formats."
    args_schema: Type[BaseModel] = OlostepWebScraperToolInput

    env_vars: List[EnvVar] = [
        EnvVar(
            name="OLOSTEP_API_KEY",
            description="API key for Olostep API.",
            required=True,
        ),
    ]
    package_dependencies: List[str] = ["requests"]

    base_url: str = "https://api.olostep.com/v1/scrapes"
    api_key: Optional[str] = None

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.api_key = api_key or os.environ.get("OLOSTEP_API_KEY")
        if not self.api_key:
            raise ValueError("OLOSTEP_API_KEY environment variable is required for OlostepWebScraperTool.")

    def _run(self, url_to_scrape: str, formats: Optional[List[str]] = None, **_: Any) -> str:
        """Synchronous execution."""
        if formats is None:
            formats = ["markdown"]
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "url_to_scrape": url_to_scrape,
            "formats": formats,
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            content = []
            if "result" in result:
                if "markdown" in formats and result["result"].get("markdown_content"):
                    content.append(f"Markdown Content:\n{result['result']['markdown_content']}")
                if "html" in formats and result["result"].get("html_content"):
                    content.append(f"HTML Content:\n{result['result']['html_content']}")
            
            if not content:
                return "No content found for the specified formats."

            return "\n\n".join(content)

        except requests.Timeout:
            return "Olostep API request timed out. Please try again later."
        except requests.HTTPError as e:
            return f"Olostep API request failed with status {e.response.status_code}: {e.response.text}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
