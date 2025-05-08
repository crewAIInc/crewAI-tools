from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Any, Union, List, Literal
from dotenv import load_dotenv
import os
import json

load_dotenv()
try:
    from tavily import TavilyClient, AsyncTavilyClient

    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilyClient = Any
    AsyncTavilyClient = Any


class TavilyExtractorToolSchema(BaseModel):
    """Input schema for TavilyExtractorTool."""

    urls: Union[List[str], str] = Field(
        ...,
        description="The URL(s) to extract data from. Can be a single URL or a list of URLs.",
    )
    include_images: Optional[bool] = Field(
        default=False,
        description="Whether to include images in the extraction.",
    )
    extract_depth: Literal["basic", "advanced"] = Field(
        default="basic",
        description="The depth of extraction. 'basic' for basic extraction, 'advanced' for advanced extraction.",
    )
    timeout: int = Field(
        default=60,
        description="The timeout for the extraction request in seconds.",
    )


class TavilyExtractorTool(BaseTool):
    """
    Tool that uses the Tavily API to extract content from web pages.

    Attributes:
        client: Synchronous Tavily client.
        async_client: Asynchronous Tavily client.
        name: The name of the tool.
        description: The description of the tool.
        args_schema: The schema for the tool's arguments.
        api_key: The Tavily API key.
        proxies: Optional proxies for the API requests.
    """

    model_config = {}
    client: TavilyClient = None
    async_client: AsyncTavilyClient = None
    name: str = "TavilyExtractorTool"
    description: str = (
        "Extracts content from one or more web pages using the Tavily API. Returns structured data."
    )
    args_schema: Type[BaseModel] = TavilyExtractorToolSchema
    api_key: Optional[str] = Field(
        default=os.getenv("TAVILY_API_KEY"),
        description="The Tavily API key. If not provided, it will be loaded from the environment variable TAVILY_API_KEY.",
    )
    proxies: Optional[dict[str, str]] = Field(
        default=None,
        description="Optional proxies to use for the Tavily API requests.",
    )

    def __init__(self, **kwargs):
        """
        Initializes the TavilyExtractorTool.

        Args:
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        if TAVILY_AVAILABLE:
            self.client = TavilyClient(api_key=self.api_key, proxies=self.proxies)
            self.async_client = AsyncTavilyClient(
                api_key=self.api_key, proxies=self.proxies
            )
        else:
            import click

            if click.confirm(
                "The 'tavily-python' package is required to use the TavilyExtractorTool. "
                "Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "tavily-python"], check=True)
            else:
                raise ImportError(
                    "The 'tavily-python' package is required to use the TavilyExtractorTool. "
                    "Please install it with: uv add tavily-python"
                )

    def _run(
        self,
        urls: Union[List[str], str],
        include_images: bool = False,
        extract_depth: Literal["basic", "advanced"] = "basic",
        timeout: int = 60,
    ) -> str:
        """
        Synchronously extracts content from the given URL(s).

        Args:
            urls: The URL(s) to extract data from.
            include_images: Whether to include images in the extraction.
            extract_depth: The depth of extraction ('basic' or 'advanced').
            timeout: The timeout for the request in seconds.

        Returns:
            A JSON string containing the extracted data.
        """
        return json.dumps(
            self.client.extract(
                urls=urls,
                extract_depth=extract_depth,
                include_images=include_images,
                timeout=timeout,
            ),
            indent=2,
        )

    async def _arun(
        self,
        urls: Union[List[str], str],
        include_images: bool = False,
        extract_depth: Literal["basic", "advanced"] = "basic",
        timeout: int = 60,
    ) -> str:
        """
        Asynchronously extracts content from the given URL(s).

        Args:
            urls: The URL(s) to extract data from.
            include_images: Whether to include images in the extraction.
            extract_depth: The depth of extraction ('basic' or 'advanced').
            timeout: The timeout for the request in seconds.

        Returns:
            A JSON string containing the extracted data.
        """
        return json.dumps(
            self.async_client.extract(
                urls=urls,
                extract_depth=extract_depth,
                include_images=include_images,
                timeout=timeout,
            ),
            indent=2,
        )
