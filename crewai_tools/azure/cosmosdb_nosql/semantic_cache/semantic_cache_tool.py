import json
import os
import uuid
from datetime import datetime, timezone
from logging import getLogger
from typing import Any, ClassVar, Dict, List, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

try:
    from azure.cosmos import ContainerProxy, CosmosClient, DatabaseProxy
    from azure.core.credentials import TokenCredential
    from openai import AzureOpenAI, Client

    COSMOSDB_AVAILABLE = True
except ImportError:
    COSMOSDB_AVAILABLE = False
    ContainerProxy = Any
    CosmosClient = Any
    DatabaseProxy = Any
    TokenCredential = Any
    AzureOpenAI = Any
    Client = Any

logger = getLogger(__name__)


class AzureCosmosDBSemanticCacheConfig(BaseModel):
    """Configuration for Azure CosmosDB semantic cache operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Cosmos DB Configuration
    cosmos_host: str = Field(..., description="The connection string of the CosmosDB")
    key: Optional[str] = Field(None, description="The Azure Key for the cosmos db")
    token_credential: Optional[TokenCredential] = Field(None, description="The Azure Token Credential")
    database_name: str = Field("memory_database", description="The name of the CosmosDB database")
    container_name: str = Field("memory_container", description="The name of the CosmosDB container")
    cosmos_container_properties: Dict[str, Any] = Field(
        default_factory=lambda: {"partition_key": {"paths": ["/agent_id"], "kind": "Hash"}},
        description="Container properties including partition key configuration"
    )
    cosmos_database_properties: Dict[str, Any] = Field(default_factory=dict, description="Database properties")
    create_container: bool = Field(True, description="Should create the container if it doesn't exist")
    vector_embedding_policy: Optional[Dict[str, Any]] = Field(default=None, description="The policy for the vector embedding.")
    indexing_policy: Dict[str, Any] = Field(..., description="The policy for the indexing.")
    full_text_policy: Optional[Dict[str, Any]] = Field(default=None, description="The policy for the full text embedding.")
    dimensions: int = Field(default=1536, description="Number of dimensions in the embedding vector")
    table_alias: str = Field(default="c", description="The alias of the CosmosDB NoSql table.")

    # Embedding Configuration
    embedding_model: str = Field("text-embedding-3-large", description="Text embedding model to use")
    embedding_dimensions: int = Field(1536, description="Number of dimensions in the embedding vector")
    azure_openai_endpoint: Optional[str] = Field(None, description="Azure OpenAI endpoint URL")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")

    # Cache Behavior
    similarity_threshold: float = Field(0.85, description="Default similarity threshold for cache hits")
    default_ttl: Optional[int] = Field(86400, description="Default time-to-live in seconds (24 hours)")
    enable_hybrid_search: bool = Field(True, description="Enable hybrid search combining vector and text search")


class AzureCosmosDBSemanticCacheToolSchema(BaseModel):
    """Input schema for AzureCosmosDBSemanticCacheTool."""

    operation: str = Field(
        ...,
        description="Operation: 'search', 'update', 'clear'"
    )


class AzureCosmosDBSemanticCacheTool(BaseTool):
    """Tool for semantic caching of LLM responses using Azure CosmosDB NoSQL."""

    USER_AGENT: ClassVar[str] = "CrewAI-CosmosDB-SemanticCache-Tool-Python"

    name: str = "AzureCosmosDBSemanticCacheTool"
    description: str = "A tool for intelligent caching of LLM responses using semantic similarity search in Azure CosmosDB."
    args_schema: Type[BaseModel] = AzureCosmosDBSemanticCacheToolSchema

    config: AzureCosmosDBSemanticCacheConfig = Field(..., description="Configuration for the semantic cache tool")
    package_dependencies: List[str] = ["azure-cosmos", "azure-core", "openai"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._database = None
        self._container = None
        self._openai_client = None

        if not COSMOSDB_AVAILABLE:
            import click
            if click.confirm(
                    "You are missing required packages. Would you like to install them?"
            ):
                import subprocess
                subprocess.run(["uv", "add", "azure-cosmos"], check=True)
                subprocess.run(["uv", "add", "azure-core"], check=True)
                subprocess.run(["uv", "add", "openai"], check=True)
            else:
                raise ImportError("You are missing required packages: 'azure-cosmos', 'azure-core', 'openai'.")

        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize the CosmosDB and OpenAI clients."""
        # Initialize CosmosDB client
        self.validate_params()
        if self.config.key is not None:
            self._cosmos_client = CosmosClient(
                self.config.cosmos_host,
                self.config.key,
                user_agent=self.USER_AGENT,
            )
        elif self.config.token_credential is not None:
            self._cosmos_client = CosmosClient(
                self.config.cosmos_host,
                self.config.token_credential,
                user_agent=self.USER_AGENT,
            )
        else:
            raise ValueError("Either 'key' or 'token_credential' must be provided")

        # Initialize OpenAI client
        if self.config.azure_openai_endpoint:
            self._openai_client = AzureOpenAI(
                azure_endpoint=self.config.azure_openai_endpoint,
                api_key=self.config.openai_api_key or os.environ.get("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01"
            )
        elif self.config.openai_api_key or os.environ.get("OPENAI_API_KEY"):
            self._openai_client = Client(
                api_key=self.config.openai_api_key or os.environ.get("OPENAI_API_KEY")
            )
        else:
            raise ValueError("Either Azure OpenAI endpoint or OpenAI API key must be provided")

        self._database = self._create_database()
        self._container = self._create_container_if_not_exists()

    def _create_database(self) -> DatabaseProxy:
        """Create the database if it doesn't exist."""
        return self._cosmos_client.create_database_if_not_exists(
            id=self.config.database_name,
            offer_throughput=self.config.cosmos_database_properties.get("offer_throughput"),
            session_token=self.config.cosmos_database_properties.get("session_token"),
            initial_headers=self.config.cosmos_database_properties.get("initial_headers"),
            etag=self.config.cosmos_database_properties.get("etag"),
            match_condition=self.config.cosmos_database_properties.get("match_condition"),
        )

    def _create_container_if_not_exists(self) -> ContainerProxy:
        """Create the container if it doesn't exist."""
        return self._database.create_container_if_not_exists(
            id=self.config.container_name,
            partition_key=self.config.cosmos_container_properties["partition_key"],
            indexing_policy=self.config.indexing_policy,
            vector_embedding_policy=self.config.vector_embedding_policy,
            full_text_policy=self.config.full_text_policy,
            offer_throughput=self.config.cosmos_container_properties.get("offer_throughput"),
            unique_key_policy=self.config.cosmos_container_properties.get("unique_key_policy"),
            conflict_resolution_policy=self.config.cosmos_container_properties.get("conflict_resolution_policy"),
            analytical_storage_ttl=self.config.cosmos_container_properties.get("analytical_storage_ttl"),
            computed_properties=self.config.cosmos_container_properties.get("computed_properties"),
            etag=self.config.cosmos_container_properties.get("etag"),
            match_condition=self.config.cosmos_container_properties.get("match_condition"),
            session_token=self.config.cosmos_container_properties.get("session_token"),
            initial_headers=self.config.cosmos_container_properties.get("initial_headers"),
            default_ttl=self.config.default_ttl,
        )

    def validate_params(self):
        if self.config.create_container:
            if (
                    self.config.indexing_policy["vectorIndexes"] is None
                    or len(self.config.indexing_policy["vectorIndexes"]) == 0
            ):
                raise ValueError(
                    "vectorIndexes cannot be null or empty in the indexing_policy."
                )
            if (
                    self.config.vector_embedding_policy is None
                    or len(self.config.vector_embedding_policy["vectorEmbeddings"]) == 0
            ):
                raise ValueError(
                    "vectorEmbeddings cannot be null "
                    "or empty in the vector_embedding_policy."
                )
            if self.config.cosmos_container_properties["partition_key"] is None:
                raise ValueError(
                    "partition_key cannot be null or empty for a container."
                )
            if self.config.enable_hybrid_search:
                if (
                        self.config.indexing_policy["fullTextIndexes"] is None
                        or len(self.config.indexing_policy["fullTextIndexes"]) == 0
                ):
                    raise ValueError(
                        "fullTextIndexes cannot be null or empty in the "
                        "indexing_policy if full text search is enabled."
                    )
                if (
                        self.config.full_text_policy is None
                        or len(self.config.full_text_policy["fullTextPaths"]) == 0
                ):
                    raise ValueError(
                        "fullTextPaths cannot be null or empty in the "
                        "full_text_policy if full text search is enabled."
                    )

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text."""
        try:
            response = self._openai_client.embeddings.create(
                input=text,
                model=self.config.embedding_model,
                dimensions=self.config.embedding_dimensions
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def _run(
        self,
        operation: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
    ) -> str:
        """Execute the semantic cache operation."""
        try:
            if operation == "search":
                return self._search_cache(prompt)
            elif operation == "update":
                return self._update_cache(prompt, response)
            elif operation == "clear":
                return self._clear_cache()
            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "valid_operations": ["search", "update", "clear"]
                })
        except Exception as e:
            logger.error(f"Semantic cache operation failed: {e}")
            return json.dumps({"error": str(e)})

    def _search_cache(
        self,
        prompt: str,
    ) -> str:
        """Search for cached responses similar to the given prompt."""
        if not prompt:
            return json.dumps({"error": "prompt is required for search operation"})

        try:
            # Generate embedding for the prompt
            query_embedding = self._generate_embedding(prompt)
            # Extract search terms from prompt
            search_terms = " ".join(prompt.split())
            if self.config.enable_hybrid_search:
                # Hybrid search combining vector and text search
                query_sql = f"""
                SELECT TOP 1 *,
                       VectorDistance(c.prompt_embedding, @query_embedding) as similarity_score
                FROM c
                ORDER BY RANK RRF(
                    FullTextScore(c.prompt, {search_terms}),
                    VectorDistance(c.prompt_embedding, {query_embedding}))
                )
                """

                parameters = [
                    {"name": "@query_embedding", "value": query_embedding},
                ]
            else:
                # Vector-only search
                query_sql = f"""
                SELECT TOP 1 *,
                       VectorDistance(c.prompt_embedding, @query_embedding) as similarity_score
                FROM c
                ORDER BY VectorDistance(c.prompt_embedding, @query_embedding)
                """

                parameters = [
                    {"name": "@query_embedding", "value": query_embedding}
                ]

            # Execute query
            items = list(self._container.query_items(
                query=query_sql,
                parameters=parameters,
                enable_cross_partition_query=False
            ))

            # Filter by similarity threshold and return best match
            for item in items:
                similarity_score = 1.0 - item.get("similarity_score", 1.0)  # Convert distance to similarity

                if similarity_score >= self.config.similarity_threshold:
                    return json.dumps({
                        "cache_hit": True,
                        "similarity_score": similarity_score,
                        "cached_response": item.get("response"),
                        "cache_id": item.get("id"),
                        "timestamp": item.get("metadata", {}).get("timestamp"),
                        "prompt": item.get("prompt")
                    })

            # No cache hit
            return json.dumps({
                "cache_hit": False,
                "similarity_score": 0.0,
                "message": f"No cached response found above similarity threshold {self.config.similarity_threshold}"
            })

        except Exception as e:
            logger.error(f"Failed to search cache: {e}")
            return json.dumps({"error": f"Failed to search cache: {str(e)}"})

    def _update_cache(
        self,
        prompt: str,
        response: str,
    ) -> str:
        """Store or update a prompt-response pair in the cache."""
        if not prompt:
            return json.dumps({"error": "prompt is required for update operation"})

        if not response:
            return json.dumps({"error": "response is required for update operation"})

        try:
            # Generate embedding for the prompt
            prompt_embedding = self._generate_embedding(prompt)

            # Create cache document
            cache_document = {
                "id": str(uuid.uuid4()),
                "prompt": prompt,
                "prompt_embedding": prompt_embedding,
                "response": response,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }

            # Add TTL if specified
            if self.config.default_ttl is not None:
                cache_document["ttl"] = self.config.default_ttl

            # Store in CosmosDB
            stored_item = self._container.upsert_item(body=cache_document)

            return json.dumps(stored_item)

        except Exception as e:
            logger.error(f"Failed to update cache: {e}")
            return json.dumps({"error": f"Failed to update cache: {str(e)}"})

    def _clear_cache(
        self,
    ) -> str:
        """Clear cache entries based on filters."""
        try:
            self._cosmos_client.delete_database(self.config.database_name)
            return "Cache is cleared."
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return json.dumps({"error": f"Failed to clear cache: {str(e)}"})