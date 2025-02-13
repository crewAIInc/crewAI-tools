"""Tests for the Databricks Tool."""
import os
import pytest
from unittest.mock import MagicMock, patch
from crewai_tools.tools.databricks_tool import query_databricks

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables."""
    os.environ["DATABRICKS_HOST"] = "test-host"
    os.environ["DATABRICKS_HTTP_PATH"] = "test-path"
    os.environ["DATABRICKS_TOKEN"] = "test-token"
    yield
    del os.environ["DATABRICKS_HOST"]
    del os.environ["DATABRICKS_HTTP_PATH"]
    del os.environ["DATABRICKS_TOKEN"]

@pytest.fixture
def mock_cursor():
    """Create a mock cursor."""
    cursor = MagicMock()
    cursor.description = [("col1",), ("col2",)]
    cursor.fetchall.return_value = [(1, "a"), (2, "b")]
    return cursor

@pytest.fixture
def mock_connection(mock_cursor):
    """Create a mock connection."""
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = mock_cursor
    return conn

def test_query_databricks_missing_env_vars():
    """Test handling of missing environment variables."""
    result = query_databricks("SELECT * FROM test")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Missing required environment variables" in str(result.get("error", ""))

@patch("databricks.sql.connect")
def test_query_databricks_successful_query(mock_connect, mock_env_vars, mock_connection):
    """Test successful query execution."""
    mock_connect.return_value = mock_connection
    
    result = query_databricks("SELECT * FROM test")
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"col1": 1, "col2": "a"}
    assert result[1] == {"col1": 2, "col2": "b"}
    mock_connect.assert_called_once()

@patch("databricks.sql.connect")
def test_query_databricks_sql_error(mock_connect, mock_env_vars):
    """Test handling of SQL errors."""
    mock_connect.side_effect = Exception("Test error")
    
    result = query_databricks("SELECT * FROM test")
    
    assert isinstance(result, dict)
    assert "error" in result
    assert "Test error" in str(result.get("error", ""))
