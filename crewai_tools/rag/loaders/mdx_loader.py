import os
import re
from pathlib import Path
from urllib.parse import urlparse
from typing import Union

from crewai_tools.rag.loaders.base_loader import BaseLoader, LoaderResult


class MDXLoader(BaseLoader):
    def load(self, source: Union[str, Path], **kwargs) -> LoaderResult:
        source_str = str(source)

        if self._is_url(source):
            content = self._load_from_url(source_str, kwargs)
        elif os.path.exists(source_str):
            content = self._load_from_file(source_str)
        else:
            content = str(source)
            source_str = kwargs.get("source", "mdx_string")

        return self._parse_mdx(content, source_str)

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
            "Accept": "text/markdown, text/x-markdown, text/plain",
            "User-Agent": "Mozilla/5.0 (compatible; crewai-tools MDXLoader)"
        })

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise ValueError(f"Error fetching MDX from URL {url}: {str(e)}")

    def _load_from_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    def _parse_mdx(self, content: str, source_str: str) -> LoaderResult:
        cleaned_content = content

        # Remove import statements
        cleaned_content = re.sub(r'^import\s+.*?\n', '', cleaned_content, flags=re.MULTILINE)

        # Remove export statements
        cleaned_content = re.sub(r'^export\s+.*?\n', '', cleaned_content, flags=re.MULTILINE)

        # Remove JSX tags (simple approach)
        cleaned_content = re.sub(r'<[^>]+>', '', cleaned_content)

        # Clean up extra whitespace
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
        cleaned_content = cleaned_content.strip()

        metadata = {"format": "mdx"}
        return LoaderResult(content=cleaned_content, source=source_str, metadata=metadata)
