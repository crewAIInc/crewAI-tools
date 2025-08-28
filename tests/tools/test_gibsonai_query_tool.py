import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from crewai_tools.tools.gibsonai_query_tool.gibsonai_query_tool import GibsonAIQueryTool


@pytest.fixture
def mock_requests():
    with patch(
        "crewai_tools.tools.gibsonai_query_tool.gibsonai_query_tool.requests"
    ) as mock:
        yield mock


@pytest.fixture
def tool():
    return GibsonAIQueryTool(api_key="test_api_key")


def test_tool_initialization():
    """Test tool initialization with API key."""
    tool = GibsonAIQueryTool(api_key="test_key")
    assert tool._api_key == "test_key"
    assert tool._api_base_url == "https://api.gibsonai.com/v1/-"


def test_tool_initialization_without_api_key():
    """Test tool initialization without API key raises ValueError."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="Missing GIBSONAI_API_KEY"):
            GibsonAIQueryTool()


def test_tool_initialization_with_env_var():
    """Test tool initialization using environment variable."""
    with patch.dict("os.environ", {"GIBSONAI_API_KEY": "env_key"}):
        tool = GibsonAIQueryTool()
        assert tool._api_key == "env_key"


def test_successful_select_query(tool, mock_requests):
    """Test successful SELECT query execution."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        ]
    }
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM users")

    assert "Query executed successfully" in result
    assert "Retrieved 2 row(s)" in result
    assert "John Doe" in result
    assert "Jane Smith" in result

    mock_requests.post.assert_called_once_with(
        "https://api.gibsonai.com/v1/-/query",
        json={"query": "SELECT * FROM users"},
        headers={
            "X-Gibson-API-Key": "test_api_key",
            "Content-Type": "application/json",
        },
        timeout=30,
    )


def test_successful_insert_query(tool, mock_requests):
    """Test successful INSERT query execution."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"affected_rows": 1}
    mock_requests.post.return_value = mock_response

    result = tool._run(
        query="INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com')"
    )

    assert "INSERT query executed successfully" in result
    assert "1 row(s) affected" in result


def test_successful_update_query(tool, mock_requests):
    """Test successful UPDATE query execution."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rowsAffected": 3}
    mock_requests.post.return_value = mock_response

    result = tool._run(
        query="UPDATE users SET status = 'active' WHERE created_at > '2023-01-01'"
    )

    assert "UPDATE query executed successfully" in result
    assert "3 row(s) affected" in result


def test_successful_delete_query(tool, mock_requests):
    """Test successful DELETE query execution."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"affected_rows": 5}
    mock_requests.post.return_value = mock_response

    result = tool._run(query="DELETE FROM old_records WHERE created_at < '2020-01-01'")

    assert "DELETE query executed successfully" in result
    assert "5 row(s) affected" in result


def test_parameterized_query(tool, mock_requests):
    """Test parameterized query execution."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"id": 1, "name": "John Doe"}]}
    mock_requests.post.return_value = mock_response

    parameters = {"name": "John Doe", "email": "john@example.com"}
    result = tool._run(
        query="SELECT * FROM users WHERE name = ? AND email = ?", parameters=parameters
    )

    assert "Query executed successfully" in result
    mock_requests.post.assert_called_once_with(
        "https://api.gibsonai.com/v1/-/query",
        json={
            "query": "SELECT * FROM users WHERE name = ? AND email = ?",
            "parameters": parameters,
        },
        headers={
            "X-Gibson-API-Key": "test_api_key",
            "Content-Type": "application/json",
        },
        timeout=30,
    )


def test_empty_select_result(tool, mock_requests):
    """Test SELECT query with no results."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM users WHERE id = 999")

    assert "Query executed successfully" in result
    assert "No rows returned" in result


def test_bad_request_error(tool, mock_requests):
    """Test handling of 400 Bad Request error."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Invalid SQL syntax"}
    mock_requests.post.return_value = mock_response

    result = tool._run(query="INVALID SQL QUERY")

    assert "Error: Invalid query" in result
    assert "Invalid SQL syntax" in result


def test_unauthorized_error(tool, mock_requests):
    """Test handling of 401 Unauthorized error."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Unauthorized" in result
    assert "check your GIBSONAI_API_KEY" in result


def test_forbidden_error(tool, mock_requests):
    """Test handling of 403 Forbidden error."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_requests.post.return_value = mock_response

    result = tool._run(query="DROP TABLE important_data")

    assert "Error: Forbidden" in result
    assert "Insufficient permissions" in result


def test_not_found_error(tool, mock_requests):
    """Test handling of 404 Not Found error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM non_existent_table")

    assert "Error: Not found" in result


def test_server_error(tool, mock_requests):
    """Test handling of 500 Internal Server Error."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Internal server error" in result
    assert "try again later" in result


def test_unexpected_status_code(tool, mock_requests):
    """Test handling of unexpected status codes."""
    mock_response = MagicMock()
    mock_response.status_code = 418
    mock_response.text = "I'm a teapot"
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Unexpected response (Status 418)" in result
    assert "I'm a teapot" in result


def test_timeout_error(tool, mock_requests):
    """Test handling of timeout errors."""
    mock_requests.post.side_effect = requests.exceptions.Timeout()

    result = tool._run(query="SELECT * FROM large_table")

    assert "Error: Request timeout" in result
    assert "took too long to execute" in result


def test_connection_error(tool, mock_requests):
    """Test handling of connection errors."""
    mock_requests.post.side_effect = requests.exceptions.ConnectionError()

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Connection failed" in result
    assert "Unable to reach GibsonAI API" in result


def test_request_exception(tool, mock_requests):
    """Test handling of general request exceptions."""
    mock_requests.post.side_effect = requests.exceptions.RequestException(
        "Network error"
    )

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Request failed" in result
    assert "Network error" in result


def test_json_decode_error(tool, mock_requests):
    """Test handling of invalid JSON responses."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_requests.post.return_value = mock_response

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Invalid JSON response from API" in result


def test_unexpected_exception(tool, mock_requests):
    """Test handling of unexpected exceptions."""
    mock_requests.post.side_effect = Exception("Unexpected error")

    result = tool._run(query="SELECT * FROM users")

    assert "Error: Unexpected error occurred" in result
    assert "Unexpected error" in result


def test_query_whitespace_handling(tool, mock_requests):
    """Test that query whitespace is properly handled."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}
    mock_requests.post.return_value = mock_response

    tool._run(query="  SELECT * FROM users  ")

    mock_requests.post.assert_called_once()
    call_args = mock_requests.post.call_args
    assert call_args[1]["json"]["query"] == "SELECT * FROM users"


def test_format_response_fallback(tool):
    """Test format response fallback when parsing fails."""
    result_data = {"unexpected": "format", "data": "value"}

    formatted = tool._format_response("SELECT * FROM users", result_data)

    assert "Query executed successfully" in formatted
    assert "Result: value" in formatted
