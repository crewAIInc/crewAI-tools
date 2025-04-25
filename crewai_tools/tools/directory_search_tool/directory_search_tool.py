from typing import Any, Optional, Type, Union

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackDirectoryLoader:
    def __init__(self, **kwargs):
        pass

try:
    from embedchain.loaders.directory_loader import DirectoryLoader
except ImportError:
    DirectoryLoader = FallbackDirectoryLoader


class FixedDirectorySearchToolSchema(BaseModel):
    """Input for DirectorySearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the directory's content",
    )


class DirectorySearchToolSchema(FixedDirectorySearchToolSchema):
    """Input for DirectorySearchTool."""

    directory: str = Field(..., description="Mandatory directory you want to search")


class DirectorySearchTool(RagTool):
    name: str = "Search a directory's content"
    description: str = (
        "A tool that can be used to semantic search a query from a directory's content."
    )
    args_schema: Type[BaseModel] = DirectorySearchToolSchema

    def __init__(self, directory: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if directory is not None:
            try:
                kwargs["loader"] = DirectoryLoader(config=dict(recursive=True))
                self.add(directory)
                self.description = f"A tool that can be used to semantic search a query the {directory} directory's content."
                self.args_schema = FixedDirectorySearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for DirectorySearchTool to function. Please install it with 'pip install embedchain'") from e

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().add(*args, **kwargs)

    def _before_run(
        self,
        query: str,
        **kwargs: Any,
    ) -> Any:
        if "directory" in kwargs:
            try:
                self.add(kwargs["directory"])
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for DirectorySearchTool to function. Please install it with 'pip install embedchain'") from e

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
