import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText

from crewai_tools.tools.pdf_text_writing_tool.pdf_text_writing_tool import (
    PDFTextWritingTool,
    PDFTextWritingToolSchema,
)


@pytest.fixture
def sample_pdf():
    """Create a simple PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        writer = PdfWriter()
        from pypdf import PageObject
        
        page = PageObject.create_blank_page(width=612, height=792)
        writer.add_page(page)
        
        with open(temp_file.name, "wb") as output_file:
            writer.write(output_file)
        
        yield temp_file.name
    
    os.unlink(temp_file.name)


@pytest.fixture
def sample_font_file():
    """Create a mock TTF font file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as temp_file:
        temp_file.write(b"mock font data")
        yield temp_file.name
    
    os.unlink(temp_file.name)


def test_pdf_text_writing_tool_schema():
    """Test the PDFTextWritingToolSchema validation."""
    schema = PDFTextWritingToolSchema(
        pdf_path="test.pdf",
        text="Hello World",
        position=(100, 200),
        font_size=14,
        font_color="0 0 1 rg",
        page_number=0
    )
    
    assert schema.pdf_path == "test.pdf"
    assert schema.text == "Hello World"
    assert schema.position == (100, 200)
    assert schema.font_size == 14
    assert schema.font_color == "0 0 1 rg"
    assert schema.page_number == 0


def test_pdf_text_writing_tool_initialization():
    """Test PDFTextWritingTool initialization."""
    tool = PDFTextWritingTool()
    
    assert tool.name == "PDF Text Writing Tool"
    assert "write text to a specific position in a PDF document" in tool.description
    assert tool.args_schema == PDFTextWritingToolSchema


def test_pdf_text_writing_tool_basic_functionality(sample_pdf):
    """Test basic text writing functionality."""
    tool = PDFTextWritingTool()
    
    result = tool.run(
        pdf_path=sample_pdf,
        text="Test Text",
        position=(100, 200),
        font_size=12,
        font_color="0 0 0 rg",
        page_number=0
    )
    
    assert "Text added to modified_output.pdf successfully" in result


def test_pdf_text_writing_tool_page_out_of_range(sample_pdf):
    """Test error handling for page number out of range."""
    tool = PDFTextWritingTool()
    
    result = tool.run(
        pdf_path=sample_pdf,
        text="Test Text",
        position=(100, 200),
        font_size=12,
        font_color="0 0 0 rg",
        page_number=999
    )
    
    assert result == "Page number out of range."


def test_pdf_text_writing_tool_missing_font_file(sample_pdf):
    """Test that font file parameter is ignored (not supported)."""
    tool = PDFTextWritingTool()
    
    result = tool.run(
        pdf_path=sample_pdf,
        text="Test Text",
        position=(100, 200),
        font_size=12,
        font_color="0 0 0 rg",
        font_file="nonexistent_font.ttf",
        page_number=0
    )
    
    assert "Text added to modified_output.pdf successfully" in result


def test_pdf_text_writing_tool_with_custom_font(sample_pdf, sample_font_file):
    """Test text writing with custom font (currently not supported)."""
    tool = PDFTextWritingTool()
    
    result = tool.run(
        pdf_path=sample_pdf,
        text="Test Text",
        position=(100, 200),
        font_size=12,
        font_color="0 0 0 rg",
        font_file=sample_font_file,
        page_number=0
    )
    
    assert "Text added to modified_output.pdf successfully" in result


def test_pdf_text_writing_tool_different_positions(sample_pdf):
    """Test text writing at different positions."""
    tool = PDFTextWritingTool()
    
    positions = [(50, 100), (200, 300), (400, 500)]
    
    for position in positions:
        result = tool.run(
            pdf_path=sample_pdf,
            text=f"Text at {position}",
            position=position,
            font_size=12,
            font_color="0 0 0 rg",
            page_number=0
        )
        
        assert "Text added to modified_output.pdf successfully" in result


def test_pdf_text_writing_tool_different_font_sizes(sample_pdf):
    """Test text writing with different font sizes."""
    tool = PDFTextWritingTool()
    
    font_sizes = [8, 12, 16, 24]
    
    for font_size in font_sizes:
        result = tool.run(
            pdf_path=sample_pdf,
            text=f"Size {font_size} text",
            position=(100, 200),
            font_size=font_size,
            font_color="0 0 0 rg",
            page_number=0
        )
        
        assert "Text added to modified_output.pdf successfully" in result


def test_pdf_text_writing_tool_different_colors(sample_pdf):
    """Test text writing with different colors."""
    tool = PDFTextWritingTool()
    
    colors = ["0 0 0 rg", "1 0 0 rg", "0 1 0 rg", "0 0 1 rg"]
    
    for color in colors:
        result = tool.run(
            pdf_path=sample_pdf,
            text="Colored text",
            position=(100, 200),
            font_size=12,
            font_color=color,
            page_number=0
        )
        
        assert "Text added to modified_output.pdf successfully" in result
