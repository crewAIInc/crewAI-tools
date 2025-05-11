import datetime
import os
from typing import Any, Optional, Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def _save_results_to_file(content: str) -> None:
    """Saves the search results to a file."""
    filename = (
        f"search_results_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    )
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Results saved to {filename}")


class BrightDataUnlockerToolSchema(BaseModel):
    """
    Pydantic schema for input parameters used by the BrightDataWebUnlockerTool.

    This schema defines the structure and validation for parameters passed when performing
    a web scraping request using Bright Data's Web Unlocker.

    Attributes:
        url (str): The target URL to scrape.
        save_file (Optional[bool]): Whether to save the response content to a local file. Defaults to False.
        format (Optional[str]): Format of the response returned by Bright Data. Accepted values are 'json' or 'raw'. Defaults to 'html' (but should be set to 'raw' or 'json' to avoid API errors).
    """

    url: str = Field(..., description="URL to perform the web scraping")
    save_file: Optional[bool] = Field(
        default=False, description="Whether to save results to a local file"
    )
    format: Optional[str] = Field(
        default="html", description="Response format (raw is standard)"
    )


class BrightDataWebUnlockerTool(BaseTool):
    """
    A tool for performing web scraping using the Bright Data Web Unlocker API.

    This tool allows automated and programmatic access to web pages by routing requests
    through Bright Data's unlocking and proxy infrastructure, which can bypass bot
    protection mechanisms like CAPTCHA, geo-restrictions, and anti-bot detection.

    Attributes:
        name (str): Name of the tool.
        description (str): Description of what the tool does.
        args_schema (Type[BaseModel]): Pydantic model schema for expected input arguments.
        base_url (str): Base URL of the Bright Data Web Unlocker API.
        api_key (str): Bright Data API key (must be set in the BRIGHT_DATA_API_KEY environment variable).
        zone (str): Bright Data zone identifier (must be set in the BRIGHT_DATA_ZONE environment variable).

    Methods:
        _run(**kwargs: Any) -> Any:
            Sends a scraping request to Bright Data's Web Unlocker API and returns the result.
            Handles optional file saving and formats response based on input schema.
    """

    name: str = "Bright Data Web Unlocker Scraping"
    description: str = "Tool to perform web scraping using Bright Data Web Unlocker"
    args_schema: Type[BaseModel] = BrightDataUnlockerToolSchema
    base_url: str = "https://api.brightdata.com/request"
    api_key: str = ""
    zone: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.getenv("BRIGHT_DATA_API_KEY")
        self.zone = os.getenv("BRIGHT_DATA_ZONE")
        if not self.api_key:
            raise ValueError("BRIGHT_DATA_API_KEY environment variable is required.")
        if not self.zone:
            raise ValueError("BRIGHT_DATA_ZONE environment variable is required.")

    def _run(self, **kwargs: Any) -> Any:
        payload = {
            "url": kwargs["url"],
            "zone": self.zone,
            "format": kwargs.get("format", "raw"),
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=20
            )
            print(f"Status Code: {response.status_code}")
            response.raise_for_status()

            if (
                kwargs.get("data_format") == "html"
                or kwargs.get("data_format") == "markdown"
            ):
                content = response.text
            else:
                content = response.json()

            if kwargs.get("save_file", False):
                _save_results_to_file(
                    content if isinstance(content, str) else str(content)
                )

            return content

        except requests.RequestException as e:
            return f"HTTP Error performing BrightData Web Unlocker Scrape: {e}\nResponse: {getattr(e.response, 'text', '')}"
        except Exception as e:
            return f"Error fetching results: {str(e)}"
