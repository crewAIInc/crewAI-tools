import os
import json
from urllib.parse import urlparse
from pathlib import Path
from typing import Union

from crewai_tools.rag.loaders.base_loader import BaseLoader, LoaderResult


class JSONLoader(BaseLoader):
    def load(self, source: Union[str, Path], **kwargs) -> LoaderResult:
        source_str = str(source)

        if self._is_url(source):
            content = self._load_from_url(source_str, kwargs)
        elif os.path.exists(source_str):
            content = self._load_from_file(source_str)
        else:
            content = str(source)
            source_str = kwargs.get("source", "json_string")

        return self._parse_json(content, source_str)

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
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; crewai-tools JSONLoader)"
        })

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text if not self._is_json_response(response) else json.dumps(response.json(), indent=2)
        except requests.RequestException as e:
            raise ValueError(f"Error fetching JSON from URL {url}: {str(e)}")

    def _is_json_response(self, response) -> bool:
        try:
            response.json()
            return True
        except ValueError:
            return False

    def _load_from_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    def _parse_json(self, content: str, source_str: str) -> LoaderResult:
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                text = "\n".join(f"{k}: {json.dumps(v, indent=0)}" for k, v in data.items())
            elif isinstance(data, list):
                text = "\n".join(json.dumps(item, indent=0) for item in data)
            else:
                text = json.dumps(data, indent=0)

            metadata = {
                "format": "json",
                "type": type(data).__name__,
                "size": len(data) if isinstance(data, (list, dict)) else 1
            }
        except json.JSONDecodeError as e:
            text = content
            metadata = {"format": "json", "parse_error": str(e)}

        return LoaderResult(content=text, source=source_str, metadata=metadata)
