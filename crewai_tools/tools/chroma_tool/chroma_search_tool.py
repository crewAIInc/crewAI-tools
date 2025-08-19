import json
from typing import Any, Optional, Type, List, Dict

try:
    import chromadb

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = Any  # type placeholder

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ChromaToolSchema(BaseModel):
    """Input for ChromaTool."""

    query: str = Field(
        ...,
        description="The query to search retrieve relevant information from the Chroma database. Pass only the query, not the question.",
    )
    where: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata filter to apply to the search. Pass as a dictionary.",
    )
    where_document: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional document content filter to apply to the search. Pass as a dictionary with one key $contains, $regex, $not_contains, $not_regex, $and, $or.",
    )


class ChromaSearchTool(BaseTool):
    """Tool to search a Chroma collection"""

    package_dependencies: List[str] = ["chromadb"]
    name: str = "ChromaSearchTool"
    description: str = (
        "A tool to search a Chroma collection for relevant information on internal documents."
    )
    args_schema: Type[BaseModel] = ChromaToolSchema
    collection: Any = Field(
        ...,
        description="Chroma collection to search in.",
    )
    limit: Optional[int] = Field(default=3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not CHROMA_AVAILABLE:
            import click

            if click.confirm(
                "You are missing the 'chromadb' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "pip", "install", "chromadb"], check=True)
            else:
                raise ImportError(
                    "You are missing the 'chromadb' package. Please install it with: uv pip install chromadb"
                )

    def _run(self, query: str, where: Optional[Dict[str, Any]] = None, where_document: Optional[Dict[str, Any]] = None) -> str:
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "You are missing the 'chromadb' package. Please install it with: uv pip install chromadb"
            )

        if not self.collection:
            raise ValueError("Collection is required.")

        search_kwargs = {
            "query_texts": [query],
            "n_results": self.limit,
        }

        if where:
            search_kwargs["where"] = where
        
        if where_document:
            search_kwargs["where_document"] = where_document

        results = self.collection.query(**search_kwargs)

        # Format results for output
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                result = {
                    "document": doc,
                    "metadata": (
                        results["metadatas"][0][i]
                        if results["metadatas"]
                        and results["metadatas"][0]
                        and results["metadatas"][0][i] is not None
                        else {}
                    ),
                    "id": (
                        results["ids"][0][i]
                        if results["ids"] and results["ids"][0]
                        else None
                    ),
                }
                formatted_results.append(result)

        return json.dumps(formatted_results, indent=2)
