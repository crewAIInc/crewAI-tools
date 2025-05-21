import os
from importlib.metadata import version
from typing import Any, Optional, Type

try:
    from pymongo import MongoClient
    from pymongo.driver_info import DriverInfo

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

import openai
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class MongoDBVectorSearchConfig(BaseModel):
    """Configuration for MongoDB vector search queries."""

    limit: Optional[int] = Field(
        default=4, description="number of documents to return."
    )
    pre_filter: Optional[dict[str, Any]] = Field(
        ..., description="List of MQL match expressions comparing an indexed field"
    )
    post_filter_pipeline: Optional[list[dict]] = Field(
        ...,
        description="Pipeline of MongoDB aggregation stages to filter/process results after $vectorSearch.",
    )
    oversampling_factor: int = Field(
        default=10,
        description="Multiple of limit used when generating number of candidates at each step in the HNSW Vector Search",
    )
    include_embeddings: bool = Field(
        default=False,
        description="Whether to include the embedding vector of each result in metadata.",
    )


class MongoDBToolSchema(MongoDBVectorSearchConfig):
    """Input for MongoDBTool."""

    query: str = Field(
        ...,
        description="The query to search retrieve relevant information from the MongoDB database. Pass only the query, not the question.",
    )


class MongoDBVectorSearchTool(BaseTool):
    """Tool to perfrom a vector search the MongoDB database"""

    name: str = "MongoDBVectorSearchTool"
    description: str = "A tool to perfrom a vector search on a MongoDB database for relevant information on internal documents."

    args_schema: Type[BaseModel] = MongoDBToolSchema
    query_config: Optional[MongoDBVectorSearchConfig] = Field(
        default=None, description="MongoDB Vector Search query configuration"
    )
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="Text OpenAI embedding model to use",
    )
    index_name: str = Field(
        default="vector_index", description=" Name of the Atlas Search index"
    )
    text_key: str = Field(
        default="text",
        description="MongoDB field that will contain the text for each document",
    )
    embedding_key: str = Field(
        default="embedding",
        description="Field that will contain the embedding for each document",
    )
    database_name: str = Field(..., description="The name of the MongoDB database")
    collection_name: str = Field(..., description="The name of the MongoDB collection")
    connection_string: str = Field(
        ...,
        description="The connection string of the MongoDB cluster",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not MONGODB_AVAILABLE:
            import click

            if click.confirm(
                "You are missing the 'pymongo' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "pip", "install", "pymongo"], check=True)

            else:
                raise ImportError(
                    "You are missing the 'pymongo' package. Would you like to install it?"
                )

        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for MongoDBVectorSearchTool and it is mandatory to use the tool."
            )
        self._client = MongoClient(
            self.connection_string,
            driver=DriverInfo(name="CrewAI", version=version("crewai-tools")),
        )
        self._collection = self._client[self.database_name][self.collection_name]
        self._openai_client = openai.Client(api_key=openai_api_key)

    def _run(self, **kwargs) -> list[dict[str, Any]]:
        # Get the inputs.
        query = kwargs["query"]
        limit = kwargs.get("limit", self.query_config.limit)
        oversampling_factor = kwargs.get(
            "oversampling_factor", self.query_config.oversampling_factor
        )
        pre_filter = kwargs.get("pre_filter", self.query_config.pre_filter)
        include_embeddings = kwargs.get(
            "include_embeddings", self.query_config.include_embeddings
        )
        post_filter_pipeline = kwargs.get(
            "post_filter_pipeline", self.query_config.post_filter_pipeline
        )

        # Create the embedding for the query.
        embedding = (
            self._openai_clientclient.embeddings.create(
                input=[query],
                model=self.embedding_model,
            )
            .data[0]
            .embedding
        )

        # Create the vector search pipeline.
        search = {
            "index": self._index_name,
            "path": self._embedding_key,
            "queryVector": embedding,
            "numCandidates": limit * oversampling_factor,
            "limit": limit,
        }
        if pre_filter:
            search["filter"] = pre_filter

        pipeline = [
            {"$vectorSearch": search},
            {"$set": {"score": {"$meta": "vectorSearchScore"}}},
        ]

        # Remove embeddings unless requested.
        if not include_embeddings:
            pipeline.append({"$project": {self._embedding_key: 0}})

        # Post-processing.
        if post_filter_pipeline is not None:
            pipeline.extend(post_filter_pipeline)

        # Execution.
        cursor = self._collection.aggregate(pipeline)  # type: ignore[arg-type]
        docs = []

        # Format.
        for res in cursor:
            if self._text_key not in res:
                continue
            text = res.pop(self._text_key)
            score = res.pop("score")
            docs.append(dict(context=text, metadata=res, id=res["_id"], score=score))
        return docs

    def __del__(self):
        """Cleanup clients on deletion."""
        self._client.close()
        self._openai_client.close()
