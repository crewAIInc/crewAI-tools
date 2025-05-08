from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Any, Union, Literal, Sequence
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


class TavilySearchToolSchema(BaseModel):
    """Input schema for TavilySearchTool."""

    query: str = Field(..., description="The search query string.")
    search_depth: Literal["basic", "advanced"] = Field(
        "basic", description="The depth of the search."
    )
    topic: Literal["general", "news", "finance"] = Field(
        "general", description="The topic to focus the search on."
    )
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(
        None, description="The time range for the search."
    )
    days: int = Field(7, description="The number of days to search back.")
    max_results: int = Field(5, description="The maximum number of results to return.")
    include_domains: Optional[Sequence[str]] = Field(
        None, description="A list of domains to include in the search."
    )
    exclude_domains: Optional[Sequence[str]] = Field(
        None, description="A list of domains to exclude from the search."
    )
    include_answer: Union[bool, Literal["basic", "advanced"]] = Field(
        False, description="Whether to include a direct answer to the query."
    )
    include_raw_content: bool = Field(
        False, description="Whether to include the raw content of the search results."
    )
    include_images: bool = Field(
        False, description="Whether to include images in the search results."
    )
    timeout: int = Field(
        60, description="The timeout for the search request in seconds."
    )


class TavilySearchTool(BaseTool):
    """
    Tool that uses the Tavily Search API to perform web searches.

    Attributes:
        client: An instance of TavilyClient.
        async_client: An instance of AsyncTavilyClient.
        name: The name of the tool.
        description: A description of the tool's purpose.
        args_schema: The schema for the tool's arguments.
        api_key: The Tavily API key.
        proxies: Optional proxies for the API requests.
    """

    model_config = {}
    client: TavilyClient = None
    async_client: AsyncTavilyClient = None
    name: str = "Tavily Search"
    description: str = (
        "A tool that performs web searches using the Tavily Search API. "
        "It returns a JSON object containing the search results."
    )
    args_schema: Type[BaseModel] = TavilySearchToolSchema
    api_key: Optional[str] = Field(
        default=os.getenv("TAVILY_API_KEY"),
        description="The Tavily API key. If not provided, it will be loaded from the environment variable TAVILY_API_KEY.",
    )
    proxies: Optional[dict[str, str]] = Field(
        default=None,
        description="Optional proxies to use for the Tavily API requests.",
    )

    def __init__(self, **kwargs):
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
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: Literal["general", "news", "finance"] = "general",
        time_range: Optional[Literal["day", "week", "month", "year"]] = None,
        days: int = 7,
        max_results: int = 5,
        include_domains: Optional[Sequence[str]] = None,
        exclude_domains: Optional[Sequence[str]] = None,
        include_answer: Union[bool, Literal["basic", "advanced"]] = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        timeout: int = 60,
    ) -> str:
        """
        Synchronously performs a search using the Tavily API.

        Args:
            query: The search query string.
            search_depth: The depth of the search ('basic' or 'advanced').
            topic: The topic to focus the search on ('general', 'news', 'finance').
            time_range: The time range for the search ('day', 'week', 'month', 'year').
            days: The number of days to search back.
            max_results: The maximum number of results to return.
            include_domains: A list of domains to include in the search.
            exclude_domains: A list of domains to exclude from the search.
            include_answer: Whether to include a direct answer to the query.
            include_raw_content: Whether to include the raw content of the search results.
            include_images: Whether to include images in the search results.
            timeout: The timeout for the search request in seconds.

        Returns:
            A JSON string containing the search results.
        """
        return json.dumps(
            self.client.search(
                query=query,
                search_depth=search_depth,
                topic=topic,
                time_range=time_range,
                days=days,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_images=include_images,
                timeout=timeout,
            ),
            indent=2,
        )

    async def _arun(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: Literal["general", "news", "finance"] = "general",
        time_range: Optional[Literal["day", "week", "month", "year"]] = None,
        days: int = 7,
        max_results: int = 5,
        include_domains: Optional[Sequence[str]] = None,
        exclude_domains: Optional[Sequence[str]] = None,
        include_answer: Union[bool, Literal["basic", "advanced"]] = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        timeout: int = 60,
    ) -> str:
        """
        Asynchronously performs a search using the Tavily API.

        Args:
            query: The search query string.
            search_depth: The depth of the search ('basic' or 'advanced').
            topic: The topic to focus the search on ('general', 'news', 'finance').
            time_range: The time range for the search ('day', 'week', 'month', 'year').
            days: The number of days to search back.
            max_results: The maximum number of results to return.
            include_domains: A list of domains to include in the search.
            exclude_domains: A list of domains to exclude from the search.
            include_answer: Whether to include a direct answer to the query.
            include_raw_content: Whether to include the raw content of the search results.
            include_images: Whether to include images in the search results.
            timeout: The timeout for the search request in seconds.

        Returns:
            A JSON string containing the search results.
        """
        return json.dumps(
            self.async_client.search(
                query=query,
                search_depth=search_depth,
                topic=topic,
                time_range=time_range,
                days=days,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_images=include_images,
                timeout=timeout,
            ),
            indent=2,
        )
