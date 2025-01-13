from typing import Any, Dict, Type
from pydantic import BaseModel, Field, field_validator
from crewai.tools import BaseTool

try:
    from linkup import LinkupClient
    LINKUP_AVAILABLE = True
except ImportError:
    LINKUP_AVAILABLE = False
    LinkupClient = Any

class LinkupSearchToolSchema(BaseModel):
    query: str = Field(..., description="The query to search for.")

    @field_validator("query")
    def validate_query(cls, value):
        if not isinstance(value, str):
            raise ValueError("Query must be a non-empty string.")
        return value.strip()

class LinkupSearchTool(BaseTool):
    name: str = "Linkup Search Tool"
    description: str = "A tool to search and retrieve trends or insights using the Linkup API."
    args_schema: Type[BaseModel] = LinkupSearchToolSchema

    def __init__(self, api_key: str, depth: str, output_type: str, structured_output_schema:str = None, **kwargs):
        super().__init__(**kwargs)
        if not LINKUP_AVAILABLE:
            raise ImportError(
                "The 'linkup' package is required to use the LinkupSearchTool. "
                "Please install it with: pip install linkup"
            )
        self._client = LinkupClient(api_key=api_key)
        self._default_depth = depth
        self._default_output_type = output_type
        self._default_structured_schema = structured_output_schema

    def _run(self, query: str, depth: str = None, output_type: str = None, structured_output_schema: str = None, **kwargs) -> Dict[str, Any]:
        if not isinstance(query, str):
            raise ValueError(f"Query must be a string, but got {type(query)}: {query}")
        depth= self._default_depth
        output_type= self._default_output_type
        structured_output_schema = structured_output_schema or self._default_structured_schema

        """
        Executes a search using the Linkup API.

        :param query: The query to search for.
        :param depth: Search depth (default is 'standard').
        :param output_type: Desired result type (default is 'searchResults').
        :return: A dictionary containing the results or an error message.
        """
        depth = depth or self._default_depth
        output_type = output_type or self._default_output_type

        api_params = {
        "query": query,
            "depth": depth,
            "output_type": output_type,
        }

        if output_type == "structured":
            if not structured_output_schema:
                raise ValueError("structured_output_schema must be provided when output_type is 'structured'.")
            api_params["structured_output_schema"] = structured_output_schema
        try:
            response = self._client.search(**api_params)
            if output_type == "structured" :
                return response
            else:
                return {"success": True, **vars(response)}
        except Exception as e:
            return {"success": False, "error": str(e)}
