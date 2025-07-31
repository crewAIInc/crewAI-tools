import os
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from typing import Union

from crewai_tools.rag.loaders.base_loader import BaseLoader, LoaderResult


class XMLLoader(BaseLoader):
    def load(self, source: Union[str, Path], **kwargs) -> LoaderResult:
        source_str = str(source)

        if self._is_url(source):
            content = self._load_from_url(source_str, kwargs)
        elif os.path.exists(source_str):
            content = self._load_from_file(source_str)
        else:
            content = str(source)
            source_str = kwargs.get("source", "xml_string")

        return self._parse_xml(content, source_str)

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
            "Accept": "application/xml, text/xml, text/plain",
            "User-Agent": "Mozilla/5.0 (compatible; crewai-tools XMLLoader)"
        })

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise ValueError(f"Error fetching XML from URL {url}: {str(e)}")

    def _load_from_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    def _parse_xml(self, content: str, source_str: str) -> LoaderResult:
        try:
            if content.strip().startswith('<'):
                root = ET.fromstring(content)
            else:
                root = ET.parse(source_str).getroot()

            text_parts = []
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text_parts.append(elem.text.strip())

            text = "\n".join(text_parts)
            metadata = {"format": "xml", "root_tag": root.tag}
        except ET.ParseError as e:
            text = content
            metadata = {"format": "xml", "parse_error": str(e)}

        return LoaderResult(content=text, source=source_str, metadata=metadata)
