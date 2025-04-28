import pytest
from unittest.mock import patch

from crewai_tools.adapters.custom_adapter import CustomAdapter
from crewai_tools.adapters.custom_pdf_adapter import CustomPDFAdapter
from crewai_tools.tools.rag.rag_tool import RagTool
from crewai_tools.tools.pdf_search_tool.pdf_search_tool import PDFSearchTool


def test_custom_adapter():
    """Test that the custom adapter can be used."""
    adapter = CustomAdapter()
    adapter.add("test_source", "test_content")
    result = adapter.query("test_query")
    assert "test_content" in result


def test_custom_pdf_adapter():
    """Test that the custom PDF adapter can be used."""
    adapter = CustomPDFAdapter()
    adapter.add("test.pdf")
    result = adapter.query("test_query")
    assert "test.pdf" in result


@patch("importlib.import_module")
def test_rag_tool_with_custom_adapter(mock_import):
    """Test that RagTool can use the custom adapter when embedchain is not available."""
    mock_import.side_effect = lambda name, *args, **kwargs: __import__('builtins') if name != 'embedchain' else exec('raise ImportError("Module not found")')
    
    tool = RagTool()
    
    assert isinstance(tool.adapter, CustomAdapter)


@patch("importlib.import_module")
def test_pdf_search_tool_with_custom_adapter(mock_import):
    """Test that PDFSearchTool can use the custom adapter when embedchain is not available."""
    mock_import.side_effect = lambda name, *args, **kwargs: __import__('builtins') if name != 'embedchain' else exec('raise ImportError("Module not found")')
    
    tool = PDFSearchTool()
    
    assert isinstance(tool.adapter, CustomPDFAdapter)
