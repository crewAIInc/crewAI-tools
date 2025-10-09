import json
import os
from typing import Any, Optional, Type, List

try:
    import weaviate
    from weaviate.classes.init import Auth
    from weaviate.agents.query import QueryAgent
    from weaviate.agents.classes import ChatMessage

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = Any
    Auth = Any
    QueryAgent = Any
    ChatMessage = Any

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WeaviateQueryAgentAskToolSchema(BaseModel):
    query: str = Field(
        ...,
        description="The natural language question to ask the Weaviate Query Agent.",
    )


class WeaviateQueryAgentAskTool(BaseTool):
    name: str = "WeaviateQueryAgentAskTool"
    description: str = (
        "A tool to ask natural language questions to the Weaviate Query Agent. "
        "The agent will process the question, search Weaviate, and return a generated answer."
    )
    args_schema: Type[BaseModel] = WeaviateQueryAgentAskToolSchema
    collection_names: List[str] = Field(
        ...,
        description="List of collection names to query",
    )
    weaviate_cluster_url: str = Field(
        ...,
        description="The URL of the Weaviate cluster",
    )
    weaviate_api_key: str = Field(
        ...,
        description="The API key for the Weaviate cluster",
    )
    package_dependencies: List[str] = ["weaviate-client", "weaviate-agents"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not WEAVIATE_AVAILABLE:
            import click

            if click.confirm(
                "You are missing the 'weaviate-client' and 'weaviate-agents' packages. Would you like to install them?"
            ):
                import subprocess

                subprocess.run(["uv", "pip", "install", "weaviate-client", "weaviate-agents"], check=True)
            else:
                raise ImportError(
                    "You are missing the 'weaviate-client' and 'weaviate-agents' packages. Please install them to use this tool."
                )

    def _run(self, query: str) -> str:
        if not WEAVIATE_AVAILABLE:
            raise ImportError(
                "You are missing the 'weaviate-client' and 'weaviate-agents' packages. Please install them to use this tool."
            )

        if not self.weaviate_cluster_url or not self.weaviate_api_key:
            raise ValueError("WEAVIATE_URL or WEAVIATE_API_KEY is not set")

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.weaviate_cluster_url,
            auth_credentials=Auth.api_key(self.weaviate_api_key),
        )

        try:
            qa = QueryAgent(
                client=client,
                collections=self.collection_names
            )

            response = qa.ask(query)

            return response.final_answer

        finally:
            client.close()


class WeaviateQueryAgentSearchModeToolSchema(BaseModel):
    query: str = Field(
        ...,
        description="The natural language search query for the Weaviate Query Agent.",
    )


class WeaviateQueryAgentSearchModeTool(BaseTool):
    name: str = "WeaviateQueryAgentSearchModeTool"
    description: str = (
        "A tool to search Weaviate using natural language queries via the Query Agent. "
        "Returns relevant objects without generating an answer (retrieval only)."
    )
    args_schema: Type[BaseModel] = WeaviateQueryAgentSearchModeToolSchema
    collection_names: List[str] = Field(
        ...,
        description="List of collection names to search",
    )
    limit: Optional[int] = Field(default=10, description="Maximum number of results to retrieve")
    weaviate_cluster_url: str = Field(
        ...,
        description="The URL of the Weaviate cluster",
    )
    weaviate_api_key: str = Field(
        ...,
        description="The API key for the Weaviate cluster",
    )
    package_dependencies: List[str] = ["weaviate-client", "weaviate-agents"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not WEAVIATE_AVAILABLE:
            import click

            if click.confirm(
                "You are missing the 'weaviate-client' and 'weaviate-agents' packages. Would you like to install them?"
            ):
                import subprocess

                subprocess.run(["uv", "pip", "install", "weaviate-client", "weaviate-agents"], check=True)
            else:
                raise ImportError(
                    "You are missing the 'weaviate-client' and 'weaviate-agents' packages. Please install them to use this tool."
                )

    def _run(self, query: str) -> str:
        if not WEAVIATE_AVAILABLE:
            raise ImportError(
                "You are missing the 'weaviate-client' and 'weaviate-agents' packages. Please install them to use this tool."
            )

        if not self.weaviate_cluster_url or not self.weaviate_api_key:
            raise ValueError("WEAVIATE_URL or WEAVIATE_API_KEY is not set")

        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.weaviate_cluster_url,
            auth_credentials=Auth.api_key(self.weaviate_api_key),
        )

        try:
            qa = QueryAgent(
                client=client,
                collections=self.collection_names
            )

            search_response = qa.search(query, limit=self.limit)

            results = []
            for obj in search_response.search_results.objects:
                results.append({
                    "properties": obj.properties,
                    "uuid": str(obj.uuid) if hasattr(obj, 'uuid') else None
                })

            return json.dumps(results, indent=2)

        finally:
            client.close()