import os
from pathlib import Path

from crewai_tools.rag.loaders.base_loader import BaseLoader, LoaderResult


class TextFileLoader(BaseLoader):
    def load(self, source: str | Path, **kwargs) -> LoaderResult:
        if not os.path.exists(source):
            raise FileNotFoundError(f"The following file does not exist: {source}")

        with open(source, "r", encoding="utf-8") as file:
            content = file.read()

        return LoaderResult(content=content, source=str(source))


class TextLoader(BaseLoader):
    def load(self, source: str | Path, **kwargs) -> LoaderResult:
        return LoaderResult(content=source, source="raw")
