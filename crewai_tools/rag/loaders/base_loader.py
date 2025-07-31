from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LoaderResult(BaseModel):
    content: str = Field(description="The text content of the source")
    source: str = Field(description="The source of the content", default="unknown")
    metadata: Dict[str, Any] = Field(description="The metadata of the source", default_factory=dict)


class BaseLoader(ABC):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def load(self, source: str | Path, **kwargs) -> LoaderResult:
        ...
