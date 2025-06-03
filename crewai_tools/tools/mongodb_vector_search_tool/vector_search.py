from importlib.metadata import version
from typing import Any, Dict, Iterable, List, Optional, Type

try:
    # Import for testing
    from langchain_mongodb.index import create_vector_search_index  # noqa: F403

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class MongoDBVectorSearchConfig(BaseModel):
    """Configuration for MongoDB vector search queries."""

    limit: Optional[int] = Field(
        default=4, description="number of documents to return."
    )
    pre_filter: Optional[dict[str, Any]] = Field(
        default=None,
        description="List of MQL match expressions comparing an indexed field",
    )
    post_filter_pipeline: Optional[list[dict]] = Field(
        default=None,
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
    vector_index_name: str = Field(
        default="vector_index", description="Name of the Atlas Search vector index"
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
                "You are missing the 'mongodb' crewai tool. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(
                    ["uv", "pip", "install", "crewai-tools[mongodb]"], check=True
                )

            else:
                raise ImportError("You are missing the 'mongodb' crewai tool.")

        from langchain_mongodb import MongoDBAtlasVectorSearch
        from langchain_openai import OpenAIEmbeddings
        from pymongo import MongoClient
        from pymongo.driver_info import DriverInfo

        client = MongoClient(
            self.connection_string,
            driver=DriverInfo(name="CrewAI", version=version("crewai-tools")),
        )
        self._coll = client[self.database_name][self.collection_name]
        self._embeddings = OpenAIEmbeddings(model=self.embedding_model)
        self._client = MongoDBAtlasVectorSearch(
            collection=self._coll,
            embedding=self._embeddings,
            index_name=self.vector_index_name,
            text_key=self.text_key,
            embedding_key=self.embedding_key,
        )

    def create_vector_search_index(
        self,
        *,
        dimensions: int,
        relevance_score_fn: str = "cosine",
        auto_index_timeout: int = 15,
    ) -> None:
        """Convenience function to create a vector search index.

        Args:
            dimensions: Number of dimensions in embedding.  If the value is set and
                the index does not exist, an index will be created.
            relevance_score_fn: The similarity score used for the index
                Currently supported: 'euclidean', 'cosine', and 'dotProduct'
            auto_index_timeout: Timeout in seconds to wait for an auto-created index
               to be ready.
        """

        create_vector_search_index(
            collection=self._coll,
            index_name=self.vector_index_name,
            dimensions=dimensions,
            path=self.embedding_key,
            similarity=relevance_score_fn,
            wait_until_complete=auto_index_timeout,
        )

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100,
        **kwargs: Any,
    ) -> List[str]:
        """Add texts, create embeddings, and add to the Collection and index.

        Important notes on ids:
            - If _id or id is a key in the metadatas dicts, one must
                pop them and provide as separate list.
            - They must be unique.
            - If they are not provided, the VectorStore will create unique ones,
                stored as bson.ObjectIds internally, and strings in Langchain.
                These will appear in Document.metadata with key, '_id'.

        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            ids: Optional list of unique ids that will be used as index in VectorStore.
                See note on ids.
            batch_size: Number of documents to insert at a time.
                Tuning this may help with performance and sidestep MongoDB limits.

        Returns:
            List of ids added to the vectorstore.
        """
        return self._client.add_texts(texts, metadatas, ids, batch_size, **kwargs)

    def _run(self, **kwargs) -> list[dict[str, Any]]:
        # Get the inputs.
        query_config = self.query_config or MongoDBVectorSearchConfig()
        query = kwargs["query"]
        limit = kwargs.get("limit", query_config.limit)
        oversampling_factor = kwargs.get(
            "oversampling_factor", query_config.oversampling_factor
        )
        pre_filter = kwargs.get("pre_filter", query_config.pre_filter)
        include_embeddings = kwargs.get(
            "include_embeddings", query_config.include_embeddings
        )
        post_filter_pipeline = kwargs.get(
            "post_filter_pipeline", query_config.post_filter_pipeline
        )

        docs = self._client.similarity_search(
            query,
            k=limit,
            pre_filter=pre_filter,
            post_filter_pipeline=post_filter_pipeline,
            oversampling_factor=oversampling_factor,
            include_scores=True,
            include_embeddings=include_embeddings,
        )

        res = []
        for doc in docs:
            score = doc.metadata.pop("score")
            res.append(
                dict(
                    context=doc.page_content,
                    id=doc.id,
                    metadata=doc.metadata,
                    score=score,
                )
            )

        return res

    def __del__(self):
        """Cleanup clients on deletion."""
        self._client.close()
