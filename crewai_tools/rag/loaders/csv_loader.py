import csv
import os
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse
from typing import Union

from crewai_tools.rag.loaders.base_loader import BaseLoader, LoaderResult


class CSVLoader(BaseLoader):
    def load(self, source: Union[str, Path], **kwargs) -> LoaderResult:
        source_str = str(source)

        if self._is_url(source):
            content = self._load_from_url(source_str, kwargs)
        elif os.path.exists(source_str):
            content = self._load_from_file(source_str)
        else:
            content = str(source)
            source_str = kwargs.get("source", "csv_string")

        return self._parse_csv(content, source_str)

    def _is_url(self, source: Union[str, Path]) -> bool:
        if not isinstance(source, str):
            return False
        try:
            parsed_url = urlparse(source)
            return bool(parsed_url.scheme and parsed_url.netloc)
        except Exception:
            return False

    def _load_from_url(self, url: str, kwargs: dict) -> str:
        import requests

        headers = kwargs.get("headers", {
            "Accept": "text/csv, application/csv, text/plain",
            "User-Agent": "Mozilla/5.0 (compatible; crewai-tools CSVLoader)"
        })

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise ValueError(f"Error fetching CSV from URL {url}: {str(e)}")

    def _load_from_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    def _parse_csv(self, content: str, source_str: str) -> LoaderResult:
        try:
            csv_reader = csv.DictReader(StringIO(content))

            text_parts = []
            headers = csv_reader.fieldnames

            if headers:
                text_parts.append("Headers: " + " | ".join(headers))
                text_parts.append("-" * 50)

                for row_num, row in enumerate(csv_reader, 1):
                    row_text = " | ".join([f"{k}: {v}" for k, v in row.items() if v])
                    text_parts.append(f"Row {row_num}: {row_text}")

            text = "\n".join(text_parts)

            metadata = {
                "format": "csv",
                "columns": headers,
                "rows": len(text_parts) - 2 if headers else 0
            }

        except Exception as e:
            text = content
            metadata = {"format": "csv", "parse_error": str(e)}

        return LoaderResult(content=text, source=source_str, metadata=metadata)
