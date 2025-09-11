import os
import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from crewai_tools.tools.olostep_google_search_tool.olostep_google_search_tool import OlostepGoogleSearchTool

@pytest.fixture
def olostep_search_tool():
    with patch.dict(os.environ, {"OLOSTEP_API_KEY": "test_api_key"}):
        yield OlostepGoogleSearchTool()

def test_tool_initialization_requires_api_key():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OLOSTEP_API_KEY environment variable is required for OlostepGoogleSearchTool."):
            OlostepGoogleSearchTool()

@patch('requests.post')
def test_google_search(mock_post, olostep_search_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_json_content = {"organic": [{"title": "Test Search Result"}]}
    mock_response.json.return_value = {
        "result": {
            "json_content": json.dumps(mock_json_content)
        }
    }
    mock_post.return_value = mock_response

    result = olostep_search_tool._run(search_query="test query")
    
    assert result == mock_json_content
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert "q=test query" in called_kwargs['json']['url_to_scrape']
    assert "&gl=us" in called_kwargs['json']['url_to_scrape']
    assert "&hl=en" in called_kwargs['json']['url_to_scrape']

@patch('requests.post')
def test_google_search_with_location_and_language(mock_post, olostep_search_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_json_content = {"organic": [{"title": "Résultat de recherche test"}]}
    mock_response.json.return_value = {
        "result": {
            "json_content": json.dumps(mock_json_content)
        }
    }
    mock_post.return_value = mock_response

    result = olostep_search_tool._run(search_query="requête de test", location="fr", language="fr")
    
    assert result == mock_json_content
    mock_post.assert_called_once()
    called_args, called_kwargs = mock_post.call_args
    assert "q=requête de test" in called_kwargs['json']['url_to_scrape']
    assert "&gl=fr" in called_kwargs['json']['url_to_scrape']
    assert "&hl=fr" in called_kwargs['json']['url_to_scrape']

@patch('requests.post')
def test_api_timeout(mock_post, olostep_search_tool):
    mock_post.side_effect = requests.Timeout
    result = olostep_search_tool._run(search_query="test")
    assert "Olostep API request timed out." in result

@patch('requests.post')
def test_api_http_error(mock_post, olostep_search_tool):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    http_error = requests.HTTPError(response=mock_response)
    mock_response.raise_for_status.side_effect = http_error
    mock_post.return_value = mock_response
    
    result = olostep_search_tool._run(search_query="test")
    assert "Olostep API request failed with status 500: Internal Server Error" in result

@patch('requests.post')
def test_no_json_content(mock_post, olostep_search_tool):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "result": {
            "json_content": None
        }
    }
    mock_post.return_value = mock_response

    result = olostep_search_tool._run(search_query="test")
    assert "No JSON content found in the response." in result
