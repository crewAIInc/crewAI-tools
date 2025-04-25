from typing import Any, Optional, Type, Union

from pydantic import BaseModel, Field

from ..rag.rag_tool import RagTool

class FallbackDataType:
    CSV = "csv"

try:
    from embedchain.models.data_type import DataType
except ImportError:
    DataType = FallbackDataType


class FixedCSVSearchToolSchema(BaseModel):
    """Input for CSVSearchTool."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to search the CSV's content",
    )


class CSVSearchToolSchema(FixedCSVSearchToolSchema):
    """Input for CSVSearchTool."""

    csv: str = Field(..., description="Mandatory csv path you want to search")


class CSVSearchTool(RagTool):
    name: str = "Search a CSV's content"
    description: str = (
        "A tool that can be used to semantic search a query from a CSV's content."
    )
    args_schema: Type[BaseModel] = CSVSearchToolSchema

    def __init__(self, csv: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if csv is not None:
            try:
                kwargs["data_type"] = DataType.CSV
                self.add(csv)
                self.description = f"A tool that can be used to semantic search a query the {csv} CSV's content."
                self.args_schema = FixedCSVSearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for CSVSearchTool to function. Please install it with 'pip install embedchain'") from e

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
        if "csv" in kwargs:
            try:
                self.add(kwargs["csv"])
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for CSVSearchTool to function. Please install it with 'pip install embedchain'") from e

    def _run(
        self,
        search_query: str,
        **kwargs: Any,
    ) -> Any:
        return super()._run(query=search_query, **kwargs)
