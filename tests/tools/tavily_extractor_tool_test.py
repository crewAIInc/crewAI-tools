from unittest.mock import patch, Mock, AsyncMock
import pytest
from crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool import TavilyExtractorTool
import os
import json


@pytest.fixture
def mock_tavily_extract_response():
    return {
        "results": [
            {
                "url": "https://example.com/1",
                "content": "Extracted content from page 1",
                "title": "Page 1 Title",
                "images": []
            },
            {
                "url": "https://example.com/2", 
                "content": "Extracted content from page 2",
                "title": "Page 2 Title",
                "images": ["https://example.com/image1.jpg"]
            }
        ]
    }


@pytest.fixture
def tavily_extractor_tool():
    return TavilyExtractorTool(api_key="test_api_key")


@patch("crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool.TavilyClient")
@patch("crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool.AsyncTavilyClient")
def test_tavily_extractor_tool_initialization(mock_async_client, mock_client):
    tool = TavilyExtractorTool(api_key="test_key")
    assert tool.name == "TavilyExtractorTool"
    assert "Extracts content from one or more web pages" in tool.description
    assert tool.include_images is False
    assert tool.extract_depth == "basic"
    assert tool.timeout == 60


def test_tavily_extractor_tool_custom_initialization():
    tool = TavilyExtractorTool(
        api_key="custom_key",
        proxies={"http": "http://proxy:8080"}
    )
    assert tool.api_key == "custom_key"
    assert tool.proxies == {"http": "http://proxy:8080"}


@patch.dict(os.environ, {"TAVILY_API_KEY": "env_api_key"})
def test_tavily_extractor_tool_env_api_key():
    tool = TavilyExtractorTool()
    assert tool.api_key == "env_api_key"


@patch("crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool.TavilyClient")
def test_tavily_extractor_tool_run_single_url(mock_tavily_client, tavily_extractor_tool, mock_tavily_extract_response):
    mock_client_instance = Mock()
    mock_client_instance.extract.return_value = mock_tavily_extract_response
    mock_tavily_client.return_value = mock_client_instance
    tavily_extractor_tool.client = mock_client_instance
    
    result = tavily_extractor_tool._run("https://example.com/1")
    
    mock_client_instance.extract.assert_called_once_with(
        urls="https://example.com/1",
        extract_depth="basic",
        include_images=False,
        timeout=60
    )
    
    result_dict = json.loads(result)
    assert len(result_dict["results"]) == 2
    assert result_dict["results"][0]["url"] == "https://example.com/1"
    assert result_dict["results"][0]["content"] == "Extracted content from page 1"


@patch("crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool.TavilyClient")
def test_tavily_extractor_tool_run_multiple_urls(mock_tavily_client, tavily_extractor_tool, mock_tavily_extract_response):
    mock_client_instance = Mock()
    mock_client_instance.extract.return_value = mock_tavily_extract_response
    mock_tavily_client.return_value = mock_client_instance
    tavily_extractor_tool.client = mock_client_instance
    
    urls = ["https://example.com/1", "https://example.com/2"]
    result = tavily_extractor_tool._run(urls)
    
    mock_client_instance.extract.assert_called_once_with(
        urls=urls,
        extract_depth="basic",
        include_images=False,
        timeout=60
    )
    
    result_dict = json.loads(result)
    assert len(result_dict["results"]) == 2


@patch("crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool.TavilyClient")
def test_tavily_extractor_tool_run_with_images(mock_tavily_client, mock_tavily_extract_response):
    tool = TavilyExtractorTool(api_key="test_key", include_images=True)
    mock_client_instance = Mock()
    mock_client_instance.extract.return_value = mock_tavily_extract_response
    mock_tavily_client.return_value = mock_client_instance
    tool.client = mock_client_instance
    
    result = tool._run("https://example.com/1")
    
    mock_client_instance.extract.assert_called_once_with(
        urls="https://example.com/1",
        extract_depth="basic",
        include_images=True,
        timeout=60
    )
    
    result_dict = json.loads(result)
    assert result_dict["results"][1]["images"] == ["https://example.com/image1.jpg"]


@patch("crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool.AsyncTavilyClient")
@pytest.mark.asyncio
async def test_tavily_extractor_tool_arun(mock_async_tavily_client, tavily_extractor_tool, mock_tavily_extract_response):
    mock_async_client_instance = AsyncMock()
    mock_async_client_instance.extract.return_value = mock_tavily_extract_response
    mock_async_tavily_client.return_value = mock_async_client_instance
    tavily_extractor_tool.async_client = mock_async_client_instance
    
    result = await tavily_extractor_tool._arun("https://example.com/1")
    
    mock_async_client_instance.extract.assert_called_once_with(
        urls="https://example.com/1",
        extract_depth="basic",
        include_images=False,
        timeout=60
    )
    
    result_dict = json.loads(result)
    assert len(result_dict["results"]) == 2


def test_tavily_extractor_tool_no_client_error(tavily_extractor_tool):
    tavily_extractor_tool.client = None
    
    with pytest.raises(ValueError, match="Tavily client is not initialized"):
        tavily_extractor_tool._run("https://example.com")


@pytest.mark.asyncio
async def test_tavily_extractor_tool_no_async_client_error(tavily_extractor_tool):
    tavily_extractor_tool.async_client = None
    
    with pytest.raises(ValueError, match="Tavily async client is not initialized"):
        await tavily_extractor_tool._arun("https://example.com")


def test_tavily_extractor_tool_schema_validation():
    from crewai_tools.tools.tavily_extractor_tool.tavily_extractor_tool import TavilyExtractorToolSchema
    
    schema = TavilyExtractorToolSchema(urls="https://example.com")
    assert schema.urls == "https://example.com"
    
    urls_list = ["https://example.com/1", "https://example.com/2"]
    schema = TavilyExtractorToolSchema(urls=urls_list)
    assert schema.urls == urls_list
