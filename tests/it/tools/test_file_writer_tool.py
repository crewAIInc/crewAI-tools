import pytest
from pathlib import Path

from crewai_tools.tools.file_writer_tool.file_writer_tool import FileWriterTool


@pytest.mark.integration
class TestFileWriterToolIntegration:
    @pytest.fixture
    def tool(self):
        return FileWriterTool()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        return tmp_path

    def test_cross_platform_paths(self, tool, temp_dir):
        test_paths = [
            "test.txt",
            "dir/test.txt",
            "dir\\test.txt"
        ]
        content = "test content"
        
        for path in test_paths:
            result = tool.run(
                filename=path,
                content=content,
                directory=str(temp_dir)
            )
            assert "successfully" in result
            full_path = temp_dir / Path(path).name
            assert full_path.exists()
            assert full_path.read_text() == content

    def test_progress_tracking_real(self, tool, temp_dir):
        progress_calls = []
        content = "x" * (1024 * 1024)  # 1MB
        
        tool.run(
            filename="large.txt",
            content=content,
            directory=str(temp_dir),
            progress_callback=lambda w, t: progress_calls.append((w, t))
        )
        
        assert len(progress_calls) > 1
        assert progress_calls[-1][0] == len(content)

    def test_nested_directory_creation(self, tool, temp_dir):
        nested_dir = temp_dir / "level1" / "level2"
        content = "nested content"
        
        result = tool.run(
            filename="nested.txt",
            content=content,
            directory=str(nested_dir)
        )
        
        assert "successfully" in result
        assert nested_dir.exists()
        assert (nested_dir / "nested.txt").exists()
        assert (nested_dir / "nested.txt").read_text() == content

    def test_utf8_encoding(self, tool, temp_dir):
        content = "Hello, 世界! 🌍"
        
        result = tool.run(
            filename="utf8.txt",
            content=content,
            directory=str(temp_dir),
            encoding="utf-8"
        )
        
        assert "successfully" in result
        output_file = temp_dir / "utf8.txt"
        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == content
