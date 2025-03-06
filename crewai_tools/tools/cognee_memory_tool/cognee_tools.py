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
            # Install Cognee via 'uv add cognee'
            subprocess.run(["uv", "add", "cognee"], check=True)

            # Now re-import Cognee to confirm install
            import cognee

            COGNEE_AVAILABLE = True
        except Exception as e:
            # If auto-install fails, raise an ImportError
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
        description="Specifies the type of search (e.g. INSIGHTS, EXACT).",
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
        # Because Cognee uses async, we need to run it in an asyncio event loop
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
    """Searches Cognee knowledge graph for insights."""

    name: str = "cognee_search"
    description: str = (
        "Searches the Cognee knowledge graph for insights. "
        "Use this to retrieve data from previously added texts."
    )
    args_schema: Type[BaseModel] = CogneeSearchSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ensure_cognee_installed()

    def _run(self, query: str, query_type: str = "INSIGHTS") -> str:
        async def do_search():
            from cognee.modules.search.types import SearchType

            # Convert string to SearchType if possible
            stype = getattr(SearchType, query_type.upper(), SearchType.INSIGHTS)
            results = await cognee.search(query_text=query, query_type=stype)
            # Return as a JSON string
            return json.dumps([str(r) for r in results], indent=2)

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(do_search())
