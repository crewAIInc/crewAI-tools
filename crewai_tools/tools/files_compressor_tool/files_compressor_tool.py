
import os
import zipfile
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class FileCompressorToolInput(BaseModel):
    """Input schema for FileCompressorTool."""
    input_path: str = Field(..., description="Path to the file or directory to compress.")
    output_zip: Optional[str] = Field(None, description="Optional output zip filename. Defaults to 'compressed.zip' in the input directory.")
    overwrite: bool = Field(False, description="Whether to overwrite the zip if it already exists.")


class FileCompressorTool(BaseTool):
    name: str = "File Compressor Tool"
    description: str = (
        "Compresses a file or directory into a .zip archive. Useful for archiving logs, documents, or backups."
    )
    args_schema: Type[BaseModel] = FileCompressorToolInput

    def _run(self, input_path: str, output_zip: Optional[str] = None, overwrite: bool = False) -> str:
        try:
            if not os.path.exists(input_path):
                return f"Input path '{input_path}' does not exist."

            # Default zip file name if not provided
            if not output_zip:
                base_name = os.path.basename(input_path.rstrip("/\\"))
                output_zip = os.path.join(os.getcwd(), f"{base_name}.zip")

            # Ensure output directory exists
            output_dir = os.path.dirname(output_zip)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if os.path.exists(output_zip) and not overwrite:
                return f"Output zip '{output_zip}' already exists and overwrite is set to False."

            # Compression logic
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(input_path):
                    zipf.write(input_path, os.path.basename(input_path))
                else:
                    for root, _, files in os.walk(input_path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, start=input_path)
                            zipf.write(full_path, arcname)

            return f"Successfully compressed '{input_path}' into '{output_zip}'"
        except Exception as e:
            return f"An error occurred during compression: {str(e)}"

