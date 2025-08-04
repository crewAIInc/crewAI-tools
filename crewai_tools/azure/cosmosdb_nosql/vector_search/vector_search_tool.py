import json
import os
import uuid
from collections import defaultdict
from logging import getLogger
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, Type

from crewai.tools import BaseTool
from openai import AzureOpenAI, Client
from pydantic import BaseModel, Field

try:
    from azure.cosmos import ContainerProxy, CosmosClient, DatabaseProxy
    from azure.core.credentials import TokenCredential

    COSMOSDB_AVAILABLE = True
except ImportError:
    COSMOSDB_AVAILABLE = False
    ContainerProxy = Any
    CosmosClient = Any
    DatabaseProxy = Any
    TokenCredential = Any

logger = getLogger(__name__)


class AzureCosmosDBNoSqlSearchConfig(BaseModel):
    """Configuration for Azure CosmosDB NoSql vector search queries."""

    max_results: Optional[int] = Field(
        default=5, description="The number of items to return."
    )
    with_embedding: bool = Field(
        default=False, description="Return embeddings if True."
    )
    where: Optional[str] = Field(
        default=None, description="Where clause."
    )
    offset_limit: Optional[str] = Field(
        default=None, description="Offset limit."
    )
    projection_mapping: Optional[Dict[str, Any]] = Field(
        default=None, description="Projection mapping."
    )
    full_text_rank_filter: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Full text rank filter."
    )
    weights: Optional[List[float]] = Field(
        default=None, description="Weights."
    )
    threshold: Optional[float] = Field(
        default=0.0, description="Threshold."
    )


class AzureCosmosDBNoSqlToolSchema(BaseModel):
    """Input for CosmosDBNoSqlTool."""

    query: str = Field(
        ...,
        description="The query to search retrieve relevant information from the CosmosDB NoSql database. Pass only the query, not the question.",
    )


