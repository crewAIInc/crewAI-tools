from importlib.metadata import version
from platform import architecture, python_version
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

try:
    from oxylabs import RealtimeClient
    from oxylabs.sources.response import Response as OxylabsResponse

    OXYLABS_AVAILABLE = True
except ImportError:
    RealtimeClient = Any
    OxylabsResponse = Any

    OXYLABS_AVAILABLE = False


__all__ = ["OxylabsUniversalScraperTool"]


class OxylabsUniversalScraperArgs(BaseModel):
    url: str = Field(description="Website URL")

    user_agent_type: str | None = None
    geo_location: str | None = None
    render: str | None = None
    content_encoding: str | None = None
    context: list | None = None
    callback_url: str | None = None
    parse: bool | None = None
    parsing_instructions: dict | None = None
    browser_instructions: dict | None = None


class OxylabsUniversalScraperTool(BaseTool):
    """
    Scrape any website with OxylabsUniversalScraperTool.

    Oxylabs API documentation:
    https://developers.oxylabs.io/scraper-apis/web-scraper-api/other-websites

    Get Oxylabs account:
    https://dashboard.oxylabs.io/en

    Args:
        username (str): Oxylabs username.
        password (str): Oxylabs password.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )
    name: str = "Oxylabs Universal Scraper tool"
    description: str = "Scrape any url with Oxylabs Universal Scraper"
    args_schema: Type[BaseModel] = OxylabsUniversalScraperArgs

    oxylabs_api: RealtimeClient

    def __init__(self, username: str, password: str, **kwargs):
        bits, _ = architecture()
        sdk_type = (
            f"oxylabs-crewai-sdk-python/"
            f"{version('crewai')} "
            f"({python_version()}; {bits})"
        )

        if OXYLABS_AVAILABLE:
            # import RealtimeClient to make it accessible for the current scope
            from oxylabs import RealtimeClient

            kwargs["oxylabs_api"] = RealtimeClient(
                username=username,
                password=password,
                sdk_type=sdk_type,
            )
        else:
            import click

            if click.confirm(
                "You are missing the 'oxylabs' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "oxylabs"], check=True)
                    from oxylabs import RealtimeClient

                    kwargs["oxylabs_api"] = RealtimeClient(
                        username=username,
                        password=password,
                        sdk_type=sdk_type,
                    )
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install oxylabs package")
            else:
                raise ImportError(
                    "`oxylabs` package not found, please run `uv add oxylabs`"
                )

        super().__init__(**kwargs)

    def _run(self, url: str, **kwargs) -> OxylabsResponse:
        return self.oxylabs_api.universal.scrape_url(url, **kwargs)
