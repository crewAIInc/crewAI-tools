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
    num_query: Optional[int] = Field(default=None)
    num_results: Optional[int] = Field(default=None)
    data_sources: Optional[List[str]] = Field(default=None)

    def __init__(self, api_key: str, **kwargs):
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
        self._client = Valyu(api_key=api_key)
        if "max_price" in kwargs:
            self.max_price = kwargs["max_price"]
        if "search_type" in kwargs:
            self.search_type = kwargs["search_type"]
        if "num_query" in kwargs:
            self.num_query = kwargs["num_query"]
        if "num_results" in kwargs:
            self.num_results = kwargs["num_results"]
        if "data_sources" in kwargs:
            self.data_sources = kwargs["data_sources"]

    def _run(
        self,
        query: str = Field(),
        search_type: Optional[Literal["both", "proprietary", "web"]] = Field(
            default=None
        ),
        data_sources: Optional[List[str]] = Field(default=None),
        num_query: Optional[int] = Field(default=None),
        num_results: Optional[int] = Field(default=None),
        max_price: Optional[int] = Field(default=None),
    ) -> Any:
        # Validate num_query and num_results
        final_num_query = self.num_query or num_query
        final_num_results = self.num_results or num_results
        if (
            final_num_query is not None
            and final_num_results is not None
            and final_num_query < final_num_results
        ):
            return {
                "success": False,
                "error": "num_query must be greater than or equal to num_results",
            }

        params = {
            "query": query,
            "search_type": self.search_type or search_type,
            "num_query": final_num_query,
            "num_results": final_num_results,
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
