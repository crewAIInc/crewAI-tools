from typing import Any, Dict, Type
from pydantic import BaseModel, Field, field_validator
from crewai.tools import BaseTool
from crewai import Agent, Task, Crew
import os
import json
try:
    from linkup import LinkupClient

    LINKUP_AVAILABLE = True
except ImportError:
    LINKUP_AVAILABLE = False
    LinkupClient = Any

class LinkupSearchToolSchema(BaseModel):
    """Input for LinkupBaseTool."""
   
    query: str = Field(
        ..., description="The query to search for."
    )

class LinkupSearchTool(BaseTool):
    name: str = "Linkup Search Tool"
    description: str = "A tool to search and retrieve trends or insights using the Linkup API."
    args_schema: Type[BaseModel] = LinkupSearchToolSchema


    def __init__(self, api_key: str, depth: str, output_type: str, structured_output_schema:str = None, **kwargs):
        from linkup import LinkupClient

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

    def _run(self, query: str ) :


        """
        Executes a search using the Linkup API.

        :param query: The query to search for.
        :return: The results or an error message.
        """

        api_params = {
            "query": query,
            "depth": self._default_depth,
            "output_type": self._default_output_type,
        }

        if self._default_output_type == "structured":
            if not self.structured_output_schema:
                raise ValueError("structured_output_schema must be provided when output_type is 'structured'.")
            api_params["structured_output_schema"] = self._default_structured_schema
        return self._client.search(**api_params)
