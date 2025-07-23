from unittest.mock import patch, Mock, AsyncMock
import pytest
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool
import os
import json


@pytest.fixture
def mock_tavily_response():
    return {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "This is test content for result 1",
                "score": 0.95
            },
            {
                "title": "Test Result 2", 
                "url": "https://example.com/2",
                "content": "This is test content for result 2",
                "score": 0.87
            }
        ]
    }


@pytest.fixture
def tavily_search_tool():
    return TavilySearchTool(api_key="test_api_key")


@patch("crewai_tools.tools.tavily_search_tool.tavily_search_tool.TavilyClient")
@patch("crewai_tools.tools.tavily_search_tool.tavily_search_tool.AsyncTavilyClient")
def test_tavily_search_tool_initialization(mock_async_client, mock_client):
    tool = TavilySearchTool(api_key="test_key")
    assert tool.name == "Tavily Search"
    assert tool.search_depth == "basic"
    assert tool.topic == "general"
    assert tool.max_results == 5
    assert tool.include_answer is False
    assert tool.include_raw_content is False
    assert tool.include_images is False


def test_tavily_search_tool_custom_initialization():
    tool = TavilySearchTool(
        api_key="custom_key",
        search_depth="advanced",
        topic="news",
        max_results=10,
        include_answer=True,
        include_raw_content=True,
        include_images=True
    )
    assert tool.api_key == "custom_key"
    assert tool.search_depth == "advanced"
    assert tool.topic == "news"
    assert tool.max_results == 10
    assert tool.include_answer is True
    assert tool.include_raw_content is True
    assert tool.include_images is True


@patch.dict(os.environ, {"TAVILY_API_KEY": "env_api_key"})
def test_tavily_search_tool_env_api_key():
    tool = TavilySearchTool()
    assert tool.api_key == "env_api_key"


@patch("crewai_tools.tools.tavily_search_tool.tavily_search_tool.TavilyClient")
def test_tavily_search_tool_run(mock_tavily_client, tavily_search_tool, mock_tavily_response):
    mock_client_instance = Mock()
    mock_client_instance.search.return_value = mock_tavily_response
    mock_tavily_client.return_value = mock_client_instance
    tavily_search_tool.client = mock_client_instance
    
    result = tavily_search_tool._run("test query")
    
    mock_client_instance.search.assert_called_once_with(
        query="test query",
        search_depth="basic",
        topic="general",
        time_range=None,
        days=7,
        max_results=5,
        include_domains=None,
        exclude_domains=None,
        include_answer=False,
        include_raw_content=False,
        include_images=False,
        timeout=60
    )
    
    result_dict = json.loads(result)
    assert result_dict["query"] == "test query"
    assert len(result_dict["results"]) == 2
    assert result_dict["results"][0]["title"] == "Test Result 1"


@patch("crewai_tools.tools.tavily_search_tool.tavily_search_tool.AsyncTavilyClient")
@pytest.mark.asyncio
async def test_tavily_search_tool_arun(mock_async_tavily_client, tavily_search_tool, mock_tavily_response):
    mock_async_client_instance = AsyncMock()
    mock_async_client_instance.search.return_value = mock_tavily_response
    mock_async_tavily_client.return_value = mock_async_client_instance
    tavily_search_tool.async_client = mock_async_client_instance
    
    result = await tavily_search_tool._arun("test query")
    
    mock_async_client_instance.search.assert_called_once_with(
        query="test query",
        search_depth="basic",
        topic="general",
        time_range=None,
        days=7,
        max_results=5,
        include_domains=None,
        exclude_domains=None,
        include_answer=False,
        include_raw_content=False,
        include_images=False,
        timeout=60
    )
    
    result_dict = json.loads(result)
    assert result_dict["query"] == "test query"
    assert len(result_dict["results"]) == 2


def test_tavily_search_tool_content_truncation(tavily_search_tool):
    long_content_response = {
        "query": "test query",
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "content": "x" * 1500,  # Content longer than max_content_length_per_result (1000)
                "score": 0.95
            }
        ]
    }
    
    with patch.object(tavily_search_tool, 'client') as mock_client:
        mock_client.search.return_value = long_content_response
        
        result = tavily_search_tool._run("test query")
        result_dict = json.loads(result)
        
        assert len(result_dict["results"][0]["content"]) == 1003  # 1000 + "..."
        assert result_dict["results"][0]["content"].endswith("...")


def test_tavily_search_tool_no_client_error(tavily_search_tool):
    tavily_search_tool.client = None
    
    with pytest.raises(ValueError, match="Tavily client is not initialized"):
        tavily_search_tool._run("test query")


@pytest.mark.asyncio
async def test_tavily_search_tool_no_async_client_error(tavily_search_tool):
    tavily_search_tool.async_client = None
    
    with pytest.raises(ValueError, match="Tavily async client is not initialized"):
        await tavily_search_tool._arun("test query")
