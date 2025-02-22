import asyncio
from unittest.mock import MagicMock, patch

import pytest

from crewai_tools import SnowflakeConfig, SnowflakeSearchTool


# Unit Test Fixtures
@pytest.fixture
def mock_snowflake_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("col1",), ("col2",)]
    mock_cursor.fetchall.return_value = [(1, "value1"), (2, "value2")]
    mock_cursor.execute.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


@pytest.fixture
def mock_config():
    return SnowflakeConfig(
        account="test_account",
        user="test_user",
        password="test_password",
        warehouse="test_warehouse",
        database="test_db",
        snowflake_schema="test_schema",
    )


@pytest.fixture
def snowflake_tool(mock_config):
    with patch("snowflake.connector.connect") as mock_connect:
        tool = SnowflakeSearchTool(config=mock_config)
        yield tool


@pytest.fixture
def clear_cache():
    # Clear the cache before and after each test
    from crewai_tools.tools.snowflake_search_tool.snowflake_search_tool import (
        _query_cache,
    )

    _query_cache.clear()
    yield
    _query_cache.clear()


# Unit Tests
@pytest.mark.asyncio
async def test_successful_query_execution(snowflake_tool, mock_snowflake_connection):
    with patch.object(snowflake_tool, "_create_connection") as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        results = await snowflake_tool._run(
            query="SELECT * FROM test_table", timeout=300
        )

        assert len(results) == 2
        assert results[0]["col1"] == 1
        assert results[0]["col2"] == "value1"
        mock_snowflake_connection.cursor.assert_called_once()


@pytest.mark.asyncio
async def test_query_caching(snowflake_tool, mock_snowflake_connection, clear_cache):
    with patch.object(snowflake_tool, "_create_connection") as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        # First query execution
        results1 = await snowflake_tool._run(
            query="SELECT * FROM test_table", timeout=300
        )

        # Second execution of the same query
        results2 = await snowflake_tool._run(
            query="SELECT * FROM test_table", timeout=300
        )

        # Different query
        results3 = await snowflake_tool._run(
            query="SELECT * FROM different_table", timeout=300
        )

        # Verify results are the same for cached query
        assert results1 == results2

        # Verify cursor.execute was called only twice (once for first query, once for different query)
        assert mock_snowflake_connection.cursor.call_count == 2

        # Verify cache behavior with different parameters
        results4 = await snowflake_tool._run(
            query="SELECT * FROM test_table", timeout=600  # Different timeout
        )

        # Should trigger new query due to different cache key
        assert mock_snowflake_connection.cursor.call_count == 3


@pytest.mark.asyncio
async def test_cache_size_limit(snowflake_tool, mock_snowflake_connection, clear_cache):
    with patch.object(snowflake_tool, "_create_connection") as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        # Execute queries up to cache size limit + 1
        from crewai_tools.tools.snowflake_search_tool.snowflake_search_tool import (
            CACHE_SIZE,
            _query_cache,
        )

        for i in range(CACHE_SIZE + 1):
            await snowflake_tool._run(query=f"SELECT * FROM table_{i}", timeout=300)

        # First query should have been evicted
        first_query_key = snowflake_tool._get_cache_key("SELECT * FROM table_0", 300)
        assert first_query_key not in _query_cache

        # Second query should appear
        second_query_key = snowflake_tool._get_cache_key("SELECT * FROM table_1", 300)
        assert second_query_key in _query_cache


@pytest.mark.asyncio
async def test_connection_pooling(snowflake_tool, mock_snowflake_connection):
    with patch.object(snowflake_tool, "_create_connection") as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        # Execute multiple queries
        await asyncio.gather(
            snowflake_tool._run("SELECT 1"),
            snowflake_tool._run("SELECT 2"),
            snowflake_tool._run("SELECT 3"),
        )

        # Should reuse connections from pool
        assert mock_create_conn.call_count <= snowflake_tool.pool_size


@pytest.mark.asyncio
async def test_cleanup_on_deletion(snowflake_tool, mock_snowflake_connection):
    with patch.object(snowflake_tool, "_create_connection") as mock_create_conn:
        mock_create_conn.return_value = mock_snowflake_connection

        # Add connection to pool
        await snowflake_tool._get_connection()

        # Return connection to pool
        async with snowflake_tool._pool_lock:
            snowflake_tool._connection_pool.append(mock_snowflake_connection)

        # Trigger cleanup
        snowflake_tool.__del__()

        mock_snowflake_connection.close.assert_called_once()


def test_config_validation():
    # Test missing required fields
    with pytest.raises(ValueError):
        SnowflakeConfig()

    # Test invalid account format
    with pytest.raises(ValueError):
        SnowflakeConfig(
            account="invalid//account", user="test_user", password="test_pass"
        )

    # Test missing authentication
    with pytest.raises(ValueError):
        SnowflakeConfig(account="test_account", user="test_user")
