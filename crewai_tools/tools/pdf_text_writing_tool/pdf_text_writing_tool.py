from pathlib import Path
from typing import Optional, Type

from pydantic import BaseModel, Field
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText

from crewai_tools.tools.rag.rag_tool import RagTool


class PDFTextWritingToolSchema(BaseModel):
    """Input schema for PDFTextWritingTool."""

    pdf_path: str = Field(..., description="Path to the PDF file to modify")
    text: str = Field(..., description="Text to add to the PDF")
    position: tuple = Field(
        ..., description="Tuple of (x, y) coordinates for text placement"
    )
    font_size: int = Field(default=12, description="Font size of the text")
    font_color: str = Field(
        default="0 0 0 rg", description="RGB color code for the text"
    )
    font_name: Optional[str] = Field(
        default="F1", description="Font name for standard fonts"
    )
    font_file: Optional[str] = Field(
        None, description="Path to a .ttf font file for custom font usage (currently not supported)"
    )
    page_number: int = Field(default=0, description="Page number to add text to")


class PDFTextWritingTool(RagTool):
    """A tool to add text to specific positions in a PDF, with custom font support."""

    name: str = "PDF Text Writing Tool"
    description: str = (
        "A tool that can write text to a specific position in a PDF document, with optional custom font embedding."
    )
    args_schema: Type[BaseModel] = PDFTextWritingToolSchema

    def run(
        self,
        pdf_path: str,
        text: str,
        position: tuple,
        font_size: int,
        font_color: str,
        font_name: str = "Arial",
        font_file: Optional[str] = None,
        page_number: int = 0,
    ) -> str:
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()

            if page_number >= len(reader.pages):
                return "Page number out of range."

            for page in reader.pages:
                writer.add_page(page)

            x_position, y_position = position
            rect = (x_position, y_position, x_position + 200, y_position + 50)
            
            if font_color == "0 0 0 rg":
                color = "000000"  # black
            elif font_color == "1 0 0 rg":
                color = "ff0000"  # red
            elif font_color == "0 1 0 rg":
                color = "00ff00"  # green
            elif font_color == "0 0 1 rg":
                color = "0000ff"  # blue
            else:
                color = "000000"  # default to black

            annotation = FreeText(
                text=text,
                rect=rect,
                font=font_name,
                font_size=f"{font_size}pt",
                font_color=color,
            )

            writer.add_annotation(page_number=page_number, annotation=annotation)

            # Save the new PDF
            output_pdf_path = "modified_output.pdf"
            with open(output_pdf_path, "wb") as out_file:
                writer.write(out_file)

            return f"Text added to {output_pdf_path} successfully."
            
        except Exception as e:
            return f"Error adding text to PDF: {str(e)}"
