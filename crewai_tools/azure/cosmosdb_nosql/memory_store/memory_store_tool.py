import json
from datetime import datetime, timezone
from logging import getLogger
from typing import Any, ClassVar, Dict, List, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

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


class AzureCosmosDBMemoryConfig(BaseModel):
    """Configuration for Azure CosmosDB memory operations."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

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


class AzureCosmosDBMemoryToolSchema(BaseModel):
    """Input schema for AzureCosmosDBMemoryTool."""

    operation: str = Field(
        ...,
        description="The operation to perform: 'store', 'retrieve', 'update', 'delete', 'clear'"
    )


class AzureCosmosDBMemoryTool(BaseTool):
    """Tool for performing memory CRUD operations on Azure CosmosDB NoSQL."""

    USER_AGENT: ClassVar[str] = "CrewAI-CosmosDB-Memory-Tool-Python"

    name: str = "AzureCosmosDBMemoryTool"
    description: str = "A tool for storing, retrieving, updating, and deleting memory items in Azure CosmosDB."
    args_schema: Type[BaseModel] = AzureCosmosDBMemoryToolSchema

    config: AzureCosmosDBMemoryConfig = Field(..., description="Configuration for the memory tool")
    package_dependencies: List[str] = ["azure-cosmos", "azure-core"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._database = None
        self._container = None

        if not COSMOSDB_AVAILABLE:
            import click
            if click.confirm(
                    "You are missing the azure-cosmos package. Would you like to install it?"
            ):
                import subprocess
                subprocess.run(["uv", "add", "azure-cosmos"], check=True)
                subprocess.run(["uv", "add", "azure-core"], check=True)
            else:
                raise ImportError("You are missing the 'azure-cosmos' package.")

        self._initialize_client()

    def _initialize_client(self):
        """Initialize the CosmosDB client and container."""
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
        if not self.config.create_container:
            return self._database.get_container_client(self.config.container_name)

        return self._database.create_container_if_not_exists(
            id=self.config.container_name,
            partition_key=self.config.cosmos_container_properties["partition_key"],
            offer_throughput=self.config.cosmos_container_properties.get("offer_throughput"),
            unique_key_policy=self.config.cosmos_container_properties.get("unique_key_policy"),
            conflict_resolution_policy=self.config.cosmos_container_properties.get("conflict_resolution_policy"),
            analytical_storage_ttl=self.config.cosmos_container_properties.get("analytical_storage_ttl"),
            computed_properties=self.config.cosmos_container_properties.get("computed_properties"),
            etag=self.config.cosmos_container_properties.get("etag"),
            match_condition=self.config.cosmos_container_properties.get("match_condition"),
            session_token=self.config.cosmos_container_properties.get("session_token"),
            initial_headers=self.config.cosmos_container_properties.get("initial_headers"),
            default_ttl=self.config.cosmos_container_properties.get("default_ttl"),
        )

    def _get_partition_key_fields_and_paths(self) -> tuple[List[str], Any]:
        """Extract partition key field names and the raw partition key configuration."""
        partition_key_config = self.config.cosmos_container_properties.get("partition_key", {})

        # Handle both old and new format
        if isinstance(partition_key_config, dict):
            paths = partition_key_config.get("paths", ["/agent_id"])
        else:
            # Fallback for simple string format
            paths = [partition_key_config] if isinstance(partition_key_config, str) else ["/agent_id"]

        # Extract field names from paths (remove leading "/")
        field_names = [path.lstrip("/") for path in paths]

        return field_names, partition_key_config

    def _build_partition_key_filter(self, partition_key_value: Union[str, List[str]], field_names: List[str]) -> str:
        """Build SQL WHERE clause for partition key filtering."""
        if isinstance(partition_key_value, str):
            # Single partition key
            if len(field_names) > 1:
                raise ValueError(
                    f"Container has hierarchical partition key with {len(field_names)} levels, but only one value provided")
            return f"c.{field_names[0]} = '{partition_key_value}'"
        else:
            # Hierarchical partition key
            if len(partition_key_value) != len(field_names):
                raise ValueError(
                    f"Container has {len(field_names)} partition key levels, but {len(partition_key_value)} values provided")

            conditions = []
            for field, value in zip(field_names, partition_key_value):
                conditions.append(f"c.{field} = '{value}'")
            return " AND ".join(conditions)

    def _set_partition_key_fields_in_item(self, item: Dict[str, Any], partition_key_value: Union[str, List[str]],
                                          field_names: List[str]) -> None:
        """Set partition key fields in the document item."""
        if isinstance(partition_key_value, str):
            # Single partition key
            if len(field_names) > 1:
                raise ValueError(
                    f"Container has hierarchical partition key with {len(field_names)} levels, but only one value provided")
            item[field_names[0]] = partition_key_value
        else:
            # Hierarchical partition key
            if len(partition_key_value) != len(field_names):
                raise ValueError(
                    f"Container has {len(field_names)} partition key levels, but {len(partition_key_value)} values provided")

            for field, value in zip(field_names, partition_key_value):
                item[field] = value

    def _run(
        self,
        operation: str,
        memory_item: Dict[str, Any],
        partition_key_value: Optional[Union[str, List[str]]] = None,
        memory_id: Optional[str] = None,
        query_filter: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = 10,
        ttl: Optional[int] = None,
    ) -> str:
        """Execute the memory operation."""
        try:
            if operation == "store":
                return self._store_memory(memory_item, ttl)
            elif operation == "read":
                return self._read_memory(partition_key_value, memory_id)
            elif operation == "retrieve":
                return self._retrieve_memory(partition_key_value, query_filter, max_results)
            elif operation == "update":
                return self._update_memory(partition_key_value, memory_id, memory_item, ttl)
            elif operation == "delete":
                return self._delete_memory(partition_key_value, memory_id)
            elif operation == "clear":
                return self._clear_memory(partition_key_value)
            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "valid_operations": ["store", "retrieve", "update", "delete", "clear"]
                })
        except Exception as e:
            logger.error(f"Memory operation failed: {e}")
            return json.dumps({"error": str(e)})

    def _store_memory(
            self,
            memory_item: Dict[str, Any],
            ttl: Optional[int] = None
    ) -> str:
        """Store a new memory item."""
        if ttl is not None:
            memory_item["ttl"] = ttl

        try:
            response = self._container.create_item(
                body=memory_item
            )
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return json.dumps({"error": f"Failed to store memory: {str(e)}"})

    def _read_memory(
            self,
            partition_key_value: str,
            memory_id: str,
    ) -> str:
        """Read a memory item."""
        try:
            response = self._container.read_item(
                item=memory_id,
                partition_key=partition_key_value
            )
            return json.dumps(response)
        except Exception as e:
            logger.error(f"Failed to read memory: {e}")
            return json.dumps({"error": f"Failed to read memory: {str(e)}"})

    def _retrieve_memory(
            self,
            partition_key_value: Union[str, List[str]],
            query_filter: Optional[Dict[str, Any]] = None,
            max_results: Optional[int] = 10,
    ) -> str:
        """Retrieve memory items."""
        if not partition_key_value:
            return json.dumps({"error": "partition_key_value is required for retrieve operation"})
        try:
            field_names, _ = self._get_partition_key_fields_and_paths()
            partition_filter = self._build_partition_key_filter(partition_key_value, field_names)
            query_sql = f"SELECT * FROM c WHERE {partition_filter}"

            # Add additional query filters if provided
            if query_filter:
                for key, value in query_filter.items():
                    if isinstance(value, str):
                        query_sql += f" AND c.content.{key} = '{value}'"
                    else:
                        query_sql += f" AND c.content.{key} = {value}"

            # Add ordering by creation time (newest first)
            query_sql += " ORDER BY c.created_at DESC"

            # Add limit if specified
            if max_results:
                query_sql = f"SELECT TOP {max_results} * FROM ({query_sql}) AS subquery"

            items = list(self._container.query_items(
                query=query_sql,
                partition_key=partition_key_value,
                enable_cross_partition_query=False  # Since we're querying within a single partition
            ))
            return json.dumps(items)
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
            return json.dumps({"error": f"Failed to retrieve memory: {str(e)}"})

    def _update_memory(
            self,
            partition_key_value: str,
            memory_id: str,
            upsert_item: Dict[str, Any],
            ttl: Optional[int] = None,
    ) -> str:
        """Update an existing memory item."""
        if not partition_key_value:
            return json.dumps({"error": "partition_key_value is required for update operation"})

        if not memory_id:
            return json.dumps({"error": "memory_id is required for update operation"})

        try:
            existing_item = self._container.read_item(
                item=memory_id,
                partition_key=partition_key_value
            )

            if ttl is not None:
                upsert_item["ttl"] = ttl

            response = self._container.replace_item(
                item=existing_item,
                body=upsert_item,
                partition_key=partition_key_value
            )
            return json.dumps(response)

        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return json.dumps({"error": f"Failed to update memory: {str(e)}"})

    def _delete_memory(
            self,
            partition_key_value: str,
            memory_id: str
    ) -> str:
        """Delete a specific memory item."""
        if not partition_key_value:
            return json.dumps({"error": "partition_key_value is required for delete operation"})

        if not memory_id:
            return json.dumps({"error": "memory_id is required for delete operation"})

        try:
            self._container.delete_item(
                item=memory_id,
                partition_key=partition_key_value
            )
            return "Item with Id is {0} has been deleted".format(memory_id)
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return json.dumps({"error": f"Failed to delete memory: {str(e)}"})

    def _clear_memory(self, partition_key_value: Union[str, List[str]]) -> str:
        """Clear all memory items for a specific partition key value."""
        if not partition_key_value:
            return json.dumps({"error": "partition_key_value is required for clear operation"})

        try:
            field_names, _ = self._get_partition_key_fields_and_paths()

            # Query all items for the partition key value
            partition_filter = self._build_partition_key_filter(partition_key_value, field_names)
            query_sql = f"SELECT c.id FROM c WHERE {partition_filter}"

            items = list(self._container.query_items(
                query=query_sql,
                partition_key=partition_key_value,
                enable_cross_partition_query=False
            ))

            # Delete items in batches (Cosmos DB batch size limit is 100)
            deleted_count = 0
            batch_size = 100

            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]

                # Use execute_item_batch for efficient batch deletion
                batch_ops = [("delete", {"id": item["id"]}) for item in batch]

                if batch_ops:
                    self._container.execute_item_batch(
                        batch_operations=batch_ops,
                        partition_key=partition_key_value
                    )
                    deleted_count += len(batch_ops)

            return json.dumps({
                "success": True,
                "partition_key_value": partition_key_value,
                "operation": "clear",
                "deleted_count": deleted_count,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return json.dumps({"error": f"Failed to clear memory: {str(e)}"})