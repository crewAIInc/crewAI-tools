from typing import Any, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


try:
    from linkup import LinkupClient

    LINKUP_AVAILABLE = True
except ImportError:
    LINKUP_AVAILABLE = False
    LinkupClient = Any


class LinkupSearchToolSchema(BaseModel):
    query: str = Field(..., description="Mandatory search query you want to use to search the web")


class LinkupSearchTool(BaseTool):
    name: str = "Linkup Search Tool"
    description: str = "Search the web using Linkup"
    args_schema: Type[BaseModel] = LinkupSearchToolSchema
    linkup: Optional["LinkupClient"] = None
    depth: str = ""
    output_type: str = "searchResults"

    def __init__(self, api_key: str, depth: str, **kwargs):
        super().__init__(**kwargs)

        if not LINKUP_AVAILABLE:
            import click

            if click.confirm(
                "You are missing the 'linkup-sdk' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "linkup-sdk"], check=True)
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install 'linkup-sdk' package")

        from linkup import LinkupClient

        self.linkup = LinkupClient(api_key=api_key)
        self.depth = depth

    def _run(self, query: str):
        return self.linkup.search(
            query=query, depth=self.depth, output_type=self.output_type
        )
