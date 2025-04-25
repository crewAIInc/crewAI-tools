import sys
from unittest.mock import patch
import pytest

def test_file_writer_tool_import_without_embedchain():
    """
    Test that FileWriterTool can be imported without embedchain installed.
    """
    with patch.dict('sys.modules', {'embedchain': None}):
        from crewai_tools import FileWriterTool
        tool = FileWriterTool()
        assert tool.name == "File Writer Tool"
