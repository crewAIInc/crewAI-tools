import os
from distutils.util import strtobool
from pathlib import Path
from typing import Any, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, validator


class FileWriterToolInput(BaseModel):
    filename: str
    directory: Optional[str] = "./"
    overwrite: str = "False"
    content: str
    max_size: Optional[int] = Field(default=10_000_000, description="Maximum file size in bytes (default 10MB)")
    encoding: str = Field(default="utf-8", description="File encoding (default UTF-8)")

    @validator("filename")
    def validate_filename(cls, v: str) -> str:
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid filename: must not contain '..' or start with '/'")
        return v

    @validator("directory")
    def validate_directory(cls, v: Optional[str]) -> Optional[str]:
        if v and (".." in v or v.startswith("/")):
            raise ValueError("Invalid directory: must not contain '..' or start with '/'")
        return v


class FileWriterTool(BaseTool):
    name: str = "File Writer Tool"
    description: str = "A secure, cross-platform tool to write content to files with size limits and encoding support."
    args_schema: Type[BaseModel] = FileWriterToolInput

    def _validate_path(self, path: Path) -> None:
        if not os.access(path.parent, os.W_OK):
            raise ValueError(f"No write permission for directory: {path.parent}")

    def _check_size(self, content: str, encoding: str, max_size: int) -> None:
        if len(content.encode(encoding)) > max_size:
            raise ValueError(f"Content exceeds maximum size of {max_size} bytes")

    def _write_with_progress(self, file, content: str, encoding: str, chunk_size: int = 8192) -> None:
        total = len(content)
        written = 0
        while written < total:
            chunk = content[written:written + chunk_size]
            file.write(chunk)
            written += len(chunk)

    def _run(self, **kwargs: Any) -> str:
        try:
            directory = Path(kwargs.get("directory") or "")
            filepath = directory / kwargs["filename"]

            # Create directory if needed
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)

            # Validate path and permissions
            self._validate_path(filepath)

            # Get and validate parameters
            content = kwargs["content"]
            encoding = kwargs.get("encoding", "utf-8")
            max_size = kwargs.get("max_size", 10_000_000)
            overwrite = bool(strtobool(kwargs["overwrite"]))

            # Check content size
            self._check_size(content, encoding, max_size)

            # Check if file exists
            if filepath.exists() and not overwrite:
                return f"File {filepath} already exists and overwrite option was not passed."

            # Write content with progress tracking
            mode = "w" if overwrite else "x"
            with filepath.open(mode=mode, encoding=encoding) as file:
                self._write_with_progress(file, content, encoding)

            return f"Content successfully written to {filepath}"
        except FileExistsError:
            return (
                f"File {filepath} already exists and overwrite option was not passed."
            )
        except KeyError as e:
            return f"An error occurred while accessing key: {str(e)}"
        except Exception as e:
            return f"An error occurred while writing to the file: {str(e)}"
