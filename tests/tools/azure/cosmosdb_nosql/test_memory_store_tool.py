import json
import os
# Direct import to avoid import chain issues
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool import AzureCosmosDBMemoryConfig, \
    AzureCosmosDBMemoryTool, AzureCosmosDBMemoryToolSchema

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


# Unit Test Fixtures
@pytest.fixture
def mock_memory_config():
    """Create a mock memory configuration."""
    return AzureCosmosDBMemoryConfig(
        cosmos_host="https://test.documents.azure.com:443/",
        key="test_key",
        database_name="test_memory_db",
        container_name="test_memory_container",
        cosmos_container_properties={
            "partition_key": {"paths": ["/agent_id"], "kind": "Hash"}
        }
    )


@pytest.fixture
def mock_hierarchical_config():
    """Create a mock config with hierarchical partition key."""
    return AzureCosmosDBMemoryConfig(
        cosmos_host="https://test.documents.azure.com:443/",
        key="test_key",
        database_name="test_memory_db",
        container_name="test_memory_container",
        cosmos_container_properties={
            "partition_key": {"paths": ["/agent_id", "/session_id"], "kind": "MultiHash"}
        }
    )


@pytest.fixture
def mock_cosmos_container():
    """Mock CosmosDB container for testing."""
    mock_container = MagicMock()

    # Mock responses for different operations
    mock_container.create_item.return_value = {
        "id": "test_memory_123",
        "agent_id": "agent_1",
        "content": {"message": "Test memory"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "_ts": 1234567890
    }

    mock_container.read_item.return_value = {
        "id": "test_memory_123",
        "agent_id": "agent_1",
        "content": {"message": "Test memory"},
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    mock_container.query_items.return_value = [
        {
            "id": "memory_1",
            "agent_id": "agent_1",
            "content": {"message": "First memory"},
            "created_at": "2025-08-01T10:00:00Z"
        },
        {
            "id": "memory_2",
            "agent_id": "agent_1",
            "content": {"message": "Second memory"},
            "created_at": "2025-08-01T11:00:00Z"
        }
    ]

    mock_container.replace_item.return_value = {
        "id": "test_memory_123",
        "agent_id": "agent_1",
        "content": {"message": "Updated memory"},
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    mock_container.delete_item.return_value = None
    mock_container.execute_item_batch.return_value = None

    return mock_container


@pytest.fixture
def memory_tool(mock_memory_config):
    """Create a memory tool instance with mocked dependencies."""
    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", True):
        with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.CosmosClient") as mock_cosmos_client:
            # Mock CosmosDB client and database
            mock_cosmos_instance = MagicMock()
            mock_cosmos_client.return_value = mock_cosmos_instance

            mock_database = MagicMock()
            mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database

            mock_container = MagicMock()
            mock_database.create_container_if_not_exists.return_value = mock_container

            # Create tool instance
            tool = AzureCosmosDBMemoryTool(config=mock_memory_config)
            tool._container = mock_container

            yield tool


@pytest.fixture
def hierarchical_memory_tool(mock_hierarchical_config):
    """Create a memory tool with hierarchical partition key."""
    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", True):
        with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.CosmosClient") as mock_cosmos_client:
            mock_cosmos_instance = MagicMock()
            mock_cosmos_client.return_value = mock_cosmos_instance

            mock_database = MagicMock()
            mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database

            mock_container = MagicMock()
            mock_database.create_container_if_not_exists.return_value = mock_container

            tool = AzureCosmosDBMemoryTool(config=mock_hierarchical_config)
            tool._container = mock_container

            yield tool


# Test Configuration Classes
def test_memory_config_defaults():
    """Test default configuration values."""
    config = AzureCosmosDBMemoryConfig(
        cosmos_host="https://test.documents.azure.com:443/",
        key="test_key"
    )

    assert config.database_name == "memory_database"
    assert config.container_name == "memory_container"
    assert config.create_container is True
    assert config.cosmos_container_properties["partition_key"]["paths"] == ["/agent_id"]


def test_memory_tool_schema():
    """Test the input schema validation."""
    schema = AzureCosmosDBMemoryToolSchema(operation="store")
    assert schema.operation == "store"

    # Test all valid operations
    valid_operations = ["store", "retrieve", "update", "delete", "clear"]
    for op in valid_operations:
        schema = AzureCosmosDBMemoryToolSchema(operation=op)
        assert schema.operation == op


# Test Tool Initialization
def test_tool_initialization_with_key(mock_memory_config):
    """Test tool initialization with API key."""
    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", True):
        with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.CosmosClient") as mock_client:
            tool = AzureCosmosDBMemoryTool(config=mock_memory_config)
            mock_client.assert_called_once()
            assert tool.name == "AzureCosmosDBMemoryTool"


def test_tool_initialization_with_token_credential():
    """Test tool initialization with token credential."""
    from azure.core.credentials import TokenCredential

    mock_credential = MagicMock(spec=TokenCredential)
    config = AzureCosmosDBMemoryConfig(
        cosmos_host="https://test.documents.azure.com:443/",
        token_credential=mock_credential
    )

    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", True):
        with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.CosmosClient") as mock_client:
            tool = AzureCosmosDBMemoryTool(config=config)
            mock_client.assert_called_once()


def test_tool_initialization_missing_credentials():
    """Test tool initialization fails without credentials."""
    config = AzureCosmosDBMemoryConfig(
        cosmos_host="https://test.documents.azure.com:443/"
    )

    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", True):
        with pytest.raises(ValueError, match="Either 'key' or 'token_credential' must be provided"):
            AzureCosmosDBMemoryTool(config=config)


def test_tool_initialization_missing_dependency(mock_memory_config):
    """Test tool initialization when dependencies are missing."""
    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", False):
        with patch("click.confirm", return_value=False):
            with pytest.raises(ImportError, match="You are missing the 'azure-cosmos' package"):
                AzureCosmosDBMemoryTool(config=mock_memory_config)


# Test Partition Key Handling
def test_get_partition_key_fields_single(memory_tool):
    """Test extracting single partition key field."""
    field_names, config = memory_tool._get_partition_key_fields_and_paths()
    assert field_names == ["agent_id"]
    assert config["paths"] == ["/agent_id"]


def test_get_partition_key_fields_hierarchical(hierarchical_memory_tool):
    """Test extracting hierarchical partition key fields."""
    field_names, config = hierarchical_memory_tool._get_partition_key_fields_and_paths()
    assert field_names == ["agent_id", "session_id"]
    assert config["paths"] == ["/agent_id", "/session_id"]


def test_build_partition_key_filter_single(memory_tool):
    """Test building filter for single partition key."""
    field_names = ["agent_id"]
    filter_clause = memory_tool._build_partition_key_filter("agent_1", field_names)
    assert filter_clause == "c.agent_id = 'agent_1'"


def test_build_partition_key_filter_hierarchical(hierarchical_memory_tool):
    """Test building filter for hierarchical partition key."""
    field_names = ["agent_id", "session_id"]
    filter_clause = hierarchical_memory_tool._build_partition_key_filter(
        ["agent_1", "session_123"], field_names
    )
    assert filter_clause == "c.agent_id = 'agent_1' AND c.session_id = 'session_123'"


def test_build_partition_key_filter_mismatch_single(memory_tool):
    """Test error when providing multiple values for single partition key."""
    field_names = ["agent_id"]
    with pytest.raises(ValueError, match="Container has 1 partition key levels, but 2 values provided"):
        memory_tool._build_partition_key_filter(["agent_1", "session_123"], field_names)


def test_build_partition_key_filter_mismatch_hierarchical(hierarchical_memory_tool):
    """Test error when providing wrong number of values for hierarchical partition key."""
    field_names = ["agent_id", "session_id"]
    with pytest.raises(ValueError,
                       match="Container has hierarchical partition key with 2 levels, but only one value provided"):
        hierarchical_memory_tool._build_partition_key_filter("agent_1", field_names)


def test_set_partition_key_fields_single(memory_tool):
    """Test setting single partition key field in item."""
    item = {"id": "test", "content": {"message": "test"}}
    field_names = ["agent_id"]
    memory_tool._set_partition_key_fields_in_item(item, "agent_1", field_names)
    assert item["agent_id"] == "agent_1"


def test_set_partition_key_fields_hierarchical(hierarchical_memory_tool):
    """Test setting hierarchical partition key fields in item."""
    item = {"id": "test", "content": {"message": "test"}}
    field_names = ["agent_id", "session_id"]
    hierarchical_memory_tool._set_partition_key_fields_in_item(
        item, ["agent_1", "session_123"], field_names
    )
    assert item["agent_id"] == "agent_1"
    assert item["session_id"] == "session_123"


# Test Memory Operations
def test_store_memory_success(memory_tool, mock_cosmos_container):
    """Test successful memory storage."""
    memory_tool._container = mock_cosmos_container

    memory_item = {
        "id": "test_memory_123",
        "agent_id": "agent_1",
        "content": {"message": "Test memory"},
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = memory_tool._store_memory(memory_item)
    parsed_result = json.loads(result)

    assert "id" in parsed_result
    assert parsed_result["agent_id"] == "agent_1"
    mock_cosmos_container.create_item.assert_called_once_with(body=memory_item)


def test_store_memory_with_ttl(memory_tool, mock_cosmos_container):
    """Test storing memory with TTL."""
    memory_tool._container = mock_cosmos_container

    memory_item = {"id": "test", "agent_id": "agent_1", "content": {"message": "test"}}
    ttl = 3600  # 1 hour

    result = memory_tool._store_memory(memory_item, ttl)

    # Verify TTL was added to item
    call_args = mock_cosmos_container.create_item.call_args[1]['body']
    assert call_args["ttl"] == ttl


def test_store_memory_failure(memory_tool, mock_cosmos_container):
    """Test memory storage failure."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.create_item.side_effect = Exception("Storage failed")

    memory_item = {"id": "test", "agent_id": "agent_1", "content": {"message": "test"}}

    result = memory_tool._store_memory(memory_item)
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "Storage failed" in parsed_result["error"]


def test_read_memory_success(memory_tool, mock_cosmos_container):
    """Test successful memory reading."""
    memory_tool._container = mock_cosmos_container

    result = memory_tool._read_memory("agent_1", "test_memory_123")
    parsed_result = json.loads(result)

    assert parsed_result["id"] == "test_memory_123"
    assert parsed_result["agent_id"] == "agent_1"
    mock_cosmos_container.read_item.assert_called_once_with(
        item="test_memory_123",
        partition_key="agent_1"
    )


def test_read_memory_failure(memory_tool, mock_cosmos_container):
    """Test memory reading failure."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.read_item.side_effect = Exception("Item not found")

    result = memory_tool._read_memory("agent_1", "nonexistent")
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "Item not found" in parsed_result["error"]


def test_retrieve_memory_success(memory_tool, mock_cosmos_container):
    """Test successful memory retrieval."""
    memory_tool._container = mock_cosmos_container

    result = memory_tool._retrieve_memory("agent_1")
    parsed_result = json.loads(result)

    assert len(parsed_result) == 2
    assert parsed_result[0]["id"] == "memory_1"
    assert parsed_result[1]["id"] == "memory_2"
    mock_cosmos_container.query_items.assert_called_once()


def test_retrieve_memory_with_filter(memory_tool, mock_cosmos_container):
    """Test memory retrieval with query filter."""
    memory_tool._container = mock_cosmos_container

    query_filter = {"category": "conversation"}
    result = memory_tool._retrieve_memory("agent_1", query_filter, 5)

    # Verify the query was constructed with filter
    call_args = mock_cosmos_container.query_items.call_args
    query_sql = call_args[1]['query']
    assert "c.content.category = 'conversation'" in query_sql


def test_retrieve_memory_missing_partition_key(memory_tool):
    """Test retrieve memory without partition key."""
    result = memory_tool._retrieve_memory(None)
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "partition_key_value is required" in parsed_result["error"]


def test_retrieve_memory_hierarchical(hierarchical_memory_tool, mock_cosmos_container):
    """Test memory retrieval with hierarchical partition key."""
    hierarchical_memory_tool._container = mock_cosmos_container

    result = hierarchical_memory_tool._retrieve_memory(["agent_1", "session_123"])

    call_args = mock_cosmos_container.query_items.call_args
    query_sql = call_args[1]['query']
    assert "c.agent_id = 'agent_1' AND c.session_id = 'session_123'" in query_sql


def test_update_memory_success(memory_tool, mock_cosmos_container):
    """Test successful memory update."""
    memory_tool._container = mock_cosmos_container

    upsert_item = {"content": {"message": "Updated memory"}}
    result = memory_tool._update_memory("agent_1", "test_memory_123", upsert_item)
    parsed_result = json.loads(result)

    assert "updated_at" in parsed_result
    mock_cosmos_container.read_item.assert_called_once()
    mock_cosmos_container.replace_item.assert_called_once()


def test_update_memory_with_ttl(memory_tool, mock_cosmos_container):
    """Test memory update with TTL."""
    memory_tool._container = mock_cosmos_container

    upsert_item = {"content": {"message": "Updated memory"}}
    ttl = 7200  # 2 hours

    result = memory_tool._update_memory("agent_1", "test_memory_123", upsert_item, ttl)

    # Verify TTL was added
    call_args = mock_cosmos_container.replace_item.call_args[1]['body']
    assert call_args["ttl"] == ttl


def test_update_memory_missing_partition_key(memory_tool):
    """Test update memory without partition key."""
    result = memory_tool._update_memory(None, "test_id", {})
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "partition_key_value is required" in parsed_result["error"]


def test_update_memory_missing_id(memory_tool):
    """Test update memory without memory ID."""
    result = memory_tool._update_memory("agent_1", None, {})
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "memory_id is required" in parsed_result["error"]


def test_delete_memory_success(memory_tool, mock_cosmos_container):
    """Test successful memory deletion."""
    memory_tool._container = mock_cosmos_container

    result = memory_tool._delete_memory("agent_1", "test_memory_123")

    assert "test_memory_123" in result
    assert "has been deleted" in result
    mock_cosmos_container.delete_item.assert_called_once_with(
        item="test_memory_123",
        partition_key="agent_1"
    )


def test_delete_memory_missing_partition_key(memory_tool):
    """Test delete memory without partition key."""
    result = memory_tool._delete_memory(None, "test_id")
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "partition_key_value is required" in parsed_result["error"]


def test_delete_memory_missing_id(memory_tool):
    """Test delete memory without memory ID."""
    result = memory_tool._delete_memory("agent_1", None)
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "memory_id is required" in parsed_result["error"]


def test_delete_memory_failure(memory_tool, mock_cosmos_container):
    """Test memory deletion failure."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.delete_item.side_effect = Exception("Delete failed")

    result = memory_tool._delete_memory("agent_1", "test_memory_123")
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "Delete failed" in parsed_result["error"]


def test_clear_memory_success(memory_tool, mock_cosmos_container):
    """Test successful memory clearing."""
    memory_tool._container = mock_cosmos_container

    # Mock query_items to return items to delete
    mock_cosmos_container.query_items.return_value = [
        {"id": "memory_1"},
        {"id": "memory_2"},
        {"id": "memory_3"}
    ]

    result = memory_tool._clear_memory("agent_1")
    parsed_result = json.loads(result)

    assert parsed_result["success"] is True
    assert parsed_result["deleted_count"] == 3
    assert parsed_result["partition_key_value"] == "agent_1"
    mock_cosmos_container.execute_item_batch.assert_called_once()


def test_clear_memory_hierarchical(hierarchical_memory_tool, mock_cosmos_container):
    """Test clearing memory with hierarchical partition key."""
    hierarchical_memory_tool._container = mock_cosmos_container

    mock_cosmos_container.query_items.return_value = [{"id": "memory_1"}]

    result = hierarchical_memory_tool._clear_memory(["agent_1", "session_123"])
    parsed_result = json.loads(result)

    assert parsed_result["success"] is True
    assert parsed_result["partition_key_value"] == ["agent_1", "session_123"]

    # Verify query was constructed correctly
    call_args = mock_cosmos_container.query_items.call_args
    query_sql = call_args[1]['query']
    assert "c.agent_id = 'agent_1' AND c.session_id = 'session_123'" in query_sql


def test_clear_memory_large_batch(memory_tool, mock_cosmos_container):
    """Test clearing memory with large number of items (batch processing)."""
    memory_tool._container = mock_cosmos_container

    # Create 250 items to test batch processing (batch size is 100)
    items = [{"id": f"memory_{i}"} for i in range(250)]
    mock_cosmos_container.query_items.return_value = items

    result = memory_tool._clear_memory("agent_1")
    parsed_result = json.loads(result)

    assert parsed_result["success"] is True
    assert parsed_result["deleted_count"] == 250

    # Should have called execute_item_batch 3 times (100, 100, 50)
    assert mock_cosmos_container.execute_item_batch.call_count == 3


def test_clear_memory_missing_partition_key(memory_tool):
    """Test clear memory without partition key."""
    result = memory_tool._clear_memory(None)
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "partition_key_value is required" in parsed_result["error"]


def test_clear_memory_failure(memory_tool, mock_cosmos_container):
    """Test memory clearing failure."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.query_items.side_effect = Exception("Query failed")

    result = memory_tool._clear_memory("agent_1")
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "Query failed" in parsed_result["error"]


# Test _run Method (Main Entry Point)
def test_run_store_operation(memory_tool, mock_cosmos_container):
    """Test _run method with store operation."""
    memory_tool._container = mock_cosmos_container

    memory_item = {
        "id": "test_123",
        "agent_id": "agent_1",
        "content": {"message": "Test memory"}
    }

    result = memory_tool._run(
        operation="store",
        memory_item=memory_item
    )

    parsed_result = json.loads(result)
    assert "id" in parsed_result


def test_run_retrieve_operation(memory_tool, mock_cosmos_container):
    """Test _run method with retrieve operation."""
    memory_tool._container = mock_cosmos_container

    result = memory_tool._run(
        operation="retrieve",
        memory_item={},  # Empty dict for retrieve operation
        partition_key_value="agent_1",
        max_results=5
    )

    parsed_result = json.loads(result)
    assert len(parsed_result) == 2


def test_run_update_operation(memory_tool, mock_cosmos_container):
    """Test _run method with update operation."""
    memory_tool._container = mock_cosmos_container

    memory_item = {"content": {"message": "Updated memory"}}
    result = memory_tool._run(
        operation="update",
        memory_item=memory_item,
        partition_key_value="agent_1",
        memory_id="test_123"
    )

    parsed_result = json.loads(result)
    assert "updated_at" in parsed_result


def test_run_delete_operation(memory_tool, mock_cosmos_container):
    """Test _run method with delete operation."""
    memory_tool._container = mock_cosmos_container

    result = memory_tool._run(
        operation="delete",
        memory_item={},  # Empty dict for delete operation
        partition_key_value="agent_1",
        memory_id="test_123"
    )

    assert "has been deleted" in result


def test_run_clear_operation(memory_tool, mock_cosmos_container):
    """Test _run method with clear operation."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.query_items.return_value = [{"id": "memory_1"}]

    result = memory_tool._run(
        operation="clear",
        memory_item={},  # Empty dict for clear operation
        partition_key_value="agent_1"
    )

    parsed_result = json.loads(result)
    assert parsed_result["success"] is True


def test_run_invalid_operation(memory_tool):
    """Test _run method with invalid operation."""
    result = memory_tool._run(
        operation="invalid_op",
        memory_item={}
    )
    parsed_result = json.loads(result)

    assert "error" in parsed_result
    assert "Unknown operation: invalid_op" in parsed_result["error"]
    assert "valid_operations" in parsed_result


def test_run_operation_exception(memory_tool, mock_cosmos_container):
    """Test _run method with operation exception."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.create_item.side_effect = Exception("Cosmos DB error")

    memory_item = {"id": "test", "agent_id": "agent_1", "content": {"message": "test"}}

    result = memory_tool._run(
        operation="store",
        memory_item=memory_item
    )

    parsed_result = json.loads(result)
    assert "error" in parsed_result


# Test Edge Cases and Error Conditions
def test_empty_query_results(memory_tool, mock_cosmos_container):
    """Test handling empty query results."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.query_items.return_value = []

    result = memory_tool._retrieve_memory("agent_1")
    parsed_result = json.loads(result)

    assert len(parsed_result) == 0


def test_clear_memory_no_items(memory_tool, mock_cosmos_container):
    """Test clearing memory when no items exist."""
    memory_tool._container = mock_cosmos_container
    mock_cosmos_container.query_items.return_value = []

    result = memory_tool._clear_memory("agent_1")
    parsed_result = json.loads(result)

    assert parsed_result["success"] is True
    assert parsed_result["deleted_count"] == 0


def test_special_characters_in_partition_key(memory_tool, mock_cosmos_container):
    """Test handling special characters in partition key."""
    memory_tool._container = mock_cosmos_container

    # Test with special characters that might cause SQL injection issues
    partition_key = "agent_with'quotes"
    result = memory_tool._retrieve_memory(partition_key)

    # Should handle gracefully without SQL syntax errors
    call_args = mock_cosmos_container.query_items.call_args
    query_sql = call_args[1]['query']
    assert "agent_with'quotes" in query_sql


def test_large_content_storage(memory_tool, mock_cosmos_container):
    """Test storing large content objects."""
    memory_tool._container = mock_cosmos_container

    # Create a large content object
    large_content = {
        "messages": [f"Message {i}" for i in range(1000)],
        "metadata": {"type": "conversation", "size": "large"}
    }

    memory_item = {
        "id": "large_memory",
        "agent_id": "agent_1",
        "content": large_content
    }

    result = memory_tool._store_memory(memory_item)

    # Should handle large objects without issues
    parsed_result = json.loads(result)
    assert "id" in parsed_result


def test_unicode_content_handling(memory_tool, mock_cosmos_container):
    """Test handling Unicode content."""
    memory_tool._container = mock_cosmos_container

    unicode_content = {
        "message": "Hello 世界! 🌍 Émojis and ñoñ-ASCII çhäracters",
        "language": "multi"
    }

    memory_item = {
        "id": "unicode_memory",
        "agent_id": "agent_1",
        "content": unicode_content
    }

    result = memory_tool._store_memory(memory_item)
    parsed_result = json.loads(result)

    assert "id" in parsed_result


# Integration-style Tests
def test_complete_memory_lifecycle(memory_tool, mock_cosmos_container):
    """Test complete memory lifecycle: store -> retrieve -> update -> delete."""
    memory_tool._container = mock_cosmos_container

    # Store
    memory_item = {
        "id": "lifecycle_test",
        "agent_id": "agent_1",
        "content": {"message": "Initial memory"}
    }
    store_result = memory_tool._store_memory(memory_item)
    assert "id" in json.loads(store_result)

    # Retrieve
    retrieve_result = memory_tool._retrieve_memory("agent_1")
    assert len(json.loads(retrieve_result)) > 0

    # Update
    update_content = {"content": {"message": "Updated memory"}}
    update_result = memory_tool._update_memory("agent_1", "lifecycle_test", update_content)
    assert "updated_at" in json.loads(update_result)

    # Delete
    delete_result = memory_tool._delete_memory("agent_1", "lifecycle_test")
    assert "deleted" in delete_result


def test_concurrent_operations_simulation(memory_tool, mock_cosmos_container):
    """Test simulation of concurrent operations on same partition."""
    memory_tool._container = mock_cosmos_container

    # Simulate multiple store operations
    for i in range(5):
        memory_item = {
            "id": f"concurrent_{i}",
            "agent_id": "agent_1",
            "content": {"message": f"Concurrent memory {i}"}
        }
        result = memory_tool._store_memory(memory_item)
        assert "id" in json.loads(result)

    # Clear all
    mock_cosmos_container.query_items.return_value = [
        {"id": f"concurrent_{i}"} for i in range(5)
    ]
    clear_result = memory_tool._clear_memory("agent_1")
    parsed_clear = json.loads(clear_result)
    assert parsed_clear["deleted_count"] == 5


# Performance and Resource Tests
def test_memory_tool_resource_cleanup():
    """Test that memory tool properly manages resources."""
    config = AzureCosmosDBMemoryConfig(
        cosmos_host="https://test.documents.azure.com:443/",
        key="test_key"
    )

    with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.COSMOSDB_AVAILABLE", True):
        with patch("crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool.CosmosClient") as mock_client:
            tool = AzureCosmosDBMemoryTool(config=config)

            # Verify connections are established
            assert tool._cosmos_client is not None
            assert tool._database is not None
            assert tool._container is not None

            # Tool should be ready for operations
            assert tool.name == "AzureCosmosDBMemoryTool"
