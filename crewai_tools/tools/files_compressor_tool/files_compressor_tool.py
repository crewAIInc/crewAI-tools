import os
import zipfile
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class FileCompressorToolInput(BaseModel):
    """Input schema for FileCompressorTool."""
    input_path: str = Field(..., description="Path to the file or directory to compress.")
    output_path: Optional[str] = Field(default=None, description="Optional output archive filename.")
    overwrite: bool = Field(default=False, description="Whether to overwrite the archive if it already exists.")
    format: str = Field(default="zip", description="Compression format (currently only 'zip' is supported).")


class FileCompressorTool(BaseTool):
    name: str = "File Compressor Tool"
    description: str = (
        "Compresses a file or directory into an archive (.zip currently supported). "
        "Useful for archiving logs, documents, or backups."
    )
    args_schema: Type[BaseModel] = FileCompressorToolInput

    def _run(self, input_path: str, output_path: Optional[str] = None, overwrite: bool = False, format: str = "zip") -> str:
        try:
            if not os.path.exists(input_path):
                return f"Input path '{input_path}' does not exist."

            if not output_path:
                output_path = self._generate_output_path(input_path, format)

            if not self._prepare_output(output_path, overwrite):
                return f"Output '{output_path}' already exists and overwrite is set to False."

            if format == "zip":
                self._compress_zip(input_path, output_path)
            else:
                return f"Compression format '{format}' is not supported yet."

            return f"Successfully compressed '{input_path}' into '{output_path}'"
        except Exception as e:
            return f"An error occurred during compression: {str(e)}"

    def _generate_output_path(self, input_path: str, format: str) -> str:
        """Generates output path based on input path and format."""
        if os.path.isfile(input_path):
            base_name = os.path.splitext(os.path.basename(input_path))[0]  # Remove extension
        else:
            base_name = os.path.basename(os.path.normpath(input_path))  # Directory name
        return os.path.join(os.getcwd(), f"{base_name}.{format}")

    def _prepare_output(self, output_path: str, overwrite: bool) -> bool:
        """Ensures output path is ready for writing."""
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if os.path.exists(output_path) and not overwrite:
            return False
        return True

    def _compress_zip(self, input_path: str, output_path: str):
        """Compresses input into a zip archive."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(input_path):
                zipf.write(input_path, os.path.basename(input_path))
            else:
                for root, _, files in os.walk(input_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, start=input_path)
                        zipf.write(full_path, arcname)


