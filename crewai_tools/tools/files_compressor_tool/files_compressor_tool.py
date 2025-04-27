import os
import zipfile
import tarfile
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class FileCompressorToolInput(BaseModel):
    """Input schema for FileCompressorTool."""
    input_path: str = Field(..., description="Path to the file or directory to compress.")
    output_path: Optional[str] = Field(default=None, description="Optional output archive filename.")
    overwrite: bool = Field(default=False, description="Whether to overwrite the archive if it already exists.")
    format: str = Field(default="zip", description="Compression format ('zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz').")


class FileCompressorTool(BaseTool):
    name: str = "File Compressor Tool"
    description: str = (
        "Compresses a file or directory into an archive (.zip currently supported). "
        "Useful for archiving logs, documents, or backups."
    )
    args_schema: Type[BaseModel] = FileCompressorToolInput

    def _run(self, input_path: str, output_path: Optional[str] = None, overwrite: bool = False, format: str = "zip") -> str:
            
            if not os.path.exists(input_path):
                return f"Input path '{input_path}' does not exist."
            
            if not output_path:
                output_path = self._generate_output_path(input_path, format)

            # Validate file extension based on format
            if format == "zip" and not output_path.endswith(".zip"):
                return f"Error: If 'zip' format is chosen, output file must have a '.zip' extension."
            elif format == "tar" and not output_path.endswith(".tar"):
                return f"Error: If 'tar' format is chosen, output file must have a '.tar' extension."
            elif format == "tar.gz" and not output_path.endswith(".tar.gz"):
                return f"Error: If 'tar.gz' format is chosen, output file must have a '.tar.gz' extension."
            elif format == "tar.bz2" and not output_path.endswith(".tar.bz2"):
                return f"Error: If 'tar.bz2' format is chosen, output file must have a '.tar.bz2' extension."
            elif format == "tar.xz" and not output_path.endswith(".tar.xz"):
                return f"Error: If 'tar.xz' format is chosen, output file must have a '.tar.xz' extension."
            
            if format not in ("zip", "tar", "tar.gz", "tar.bz2", "tar.xz"):
                return f"Compression format '{format}' is not supported. Allowed formats: 'zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz'."

            if not self._prepare_output(output_path, overwrite):
                return f"Output '{output_path}' already exists and overwrite is set to False."

            try:
                if format == "zip":
                    self._compress_zip(input_path, output_path)
                elif format == "tar":
                    self._compress_tar(input_path, output_path, "tar")
                elif format == "tar.gz":
                    self._compress_tar(input_path, output_path, "tar.gz")
                elif format == "tar.bz2":
                    self._compress_tar(input_path, output_path, "tar.bz2")
                elif format == "tar.xz":
                    self._compress_tar(input_path, output_path, "tar.xz")
                
                return f"Successfully compressed '{input_path}' into '{output_path}'"
            except FileNotFoundError:
                return f"Error: File not found at path: {input_path}"
            except PermissionError:
                return f"Error: Permission denied when accessing '{input_path}' or writing '{output_path}'"
            except Exception as e:
                return f"An unexpected error occurred during compression: {str(e)}"

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


    def _compress_tar(self, input_path: str, output_path: str, format: str):
        """Compresses input into a tar archive with the given format."""
        mode = None
        if format == "tar":
            mode = 'w'
        elif format == "tar.gz":
            mode = 'w:gz'
        elif format == "tar.bz2":
            mode = 'w:bz2'
        elif format == "tar.xz":
            mode = 'w:xz'
        else:
            raise ValueError(f"Unsupported tar format: {format}")

        with tarfile.open(output_path, mode) as tarf:
            if os.path.isfile(input_path):
                tarf.add(input_path, arcname=os.path.basename(input_path))
            else:
                tarf.add(input_path, arcname=os.path.basename(input_path))
                




