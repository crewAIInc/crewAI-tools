from unittest.mock import MagicMock, patch

import pytest

from crewai_tools import MongoDBVectorSearchTool


# Unit Test Fixtures
@pytest.fixture
def mock_mongodb_client():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("col1",), ("col2",)]
    mock_cursor.fetchall.return_value = [(1, "value1"), (2, "value2")]
    mock_cursor.execute.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


@pytest.fixture
def mongodb_vector_search_tool():
    with patch("snowflake.connector.connect") as mock_connect:
        tool = MongoDBVectorSearchTool(
            connection_string="foo", database_name="bar", collection_name="test"
        )
        yield tool


# Unit Tests
@pytest.mark.asyncio
async def test_successful_query_execution(
    mongodb_vector_search_tool, mock_mongodb_client
):
    with patch.object(
        mongodb_vector_search_tool, "_create_connection"
    ) as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        results = await snowflake_tool._run(
            query="SELECT * FROM test_table", timeout=300
        )

        assert len(results) == 2
        assert results[0]["col1"] == 1
        assert results[0]["col2"] == "value1"
        mock_snowflake_connection.cursor.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_on_deletion(mongodb_vector_search_tool, mock_mongodb_client):
    with patch.object(
        mongodb_vector_search_tool, "_create_connection"
    ) as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        # Add connection to pool
        await mongodb_vector_search_tool._get_connection()

        # Return connection to pool
        async with mongodb_vector_search_tool._pool_lock:
            mongodb_vector_search_tool._connection_pool.append(mock_mongodb_client)

        # Trigger cleanup
        mongodb_vector_search_tool.__del__()

        mock_mongodb_client.close.assert_called_once()
