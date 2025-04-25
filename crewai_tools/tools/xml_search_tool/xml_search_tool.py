from typing import Any, Optional, Type

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackDataType:
    XML = "xml"

try:
    from embedchain.models.data_type import DataType
except ImportError:
    DataType = FallbackDataType


class FixedXMLSearchToolSchema(BaseModel):
    """Input for XMLSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the XML's content",
    )


class XMLSearchToolSchema(FixedXMLSearchToolSchema):
    """Input for XMLSearchTool."""

    xml: str = Field(..., description="Mandatory xml path you want to search")


class XMLSearchTool(RagTool):
    name: str = "Search a XML's content"
    description: str = (
        "A tool that can be used to semantic search a query from a XML's content."
    )
    args_schema: Type[BaseModel] = XMLSearchToolSchema

    def __init__(self, xml: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if xml is not None:
            try:
                kwargs["data_type"] = DataType.XML
                self.add(xml)
                self.description = f"A tool that can be used to semantic search a query the {xml} XML's content."
                self.args_schema = FixedXMLSearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for XMLSearchTool to function. Please install it with 'pip install embedchain'") from e

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
        if "xml" in kwargs:
            self.add(kwargs["xml"])

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
