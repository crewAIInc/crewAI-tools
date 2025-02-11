from typing import Any, Optional, Type, Literal
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from pydantic import PrivateAttr

try:
    from valyu import Valyu

    VALYU_INSTALLED = True
except ImportError:
    Valyu = Any
    VALYU_INSTALLED = False


class ValyuBaseToolSchema(BaseModel):
    query: str = Field(..., description="The question or topic you want information on")
    search_type: Literal["proprietary", "web", "both"] = Field(
        default="both",
        description="Whether to search in proprietary sources, web, or both",
    )
    data_sources: Optional[str] = Field(
        None, description="Choose which indexes to only query from"
    )
    num_query: Optional[int] = Field(
        default=10, description="Number of query variations generated"
    )
    num_results: Optional[int] = Field(
        default=10, description="Maximum number of results returned"
    )
    max_price: Optional[float] = Field(
        default=100, description="The maximum allowed price per content in PCM"
    )


class ValyuContextTool(BaseTool):
    name: str = "Valyu Search Tool"
    description: str = "Search programmatically licensed proprietary data and the web"
    args_schema: Type[BaseModel] = ValyuBaseToolSchema
    _client: Valyu = PrivateAttr()

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        if not VALYU_INSTALLED:
            import click

            if click.confirm(
                "You are missing the 'valyu' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "valyu"], check=True)
            else:
                raise ImportError(
                    "You are missing the 'valyu' package. Please install it."
                )
        self._client = Valyu(api_key=api_key)

    def _run(
        self,
        query: str,
        search_type: str = "both",
        data_sources: Optional[str] = None,
        num_query: int = 10,
        num_results: int = 10,
        max_price: int = 100,
    ) -> Any:
        try:
            params = {
                "query": query,
                "search_type": search_type,
                "num_query": num_query,
                "num_results": num_results,
                "max_price": max_price,
            }

            if data_sources:
                params["data_sources"] = data_sources

            response = self._client.context(**params)

            results = [
                {
                    "name": result.name,
                    "url": result.url,
                    "content": result.content,
                    "source": result.source,
                    "price": result.price,
                    "organization": result.orgname,
                    "source_type": result.source_type,
                }
                for result in response.results
            ]

            return {"success": True, "results": results}

        except Exception as e:
            return {"success": False, "error": str(e)}
