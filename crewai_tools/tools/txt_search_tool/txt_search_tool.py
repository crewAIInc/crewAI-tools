from typing import Any, Optional, Type

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackDataType:
    TEXT_FILE = "text_file"

try:
    from embedchain.models.data_type import DataType
except ImportError:
    DataType = FallbackDataType


class FixedTXTSearchToolSchema(BaseModel):
    """Input for TXTSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the txt's content",
    )


class TXTSearchToolSchema(FixedTXTSearchToolSchema):
    """Input for TXTSearchTool."""

    txt: str = Field(..., description="Mandatory txt path you want to search")


class TXTSearchTool(RagTool):
    name: str = "Search a txt's content"
    description: str = (
        "A tool that can be used to semantic search a query from a txt's content."
    )
    args_schema: Type[BaseModel] = TXTSearchToolSchema

    def __init__(self, txt: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if txt is not None:
            try:
                kwargs["data_type"] = DataType.TEXT_FILE
                self.add(txt)
                self.description = f"A tool that can be used to semantic search a query the {txt} txt's content."
                self.args_schema = FixedTXTSearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for TXTSearchTool to function. Please install it with 'pip install embedchain'") from e

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
        if "txt" in kwargs:
            self.add(kwargs["txt"])

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
