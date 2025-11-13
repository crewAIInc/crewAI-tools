import pytest
from unittest.mock import patch, MagicMock
from crewai_tools.tools.keboola_storage_api_tool import utils
from crewai_tools.tools.keboola_storage_api_tool.exceptions import KeboolaAPIError


def test_prepare_keboola_headers():
    token = "abc123"
    headers = utils.prepare_keboola_headers(token)
    assert headers == {"X-StorageApi-Token": token}


@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.get")
def test_fetch_table_columns_success(mock_get):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {"columns": ["col1", "col2"]}
    mock_get.return_value = mock_response

    result = utils.fetch_table_columns("in.c-bucket.table", "token", "https://connection.keboola.com")
    assert result == ["col1", "col2"]


@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.get")
def test_fetch_table_columns_failure(mock_get):
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.text = "Access Denied"
    mock_get.return_value = mock_response

    with pytest.raises(KeboolaAPIError, match="Failed to fetch table columns: Access Denied"):
        utils.fetch_table_columns("in.c-bucket.table", "token", "https://connection.keboola.com")


@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.post")
@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.get")
def test_start_and_poll_export_job_success(mock_get, mock_post):
    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_post_response.json.return_value = {"id": "job-123"}
    mock_post.return_value = mock_post_response

    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {
        "status": "success",
        "results": {"file": {"id": "file-456"}}
    }
    mock_get.return_value = mock_get_response

    file_id = utils.start_and_poll_export_job("in.c-bucket.table", "token", "https://connection.keboola.com")
    assert file_id == "file-456"


@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.post")
def test_start_and_poll_export_job_start_failure(mock_post):
    mock_post_response = MagicMock()
    mock_post_response.ok = False
    mock_post_response.text = "Invalid Token"
    mock_post.return_value = mock_post_response

    with pytest.raises(KeboolaAPIError, match="Failed to start export job: Invalid Token"):
        utils.start_and_poll_export_job("in.c-bucket.table", "token", "https://connection.keboola.com")


@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.post")
@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.get")
def test_start_and_poll_export_job_failure_status(mock_get, mock_post):
    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_post_response.json.return_value = {"id": "job-123"}
    mock_post.return_value = mock_post_response

    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {"status": "error"}
    mock_get.return_value = mock_get_response

    with pytest.raises(KeboolaAPIError, match="Export job failed:"):
        utils.start_and_poll_export_job("in.c-bucket.table", "token", "https://connection.keboola.com")


@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.post")
@patch("crewai_tools.tools.keboola_storage_api_tool.utils.requests.get")
def test_start_and_poll_export_job_timeout(mock_get, mock_post):
    utils.config.max_poll_attempts = 2
    utils.config.poll_interval_seconds = 0.01

    mock_post_response = MagicMock()
    mock_post_response.ok = True
    mock_post_response.json.return_value = {"id": "job-123"}
    mock_post.return_value = mock_post_response

    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {"status": "waiting"}
    mock_get.return_value = mock_get_response

    with pytest.raises(TimeoutError, match="Export job did not complete in time."):
        utils.start_and_poll_export_job("in.c-bucket.table", "token", "https://connection.keboola.com")
