from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field, model_validator

from crewai.tools import BaseTool

if TYPE_CHECKING:
    from crewai.rag.config.types import RagConfigType


class Adapter(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def query(self, question: str) -> str:
        """Query the knowledge base with a question and return the answer."""

    @abstractmethod
    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Add content to the knowledge base."""


class RagTool(BaseTool):
    class _AdapterPlaceholder(Adapter):
        def query(self, question: str) -> str:
            raise NotImplementedError

        def add(self, *args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

    name: str = "Knowledge base"
    description: str = "A knowledge base that can be used to answer questions."
    summarize: bool = False
    adapter: Adapter = Field(default_factory=_AdapterPlaceholder)
    config: Any | None = None

    @model_validator(mode="after")
    def _set_default_adapter(self):
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from crewai_tools.adapters.crewai_rag_adapter import CrewAIRagAdapter
            
            self.adapter = CrewAIRagAdapter(
                collection_name="rag_tool_collection",
                summarize=self.summarize,
                config=self.config
            )

        return self

    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.adapter.add(*args, **kwargs)

    def _run(
        self,
        query: str,
    ) -> str:
        return f"Relevant Content:\n{self.adapter.query(query)}"
