from typing import Any, Optional, Type, Union

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackDataType:
    DOCX = "docx"

try:
    from embedchain.models.data_type import DataType
except ImportError:
    DataType = FallbackDataType


class FixedDOCXSearchToolSchema(BaseModel):
    """Input for DOCXSearchTool."""

    docx: Optional[str] = Field(
        ..., description="Mandatory docx path you want to search"
    )
    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the DOCX's content",
    )


class DOCXSearchToolSchema(FixedDOCXSearchToolSchema):
    """Input for DOCXSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the DOCX's content",
    )


class DOCXSearchTool(RagTool):
    name: str = "Search a DOCX's content"
    description: str = (
        "A tool that can be used to semantic search a query from a DOCX's content."
    )
    args_schema: Type[BaseModel] = DOCXSearchToolSchema

    def __init__(self, docx: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if docx is not None:
            try:
                kwargs["data_type"] = DataType.DOCX
                self.add(docx)
                self.description = f"A tool that can be used to semantic search a query the {docx} DOCX's content."
                self.args_schema = FixedDOCXSearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for DOCXSearchTool to function. Please install it with 'pip install embedchain'") from e

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
        if "docx" in kwargs:
            try:
                self.add(kwargs["docx"])
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for DOCXSearchTool to function. Please install it with 'pip install embedchain'") from e

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        search_query = kwargs.get("search_query")
        if search_query is None:
            search_query = kwargs.get("query")

        docx = kwargs.get("docx")
        if docx is not None:
            try:
                self.add(docx)
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for DOCXSearchTool to function. Please install it with 'pip install embedchain'") from e
        return super()._run(query=search_query, **kwargs)
