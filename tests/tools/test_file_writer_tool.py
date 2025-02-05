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

    @patch('pathlib.Path')
    def test_path_validation(self, mock_path):
        invalid_paths = [
            "../test.txt",
            "/absolute/path.txt",
            "test/../../file.txt",
            "test/" + "x" * 256 + ".txt"
        ]
        for path in invalid_paths:
            with self.assertRaises(ValueError):
                self.tool.run(filename=path, content=self.test_content)

    def test_file_size_limits(self):
        large_content = "x" * (self.test_config.default_max_size + 1)
        with self.assertRaises(ValueError):
            self.tool.run(filename="test.txt", content=large_content)

    def test_invalid_characters(self):
        invalid_filenames = [
            "test<file.txt",
            "test>file.txt",
            "test:file.txt",
            'test"file.txt',
            "test|file.txt",
            "test?file.txt",
            "test*file.txt",
            "test\\file.txt"
        ]
        for filename in invalid_filenames:
            with self.assertRaises(ValueError):
                self.tool.run(filename=filename, content=self.test_content)
