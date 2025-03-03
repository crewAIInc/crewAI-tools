from typing import Any, Optional, List, Literal
from crewai.tools import BaseTool
from pydantic import PrivateAttr, Field

try:
    from valyu import Valyu

    VALYU_INSTALLED = True
except ImportError:
    Valyu = Any
    VALYU_INSTALLED = False


class ValyuContextTool(BaseTool):
    name: str = "Valyu Search Tool"
    description: str = (
        "Search programmatically licensed proprietary data and the web. "
        "Parameters:\n"
        "- search_type: 'both' searches all sources, 'proprietary' for proprietary data not found on the web only, 'web' for web data only\n"
        "- max_price: Maximum price threshold. The number of dollars per 1000 results (PCM). (a number between 10 and 100 recommended)\n"
        "- num_query: Number of search queries to generate (a value of 5 is recommended)\n"
        "- num_results: Number of results to return (must be ≤ num_query)\n"
        "- data_sources: List of specific data sources to search from (only include valid sources)\n"
        "\nOnly add a data source if you have been instructed to do so and are sure it is a valid source."
    )
    _client: Any = PrivateAttr()
    search_type: Optional[str] = Field(default="both")
    max_price: Optional[int] = Field(default=None)
    max_num_results: Optional[int] = Field(default=None)
    query_rewrite: Optional[bool] = Field(default=False)
    similarity_threshold: Optional[float] = Field(default=0.4)
    data_sources: Optional[List[str]] = Field(default=None)

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the tool with an API key.
        """
        super().__init__(**kwargs)
        try:
            from valyu import Valyu
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'valyu' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "valyu"], check=True)
                from valyu import Valyu
            else:
                raise ImportError(
                    "The 'valyu' package is required to use the ValyuContextTool. "
                    "Please install it with: uv add valyu"
                )
        self._client = Valyu(api_key=api_key) if api_key else Valyu()
        if "max_price" in kwargs:
            self.max_price = kwargs["max_price"]
        if "search_type" in kwargs:
            self.search_type = kwargs["search_type"]

        if "max_num_results" in kwargs:
            self.max_num_results = kwargs["max_num_results"]
        if "query_rewrite" in kwargs:
            self.query_rewrite = kwargs["query_rewrite"]
        if "similarity_threshold" in kwargs:
            self.similarity_threshold = kwargs["similarity_threshold"]
        if "data_sources" in kwargs:
            self.data_sources = kwargs["data_sources"]

    def _run(
        self,
        query: str = Field(),
        search_type: Optional[Literal["both", "proprietary", "web"]] = Field(
            default=None
        ),
        data_sources: Optional[List[str]] = Field(default=None),
        max_num_results: Optional[int] = Field(default=None),
        query_rewrite: Optional[bool] = Field(default=None),
        similarity_threshold: Optional[float] = Field(default=None),
        max_price: Optional[int] = Field(default=None),
    ) -> Any:
        """Execute a search query using the Valyu API.

        Args:
            query (str): The search query to execute.
            search_type (Optional[Literal["both", "proprietary", "web"]]): Type of search to perform.
                'both' searches all sources, 'proprietary' for proprietary data only, 'web' for web data only.
            data_sources (Optional[List[str]]): List of specific data sources to search from.
            max_num_results (Optional[int]): Maximum number of results to return.
            query_rewrite (Optional[bool]): Whether to rewrite the query.
            similarity_threshold (Optional[float]): Similarity threshold for the query rewrite.
            max_price (Optional[int]): Maximum price threshold per 1000 results (PCM).

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the query was successful
                - results (List[dict]): List of search results if successful, each containing:
                    - title (str): Title of the result
                    - url (str): URL of the result
                    - content (str): Content of the result
                    - source (str): Source of the result
                    - price (float): Price of the result
                - error (str): Error message if unsuccessful
        """

        params = {
            "query": query,
            "search_type": self.search_type or search_type,
            "max_num_results": self.max_num_results or max_num_results,
            "query_rewrite": self.query_rewrite or query_rewrite,
            "similarity_threshold": self.similarity_threshold or similarity_threshold,
            "max_price": self.max_price or max_price,
        }

        if data_sources:
            params["data_sources"] = data_sources

        response = self._client.context(**params)

        if response.success:
            results = [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "source": result.source,
                    "price": result.price,
                }
                for result in response.results
            ]

            return {"success": True, "results": results}
        else:
            return {"success": False, "error": response.error}
