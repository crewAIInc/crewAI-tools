from typing import Any, Dict, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

try:
    from linkup import LinkupClient
    LINKUP_AVAILABLE = True
except ImportError:
    LINKUP_AVAILABLE = False
    LinkupClient = Any

class LinkupSearchToolSchema(BaseModel):
    query: str = Field(..., description="The query to search for.")
    depth: str = Field(default="standard", description="Search depth (default is 'standard').")
    output_type: str = Field(
        default="searchResults", description="Desired result type (default is 'searchResults')."
    )


class LinkupSearchTool(BaseTool):
    name: str = "Linkup Search Tool"
    description: str = "A tool to search and retrieve trends or insights using the Linkup API."
    args_schema: Type[BaseModel] = LinkupSearchToolSchema

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        if not LINKUP_AVAILABLE:
            raise ImportError(
                "The 'linkup' package is required to use the LinkupSearchTool. "
                "Please install it with: pip install linkup"
            )
        self._client = LinkupClient(api_key=api_key)

    def _run(self, query: str, depth: str = "standard", output_type: str = "searchResults") -> Dict[str, Any]:
        """
        Executes a search using the Linkup API.

        :param query: The query to search for.
        :param depth: Search depth (default is 'standard').
        :param output_type: Desired result type (default is 'searchResults').
        :return: A dictionary containing the results or an error message.
        """
        try:
            response = self._client.search(query=query, depth=depth, output_type=output_type)
            results = [
                {"name": result.name, "url": result.url, "content": result.content}
                for result in response.results
            ]
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
