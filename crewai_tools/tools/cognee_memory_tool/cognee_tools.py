import asyncio
import json
import subprocess
from typing import Optional, Type

try:
    import cognee

    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    cognee = None  # placeholder


from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def ensure_cognee_installed():
    global COGNEE_AVAILABLE, cognee
    if not COGNEE_AVAILABLE:
        try:
            print("Cognee not found. Attempting auto-install...")
            subprocess.run(["uv", "add", "cognee"], check=True)

            import cognee

            COGNEE_AVAILABLE = True
        except Exception as e:
            raise ImportError(
                "Automatic installation of 'cognee' failed. "
                "Please install it manually with: uv add cognee"
            ) from e


class CogneeAddSchema(BaseModel):
    """Schema for adding text to Cognee"""

    text: str = Field(..., description="The text to be added to Cognee.")


class CogneeCognifySchema(BaseModel):
    """Schema for triggering the cognify process."""


class CogneeSearchSchema(BaseModel):
    """Schema for searching Cognee."""

    query: str = Field(..., description="The query text to search in Cognee.")
    query_type: Optional[str] = Field(
        default="INSIGHTS",
        description="Specifies the type of search (e.g. SUMMARIES, INSIGHTS, CHUNKS, COMPLETION, GRAPH_COMPLETION, GRAPH_SUMMARY_COMPLETION.)",
    )


class CogneePruneSchema(BaseModel):
    """Schema for pruning Cognee data."""

    prune_metadata: bool = Field(
        default=True,
        description="Whether to also prune system metadata (True) or just data (False).",
    )


class CogneeAddTool(BaseTool):
    """Adds text to Cognee memory."""

    name: str = "cognee_add"
    description: str = (
        "Adds text to Cognee's knowledge base. "
        "Use this when you want to store new knowledge in Cognee."
    )
    args_schema: Type[BaseModel] = CogneeAddSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ensure_cognee_installed()

    def _run(self, text: str) -> str:
        async def add_text():
            await cognee.add(text)
            return f"Text added to Cognee: {text}"

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(add_text())


class CogneeCognifyTool(BaseTool):
    """Runs the cognify process to build the knowledge graph."""

    name: str = "cognee_cognify"
    description: str = (
        "Runs the cognify process on all text previously added to Cognee, "
        "creating a knowledge graph."
    )
    args_schema: Type[BaseModel] = CogneeCognifySchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ensure_cognee_installed()

    def _run(self, **kwargs) -> str:
        async def cognify():
            await cognee.cognify()
            return "Cognee cognify process complete."

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(cognify())


class CogneeSearchTool(BaseTool):
    """Searches Cognee knowledge graph based on the query."""

    name: str = "cognee_search"
    description: str = (
        "Searches the Cognee knowledge graph based on the query. "
        "Use this to retrieve data from previously added texts."
    )
    args_schema: Type[BaseModel] = CogneeSearchSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ensure_cognee_installed()

    def _run(self, query: str, query_type: str = "INSIGHTS") -> str:
        async def do_search():
            from cognee.modules.search.types import SearchType

            stype = getattr(SearchType, query_type.upper(), SearchType.INSIGHTS)
            results = await cognee.search(query_text=query, query_type=stype)

            return json.dumps([str(r) for r in results], indent=2)

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(do_search())


class CogneePruneTool(BaseTool):
    """Clears or resets Cognee data and optionally system metadata."""

    name: str = "cognee_prune"
    description: str = (
        "Completely resets or prunes Cognee data. "
        "Use this to clear existing knowledge and start fresh."
    )
    args_schema: Type[BaseModel] = CogneePruneSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ensure_cognee_installed()

    def _run(self, prune_metadata: bool = True) -> str:
        async def do_prune():
            from cognee import prune

            await prune.prune_data()
            if prune_metadata:
                await prune.prune_system(metadata=True)
            return (
                "Cognee data pruned. Also pruned system metadata."
                if prune_metadata
                else "Cognee data pruned, system metadata retained."
            )

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(do_prune())
