from typing import Any, Optional, Type, Union

from pydantic import BaseModel, Field, model_validator

from ..rag.rag_tool import RagTool

class FallbackDataType:
    PDF_FILE = "pdf_file"

try:
    from embedchain.models.data_type import DataType
except ImportError:
    DataType = FallbackDataType


class FixedPDFSearchToolSchema(BaseModel):
    """Input for PDFSearchTool."""

    query: str = Field(
        ..., description="Mandatory query you want to use to search the PDF's content"
    )


class PDFSearchToolSchema(FixedPDFSearchToolSchema):
    """Input for PDFSearchTool."""

    pdf: str = Field(..., description="Mandatory pdf path you want to search")


class PDFSearchTool(RagTool):
    name: str = "Search a PDF's content"
    description: str = (
        "A tool that can be used to semantic search a query from a PDF's content."
    )
    args_schema: Type[BaseModel] = PDFSearchToolSchema

    def __init__(self, pdf: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if pdf is not None:
            try:
                kwargs["data_type"] = DataType.PDF_FILE
                self.add(pdf)
                self.description = f"A tool that can be used to semantic search a query the {pdf} PDF's content."
                self.args_schema = FixedPDFSearchToolSchema
                self._generate_description()
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for PDFSearchTool to function. Please install it with 'pip install embedchain'") from e

    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            try:
                from embedchain import App

                from crewai_tools.adapters.pdf_embedchain_adapter import (
                    PDFEmbedchainAdapter,
                )

                app = App.from_config(config=self.config) if self.config else App()
                self.adapter = PDFEmbedchainAdapter(
                    embedchain_app=app, summarize=self.summarize
                )
            except ImportError:
                pass

        return self

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
        if "pdf" in kwargs:
            try:
                self.add(kwargs["pdf"])
            except NotImplementedError as e:
                raise ImportError("Embedchain is required for PDFSearchTool to function. Please install it with 'pip install embedchain'") from e
