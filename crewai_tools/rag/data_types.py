from enum import Enum
from pathlib import Path
from urllib.parse import urlparse
import os
from crewai_tools.rag.chunkers.base_chunker import BaseChunker
from crewai_tools.rag.loaders.base_loader import BaseLoader

class DataType(str, Enum):
    PDF_FILE = "pdf_file"
    TEXT_FILE = "text_file"
    CSV = "csv"
    JSON = "json"
    TXT = "txt"
    XML = "xml"
    DOCX = "docx"
    MDX = "mdx"

    # Database types
    MYSQL = "mysql"
    POSTGRES = "postgres"

    # Repository types
    GITHUB = "github"
    DIRECTORY = "directory"

    # Web types
    WEBSITE = "website"
    DOCS_SITE = "docs_site"

    # Raw types
    TEXT = "text"
    RAW = "raw"

    def get_chunker(self) -> BaseChunker:
        from importlib import import_module

        chunkers = {
            DataType.PDF_FILE: "PdfChunker",
        }

        module_path = f"crewai_tools.rag.chunkers.{chunkers.get(self, 'DefaultChunker')}"

        module_path, class_name = module_path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, class_name)()

    def get_loader(self) -> BaseLoader:
        from importlib import import_module

        loaders = {
            DataType.TEXT_FILE: ("loaders", "TextFileLoader"),
            DataType.TEXT: ("loaders", "TextLoader"),
            DataType.XML: ("xml_loader", "XMLLoader"),
            DataType.WEBSITE: ("webpage_loader", "WebPageLoader"),
            DataType.MDX: ("mdx_loader", "MDXLoader"),
            DataType.JSON: ("json_loader", "JSONLoader"),
            DataType.DOCX: ("docx_loader", "DOCXLoader"),
            DataType.CSV: ("csv_loader", "CSVLoader"),
            DataType.DIRECTORY: ("directory_loader", "DirectoryLoader"),
        }

        module_name, class_name = loaders.get(self, ("loaders", "TextLoader"))
        module_path = f"crewai_tools.rag.loaders.{module_name}"
        try:
            module = import_module(module_path)
            return getattr(module, class_name)()
        except Exception as e:
            raise ValueError(f"Error loading loader for {self}: {e}")

class DataTypes:
    @staticmethod
    def from_content(content: str | Path | None = None) -> DataType:
        if content is None:
            return DataType.TEXT

        if isinstance(content, Path):
            content = str(content)

        is_url = False
        if isinstance(content, str):
            try:
                url = urlparse(content)
                is_url = (url.scheme and url.netloc) or url.scheme == "file"
            except Exception:
                pass

        def get_file_type(path: str) -> DataType | None:
            mapping = {
                ".pdf": DataType.PDF_FILE,
                ".csv": DataType.CSV,
                ".mdx": DataType.MDX,
                ".md": DataType.MDX,
                ".docx": DataType.DOCX,
                ".json": DataType.JSON,
                ".xml": DataType.XML,
                ".txt": DataType.TEXT_FILE,
            }
            for ext, dtype in mapping.items():
                if path.endswith(ext):
                    return dtype
            return None

        if is_url:
            dtype = get_file_type(url.path)
            if dtype:
                return dtype

            if "docs" in url.netloc or ("docs" in url.path and url.scheme != "file"):
                return DataType.DOCS_SITE
            if "github.com" in url.netloc:
                return DataType.GITHUB

            return DataType.WEBSITE

        if os.path.isfile(content):
            dtype = get_file_type(content)
            if dtype:
                return dtype

            if os.path.exists(content):
                return DataType.TEXT_FILE
        elif os.path.isdir(content):
            return DataType.DIRECTORY

        return DataType.TEXT
