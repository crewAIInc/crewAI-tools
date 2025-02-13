from unittest.mock import MagicMock, patch

import pytest
from elasticsearch import AsyncElasticsearch
from pydantic import SecretStr

from crewai_tools import ElasticsearchConfig, ElasticsearchSearchTool

# Mock Response Data
MOCK_SEARCH_RESPONSE = {
    "hits": {
        "total": {"value": 2, "relation": "eq"},
        "hits": [
            {
                "_index": "test_index",
                "_id": "1",
                "_score": 1.0,
                "_source": {"field1": "value1", "field2": 1},
            },
            {
                "_index": "test_index",
                "_id": "2",
                "_score": 0.8,
                "_source": {"field1": "value2", "field2": 2},
            },
        ],
    }
}


# Unit Test Fixtures
@pytest.fixture
def mock_elasticsearch_client():
    async def mock_search(*args, **kwargs):
        return MOCK_SEARCH_RESPONSE

    async def mock_close():
        return None

    mock_client = MagicMock(spec=AsyncElasticsearch)
    mock_client.search = mock_search
    mock_client.close = mock_close
    return mock_client


@pytest.fixture
def mock_config():
    return ElasticsearchConfig(
        hosts=["http://localhost:9200"],
        username="test_user",
        password=SecretStr("test_password"),
        default_index="test_index",
    )


@pytest.fixture
def elasticsearch_tool(mock_config, mock_elasticsearch_client):
    with patch(
        "elasticsearch.AsyncElasticsearch", return_value=mock_elasticsearch_client
    ):
        tool = ElasticsearchSearchTool(config=mock_config)
        tool._client = mock_elasticsearch_client
        yield tool


# Unit Tests
@pytest.mark.asyncio
async def test_successful_query_execution(elasticsearch_tool):
    results = await elasticsearch_tool._run(
        query='{"query": {"match": {"field1": "test"}}}', index="test_index", size=10
    )

    assert results == MOCK_SEARCH_RESPONSE


@pytest.mark.asyncio
async def test_query_string_fallback(elasticsearch_tool):
    results = await elasticsearch_tool._run(query="field1:test", index="test_index")

    assert results == MOCK_SEARCH_RESPONSE


@pytest.mark.asyncio
async def test_search_with_routing(elasticsearch_tool):
    results = await elasticsearch_tool._run(
        query="test query", index="test_index", routing="user123"
    )

    assert results == MOCK_SEARCH_RESPONSE


@pytest.mark.asyncio
async def test_result_caching(elasticsearch_tool):
    elasticsearch_tool.enable_caching = True

    # First call
    results1 = await elasticsearch_tool._run(query="test query", index="test_index")

    # Second call with same parameters
    results2 = await elasticsearch_tool._run(query="test query", index="test_index")

    assert results1 == results2


@pytest.mark.asyncio
async def test_cleanup_on_exit(elasticsearch_tool):
    close_called = False

    async def mock_close():
        nonlocal close_called
        close_called = True

    elasticsearch_tool._client.close = mock_close

    async with elasticsearch_tool as tool:
        await tool._run("test query")

    assert close_called


def test_config_validation():
    # Test missing required fields
    with pytest.raises(ValueError):
        ElasticsearchConfig()

    # Test missing both hosts and cloud_id
    with pytest.raises(ValueError):
        ElasticsearchConfig(username="test_user", password=SecretStr("test_pass"))

    # Test valid cloud_id only configuration
    config = ElasticsearchConfig(
        hosts=["http://localhost:9200"],  # hosts is required even with cloud_id
        cloud_id="test:dGVzdA==",
        api_key=SecretStr("test_api_key"),
    )
    assert config.has_auth is True

    # Test valid hosts configuration
    config = ElasticsearchConfig(
        hosts=["http://localhost:9200"],
        username="test_user",
        password=SecretStr("test_pass"),
    )
    assert config.has_auth is True


@pytest.mark.asyncio
async def test_missing_index_handling(elasticsearch_tool):
    elasticsearch_tool.config.default_index = None

    with pytest.raises(ValueError, match="No index specified"):
        await elasticsearch_tool._run(query="test query")
