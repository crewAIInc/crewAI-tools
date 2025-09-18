import os
import pytest
import requests
from unittest.mock import patch, MagicMock
from crewai_tools.tools.olostep_web_scraper_tool.olostep_web_scraper_tool import OlostepWebScraperTool

@pytest.fixture
def olostep_tool():
    with patch.dict(os.environ, {"OLOSTEP_API_KEY": "test_api_key"}):
        yield OlostepWebScraperTool()

def test_tool_initialization_requires_api_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OLOSTEP_API_KEY environment variable is required for OlostepWebScraperTool."):
            OlostepWebScraperTool()

@patch('requests.post')
def test_scrape_with_markdown_format(mock_post, olostep_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "result": {
            "markdown_content": "This is a test markdown content."
        }
    }
    mock_post.return_value = mock_response

    result = olostep_tool._run(url_to_scrape="https://example.com", formats=["markdown"])
    
    assert "Markdown Content:\nThis is a test markdown content." in result
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_kwargs['json']['formats'] == ['markdown']


@patch('requests.post')
def test_scrape_with_html_format(mock_post, olostep_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "result": {
            "html_content": "<h1>Test HTML</h1>"
        }
    }
    mock_post.return_value = mock_response

    result = olostep_tool._run(url_to_scrape="https://example.com", formats=["html"])
    
    assert "HTML Content:\n<h1>Test HTML</h1>" in result
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_kwargs['json']['formats'] == ['html']

@patch('requests.post')
def test_scrape_with_both_formats(mock_post, olostep_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "result": {
            "markdown_content": "Test Markdown.",
            "html_content": "<h1>Test HTML</h1>"
        }
    }
    mock_post.return_value = mock_response

    result = olostep_tool._run(url_to_scrape="https://example.com", formats=["markdown", "html"])
    
    assert "Markdown Content:\nTest Markdown." in result
    assert "HTML Content:\n<h1>Test HTML</h1>" in result
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_kwargs['json']['formats'] == ['markdown', 'html']


@patch('requests.post')
def test_scrape_with_default_format(mock_post, olostep_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "result": {
            "markdown_content": "Default markdown content."
        }
    }
    mock_post.return_value = mock_response

    result = olostep_tool._run(url_to_scrape="https://example.com")
    
    assert "Markdown Content:\nDefault markdown content." in result
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_kwargs['json']['formats'] == ['markdown']

@patch('requests.post')
def test_api_timeout(mock_post, olostep_tool):
    mock_post.side_effect = requests.Timeout
    result = olostep_tool._run(url_to_scrape="https://example.com")
    assert "Olostep API request timed out." in result

@patch('requests.post')
def test_api_http_error(mock_post, olostep_tool):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    http_error = requests.HTTPError(response=mock_response)
    mock_response.raise_for_status.side_effect = http_error
    mock_post.return_value = mock_response
    
    result = olostep_tool._run(url_to_scrape="https://example.com")
    assert "Olostep API request failed with status 400: Bad Request" in result