class AzureCosmosDBNoSqlSearchTool(BaseTool):
    """Tool to perform a vector search the CosmosDb NoSql database"""

    VALID_SEARCH_TYPES: ClassVar[Set[str]] = {
        "vector",
        "full_text_search",
        "full_text_ranking",
        "hybrid",
    }
    USER_AGENT: ClassVar[str] = "Crew-AI-CDBNoSql-VectorSearchTool-Python"

    name: str = "AzureCosmosDBNoSqlVectorSearchTool"
    description: str = "A tool to per from a vector search on a CosmosDb database."

    args_schema: Type[BaseModel] = AzureCosmosDBNoSqlToolSchema
    query_config: AzureCosmosDBNoSqlSearchConfig = Field(
        default=None, description="Azure CosmosDB NoSql vector search configuration."
    )
    search_type: str = Field(
        default="vector",
        description="The type of vector search to perform. Valid options are vector, full text, hybrid."
    )
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="Text OpenAI embedding model to use",
    )
    cosmos_host: str = Field(
        ...,
        description="The connection string of the CosmosDB NoSql.",
    )
    key: Optional[str] = Field(
        ...,
        description="The Azure Key for the cosmos db.",
    )
    token_credential: Optional[TokenCredential] = Field(
        ...,
        description="The Azure Token Credential.",
    )
    database_name: str = Field("crewAI_database", description="The name of the CosmosDB NoSql database")
    container_name: str = Field("crewAI_container", description="The name of the CosmosDB NoSql container")
    vector_embedding_policy: Optional[Dict[str, Any]] = Field(
        default=None, description="The policy for the vector embedding."
    )
    indexing_policy: Dict[str, Any] = Field(
        ..., description="The policy for the indexing."
    )
    cosmos_container_properties: Dict[str, Any] = Field(
        default=..., description="The properties for the CosmosDB NoSql container."
    )
    cosmos_database_properties: Dict[str, Any] = Field(
        default=..., description="The properties for the CosmosDB NoSql database."
    )
    full_text_policy: Optional[Dict[str, Any]] = Field(
        default=None, description="The policy for the full text embedding."
    )
    text_key: str = Field(
        default="text",
        description="CosmosDB NoSql field that will contain the text for each document",
    )
    embedding_key: str = Field(
        default="embedding",
        description="CosmosDB NoSql field that will contain the embedding for each document",
    )
    dimensions: int = Field(
        default=1536,
        description="Number of dimensions in the embedding vector",
    )
    metadata_key: str = Field(
        default="metadata",
        description="CosmosDB NoSql field that will contain the metadata for each document",
    )
    create_container: bool = Field(
        default=True,
        description="Should create the CosmosDB NoSql container.",
    )
    full_text_search_enabled: bool = Field(
        default=False,
        description="Is the full text search enabled.",
    )
    table_alias: str = Field(
        default="c",
        description="The alias of the CosmosDB NoSql table.",
    )
    package_dependencies: List[str] = ["azure-cosmos", "azure-core"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._database = None
        if not COSMOSDB_AVAILABLE:
            import click

            if click.confirm(
                    "You are missing the azure-cosmos crewai tool. Would you like to install it?",
            ):
                import subprocess
                subprocess.run(["uv", "add", "azure-cosmos"], check=True)
                subprocess.run(["uv", "add", "azure-core"], check=True)
            else:
                raise ImportError("You are missing the 'azure-cosmos' crew ai tool.")

        if "AZURE_OPENAI_ENDPOINT" in os.environ:
            self._openai_client = AzureOpenAI()
        elif "OPENAI_API_KEY" in os.environ:
            self._openai_client = Client()
        else:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for AzureCosmosDBNoSqlVectorSearchTool and it is mandatory to use the tool."
            )

        self.validate_params()

        if self.key is not None:
            self._cosmos_client = CosmosClient(
                self.cosmos_host,
                self.key,
                user_agent=self.USER_AGENT,
            )
        elif self.token_credential is not None:
            self._cosmos_client = CosmosClient(
                self.cosmos_host,
                self.token_credential,
                user_agent=self.USER_AGENT,
            )

        self._database = self.create_database()
        self._container = self.create_container_if_not_exists()

    def create_database(self) -> DatabaseProxy:
        # Create the database if it already doesn't exist
        self._database = self._cosmos_client.create_database_if_not_exists(
            id=self.database_name,
            offer_throughput=self.cosmos_database_properties.get("offer_throughput"),
            session_token=self.cosmos_database_properties.get("session_token"),
            initial_headers=self.cosmos_database_properties.get("initial_headers"),
            etag=self.cosmos_database_properties.get("etag"),
            match_condition=self.cosmos_database_properties.get("match_condition"),
        )
        return self._database

    def create_container_if_not_exists(self) -> ContainerProxy:
        # Create the collection if it already doesn't exist
        self._container = self._database.create_container_if_not_exists(
            id=self.container_name,
            partition_key=self.cosmos_container_properties["partition_key"],
            indexing_policy=self.indexing_policy,
            default_ttl=self.cosmos_container_properties.get("default_ttl"),
            offer_throughput=self.cosmos_container_properties.get("offer_throughput"),
            unique_key_policy=self.cosmos_container_properties.get(
                "unique_key_policy"
            ),
            conflict_resolution_policy=self.cosmos_container_properties.get(
                "conflict_resolution_policy"
            ),
            analytical_storage_ttl=self.cosmos_container_properties.get(
                "analytical_storage_ttl"
            ),
            computed_properties=self.cosmos_container_properties.get(
                "computed_properties"
            ),
            etag=self.cosmos_container_properties.get("etag"),
            match_condition=self.cosmos_container_properties.get("match_condition"),
            session_token=self.cosmos_container_properties.get("session_token"),
            initial_headers=self.cosmos_container_properties.get("initial_headers"),
            vector_embedding_policy=self.vector_embedding_policy,
            full_text_policy=self.full_text_policy,
        )
        return self._container

    def validate_params(self):
        if self.search_type not in self.VALID_SEARCH_TYPES:
            raise ValueError(
                f"Invalid search_type '{self.search_type}'. "
                f"Valid options are: {self.VALID_SEARCH_TYPES}"
            )

        if self.create_container:
            if (
                    self.indexing_policy["vectorIndexes"] is None
                    or len(self.indexing_policy["vectorIndexes"]) == 0
            ):
                raise ValueError(
                    "vectorIndexes cannot be null or empty in the indexing_policy."
                )
            if (
                    self.vector_embedding_policy is None
                    or len(self.vector_embedding_policy["vectorEmbeddings"]) == 0
            ):
                raise ValueError(
                    "vectorEmbeddings cannot be null "
                    "or empty in the vector_embedding_policy."
                )
            if self.cosmos_container_properties["partition_key"] is None:
                raise ValueError(
                    "partition_key cannot be null or empty for a container."
                )
            if self.full_text_search_enabled:
                if (
                        self.indexing_policy["fullTextIndexes"] is None
                        or len(self.indexing_policy["fullTextIndexes"]) == 0
                ):
                    raise ValueError(
                        "fullTextIndexes cannot be null or empty in the "
                        "indexing_policy if full text search is enabled."
                    )
                if (
                        self.full_text_policy is None
                        or len(self.full_text_policy["fullTextPaths"]) == 0
                ):
                    raise ValueError(
                        "fullTextPaths cannot be null or empty in the "
                        "full_text_policy if full text search is enabled."
                    )

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.

        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            ids: Optional list of ids associated with the texts.
            **kwargs: Additional keyword arguments to pass to the embedding method.

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        # If the texts is empty, throw an error
        if not texts:
            raise Exception("Texts can not be null or empty")

        # Embed and create the documents
        embeddings = self._embed_texts(texts)
        text_key = self.text_key
        embedding_key = self.embedding_key
        partition_key = self.cosmos_container_properties["partition_key"]

        _metadatas = list(metadatas if metadatas is not None else ({} for _ in texts))
        _ids = list(ids if ids is not None else (str(uuid.uuid4()) for _ in texts))

        # Generate partition key values
        partition_key_values = []
        for idx, meta in enumerate(_metadatas):
            if partition_key == "id":
                partition_key_values.append(_ids[idx])
            else:
                # Look for nested key in metadata
                value = meta.get(partition_key)
                if value is None:
                    raise ValueError(f"Partition key '{partition_key}' not found in metadata at index {idx}")
                partition_key_values.append(value)

        items_to_insert = [
            {
                "id": i,
                "pk": pk,
                text_key: t,
                embedding_key: embedding,
                "metadata": m,
            }
            for i, pk, t, m, embedding in
            zip(_ids, partition_key_values, texts, _metadatas, embeddings)
        ]

        grouped_items_by_pk = defaultdict(list)
        for item in items_to_insert:
            grouped_items_by_pk[item["pk"]].append(item)

        BATCH_SIZE = 25
        doc_ids: List[str] = []
        for pk_value, items in grouped_items_by_pk.items():
            for i in range(0, len(items), BATCH_SIZE):
                batch = items[i:i + BATCH_SIZE]
                batch_ops = [("create", doc) for doc in batch]

                self._container.execute_item_batch(
                    batch_operations=batch_ops,
                    partition_key=pk_value
                )
                doc_ids.extend(doc["id"] for doc in batch)
        return doc_ids

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [
            i.embedding
            for i in self._openai_client.embeddings.create(
                input=texts,
                model=self.embedding_model,
                dimensions=self.dimensions,
            ).data
        ]

    def _run(self, query: str) -> str:
        try:
            search_query, parameters = self._construct_query(
                query=query,
            )
            results = self._execute_query(
                query=search_query,
                parameters=parameters,
            )
            return json.dumps(results)
        except Exception as e:
            logger.error(f"Error: {e}")
            return ""

    def _construct_query(
        self,
        query: str,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        config = self.query_config or AzureCosmosDBNoSqlSearchConfig()
        # Create the embedding for the query
        embeddings = self._embed_texts([query])[0]
        if (
            self.search_type == "full_text_ranking"
            or self.search_type == "hybrid"
        ):
            query = f"SELECT {'TOP ' + str(config.max_results) + ' ' if not config.offset_limit else ''}"
        else:
            query = f"""SELECT {"TOP @top " if not config.offset_limit else ""}"""
        query += self._generate_projection_fields(
            embeddings,
        )
        table = self.table_alias
        query += f" FROM {table}"

        # Add where_clause if specified
        if config.where:
            query += f" WHERE {config.where}"

        # TODO: Update the code to use parameters once parametrized queries
        #  are allowed for these query functions
        if self.search_type == "full_text_ranking":
            if config.full_text_rank_filter is None:
                raise ValueError(
                    "full_text_rank_filter cannot be None for FULL_TEXT_RANK queries."
                )
            if len(config.full_text_rank_filter) == 1:
                query += f""" ORDER BY RANK FullTextScore({table}.{config.full_text_rank_filter[0]["search_field"]}, 
                {", ".join(f"'{term}'" for term in config.full_text_rank_filter[0]["search_text"].split())})"""  # noqa:E501
            else:
                rank_components = [
                    f"FullTextScore({table}.{search_item['search_field']}, "
                    + ", ".join(
                        f"'{term}'" for term in search_item["search_text"].split()
                    )
                    + ")"
                    for search_item in config.full_text_rank_filter
                ]
                query = f" ORDER BY RANK RRF({', '.join(rank_components)})"
        elif self.search_type == "vector":
            query += " ORDER BY VectorDistance(c[@embeddingKey], @embeddings)"
        elif self.search_type == "hybrid":
            if config.full_text_rank_filter is None:
                raise ValueError(
                    "full_text_rank_filter cannot be None for HYBRID queries."
                )
            rank_components = [
                f"FullTextScore({table}.{search_item['search_field']}, "
                + ", ".join(f"'{term}'" for term in search_item["search_text"].split())
                + ")"
                for search_item in config.full_text_rank_filter
            ]
            query += f""" ORDER BY RANK RRF({", ".join(rank_components)}, 
            VectorDistance({table}.{self.embedding_key}, {embeddings})"""  # noqa:E501
            if config.weights:
                query += f", {config.weights})"
            else:
                query += ")"
        else:
            query += ""

        # Add limit_offset_clause if specified
        if config.offset_limit is not None:
            query += f""" {config.offset_limit}"""

        # TODO: Remove this if check once parametrized queries
        #  are allowed for these query functions
        parameters = []
        if (
            self.search_type == "full_text_search"
            or self.search_type == "vector"
        ):
            parameters = self._build_parameters(
                embeddings=embeddings,
            )
        return query, parameters

    def _generate_projection_fields(
        self,
        embeddings: Optional[List[float]] = None,
    ) -> str:
        # TODO: Remove the if check, once parametrized queries
        #  are supported for these query functions.
        config = self.query_config or AzureCosmosDBNoSqlSearchConfig()
        table = self.table_alias
        if (
            self.search_type == "full_text_ranking"
            or self.search_type == "hybrid"
        ):
            if config.projection_mapping:
                projection = ", ".join(
                    f"{table}.{key} as {alias}"
                    for key, alias in config.projection_mapping.items()
                )
            elif config.full_text_rank_filter:
                projection = (
                    table
                    + ".id, "
                    + ", ".join(
                        f"{table}.{search_item['search_field']} "
                        f"as {search_item['search_field']}"
                        for search_item in config.full_text_rank_filter
                    )
                )
            else:
                projection = (
                    f"{table}.id, {table}.{self.text_key} "
                )
                f"as description, {table}.{self.metadata_key} as metadata"
            if self.search_type == "hybrid":
                if config.with_embedding:
                    projection += f", {table}.{self.embedding_key} as embedding"  # noqa:E501
                projection += (
                    f", VectorDistance({table}.{self.embedding_key}, "  # noqa:E501
                    f"{embeddings}) as SimilarityScore"
                )
        else:
            if config.projection_mapping:
                projection = ", ".join(
                    f"{table}[@{key}] as {alias}"
                    for key, alias in config.projection_mapping.items()
                )
            elif config.full_text_rank_filter:
                projection = f"{table}.id" + ", ".join(
                    f"{table}.{search_item['search_field']} as {search_item['search_field']}"  # noqa: E501
                    for search_item in config.full_text_rank_filter
                )
            else:
                projection = f"{table}.id, {table}[@textKey] as description, {table}[@metadataKey] as metadata"  # noqa: E501

            if self.search_type == "vector":
                if config.with_embedding:
                    projection += f", {table}[@embeddingKey] as embedding"
                projection += (
                    f", VectorDistance({table}[@embeddingKey], "
                    "@embeddings) as SimilarityScore"
                )
        return projection

    def _build_parameters(
        self,
        embeddings: Optional[List[float]],
    ) -> List[Dict[str, Any]]:
        config = self.query_config or AzureCosmosDBNoSqlSearchConfig()
        parameters: List[Dict[str, Any]] = [
            {"name": "@top", "value": config.max_results},
        ]

        if config.projection_mapping:
            for key in config.projection_mapping.keys():
                parameters.append({"name": f"@{key}", "value": key})
        else:
            parameters.append(
                {"name": "@textKey", "value": self.text_key}
            )
            parameters.append({"name": "@metadataKey", "value": self.metadata_key})

        if self.search_type == "vector":
            parameters.append(
                {
                    "name": "@embeddingKey",
                    "value": self.embedding_key,
                }
            )
            parameters.append({"name": "@embeddings", "value": embeddings})

        return parameters

    def _execute_query(
        self,
        query: str,
        parameters: List[Dict[str, Any]],
    ) -> List[Tuple[List[Any], float]]:
        config = self.query_config or AzureCosmosDBNoSqlSearchConfig()
        docs = []
        items = list(
            self._container.query_items(
                query=query, parameters=parameters, enable_cross_partition_query=True
            )
        )
        for item in items:
            if self.search_type in [
                "vector",
                "hybrid",
            ]:
                score = item["SimilarityScore"]
                if score <= config.threshold:
                    continue
                docs.append(item)
            else:
                docs.append(item)
        return docs

