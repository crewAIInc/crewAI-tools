import unittest
from unittest.mock import patch, Mock
from pathlib import Path

from crewai_tools.tools.file_writer_tool.file_writer_tool import (
    FileWriterTool,
    FileWriterConfig,
)


class TestFileWriterTool(unittest.TestCase):
    def setUp(self):
        self.tool = FileWriterTool()
        self.test_content = "Test content"
        self.test_config = FileWriterConfig()

    def test_tool_initialization(self):
        self.assertIsInstance(self.tool, FileWriterTool)
        self.assertEqual(self.tool.name, "File Writer Tool")
        self.assertTrue(self.tool.description)
        self.assertEqual(self.tool.args_schema, FileWriterConfig)
