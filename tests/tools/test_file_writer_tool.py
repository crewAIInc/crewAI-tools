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

    @patch('builtins.open')
    def test_progress_tracking(self, mock_open):
        progress_calls = []
        def progress_callback(written, total):
            progress_calls.append((written, total))

        content = "x" * (self.test_config.chunk_size * 3)
        self.tool.run(
            filename="test.txt",
            content=content,
            progress_callback=progress_callback
        )

        self.assertEqual(len(progress_calls), 3)
        self.assertEqual(progress_calls[-1][0], len(content))
        self.assertEqual(progress_calls[-1][1], len(content))

    @patch('builtins.open')
    def test_progress_error_propagation(self, mock_open):
        mock_open.side_effect = IOError("Test error")
        progress_calls = []
        
        with self.assertRaises(IOError):
            self.tool.run(
                filename="test.txt",
                content=self.test_content,
                progress_callback=lambda w, t: progress_calls.append((w, t))
            )
        
        self.assertEqual(len(progress_calls), 0)

    def test_chunk_size_handling(self):
        custom_chunk_size = 100
        content = "x" * (custom_chunk_size * 2 + 50)  # 250 bytes
        progress_calls = []
        
        self.tool.run(
            filename="test.txt",
            content=content,
            chunk_size=custom_chunk_size,
            progress_callback=lambda w, t: progress_calls.append((w, t))
        )
        
        self.assertEqual(len(progress_calls), 3)  # 100, 200, 250 bytes
        self.assertEqual(progress_calls[0][0], custom_chunk_size)
        self.assertEqual(progress_calls[1][0], custom_chunk_size * 2)
        self.assertEqual(progress_calls[2][0], len(content))
