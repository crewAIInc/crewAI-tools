from typing import Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from linkup import LinkupClient
    LINKUP_AVAILABLE = True
except ImportError as e:
    LINKUP_AVAILABLE = False
    LinkupClient = Any

class LinkupSearchToolSchema(BaseModel):
    query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the web",
        min_length=1,
        max_length=500
    )
    depth: str = Field(
        default="standard",
        description="Search depth level (standard/deep)",
        pattern="^(standard|deep)$"
    )
    output_type: str = Field(
        default="searchResults",
        description="The type of the output (searchResults/sourcedAnswer)",
        pattern="^(searchResults|sourcedAnswer)$"
    )

class LinkupSearchTool(BaseTool):
    """
    A tool for performing web searches using the Linkup API.
    """
    name: str = "Linkup Search Tool"
    description: str = "Search the web using Linkup"
    args_schema: Type[BaseModel] = LinkupSearchToolSchema
    linkup: Optional["LinkupClient"] = None
    depth: str = ""
    output_type: str = "searchResults"

    def __init__(
        self,
        api_key: str,
        depth: str = "standard",
        output_type: str = "searchResults",
        **kwargs
    ) -> None:
        if not api_key:
            raise ValueError("API key is required")
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
        self.output_type = output_type

    def _run(self, query: str, depth: str, output_type: str) -> dict:
        try:
            response = self.linkup.search(query=query, depth=depth, output_type=output_type)
            return response
        except Exception as e:
            return {"status": "error", "message": str(e)}

