from unittest.mock import MagicMock, patch

import pytest

from crewai_tools import MongoDBVectorSearchConfig, MongoDBVectorSearchTool


# Unit Test Fixtures
@pytest.fixture
def mongodb_vector_search_tool():
    tool = MongoDBVectorSearchTool(
        connection_string="foo", database_name="bar", collection_name="test"
    )
    yield tool


class MockEmbeddingData:
    @property
    def embedding(self):
        return [[0.1]]


# Unit Tests
def test_successful_query_execution(mongodb_vector_search_tool):
    with patch.object(
        mongodb_vector_search_tool._openai_client.embeddings, "create"
    ) as mock_create_embedding, patch.object(
        mongodb_vector_search_tool._collection, "aggregate"
    ) as mock_aggregate:
        mock_result = MagicMock()
        mock_result.data = [MockEmbeddingData()]
        mock_create_embedding.return_value = mock_result
        mock_aggregate.return_value = [dict(text="foo", score=0.1, _id=1)]

        results = mongodb_vector_search_tool._run(query="sandwiches")

        assert len(results) == 1
        assert results[0]["context"] == "foo"
        assert results[0]["id"] == 1


def test_provide_config():
    query_config = MongoDBVectorSearchConfig(limit=10)
    tool = MongoDBVectorSearchTool(
        connection_string="foo",
        database_name="bar",
        collection_name="test",
        query_config=query_config,
        index_name="foo",
        embedding_model="bar",
    )
    with patch.object(
        tool._openai_client.embeddings, "create"
    ) as mock_create_embedding, patch.object(
        tool._collection, "aggregate"
    ) as mock_aggregate:
        mock_result = MagicMock()
        mock_result.data = [MockEmbeddingData()]
        mock_create_embedding.return_value = mock_result
        mock_aggregate.return_value = [dict(text="foo", score=0.1, _id=1)]

        tool._run(query="sandwiches")
        assert mock_aggregate.mock_calls[-1].args[0][0]["$vectorSearch"]["limit"] == 10

        mock_aggregate.return_value = [dict(text="foo", score=0.1, _id=1)]
        tool._run(query="sandwiches", limit=5)
        assert mock_aggregate.mock_calls[-1].args[0][0]["$vectorSearch"]["limit"] == 5


def test_cleanup_on_deletion(mongodb_vector_search_tool):
    with patch.object(
        mongodb_vector_search_tool, "_client"
    ) as mock_client, patch.object(
        mongodb_vector_search_tool, "_openai_client"
    ) as mock_openai_client:
        # Trigger cleanup
        mongodb_vector_search_tool.__del__()

        mock_client.close.assert_called_once()
        mock_openai_client.close.assert_called_once()
