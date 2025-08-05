import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool import AzureCosmosDBNoSqlSearchTool, AzureCosmosDBNoSqlSearchConfig

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


# Unit Test Fixtures
@pytest.fixture
def mock_config():
    return AzureCosmosDBNoSqlSearchConfig(
        max_results=5,
        with_embedding=False,
        threshold=0.5,
    )


@pytest.fixture
def mock_cosmos_container():
    """Mock CosmosDB container for testing."""
    mock_container = MagicMock()
    mock_container.query_items.return_value = [
        {
            "id": "1",
            "text": "Sample document about Azure AI",
            "SimilarityScore": 0.8,
            "metadata": {"category": "AI"}
        },
        {
            "id": "2",
            "text": "Another document about machine learning",
            "SimilarityScore": 0.7,
            "metadata": {"category": "ML"}
        }
    ]
    return mock_container


@pytest.fixture
def cosmosdb_tool():
    """Create a CosmosDB tool instance with mocked dependencies."""
    with patch("crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool.COSMOSDB_AVAILABLE", True):
        with patch("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool.Client") as mock_client:
                with patch("crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool.CosmosClient") as mock_cosmos_client:
                    # Mock OpenAI client
                    mock_openai_instance = MagicMock()
                    mock_client.return_value = mock_openai_instance

                    # Mock CosmosDB client
                    mock_cosmos_instance = MagicMock()
                    mock_cosmos_client.return_value = mock_cosmos_instance

                    # Create tool with required parameters
                    tool = AzureCosmosDBNoSqlSearchTool(
                        cosmos_host="https://test.documents.azure.com:443/",
                        key="test_key",
                        token_credential=None,
                        indexing_policy={
                            "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}]
                        },
                        cosmos_container_properties={
                            "partition_key": {"paths": ["/id"], "kind": "Hash"}
                        },
                        cosmos_database_properties={},
                        vector_embedding_policy={
                            "vectorEmbeddings": [{"path": "/embedding", "dataType": "float32", "dimensions": 1536}]
                        }
                    )

                    # Mock the embedding method to return one embedding per input text
                    tool._embed_texts = lambda x: [[0.1, 0.2, 0.3] * 512 for _ in x]  # 1536 dimensions per text
                    tool._container = MagicMock()

                    yield tool


# Unit Tests
def test_vector_search_query(cosmosdb_tool, mock_cosmos_container):
    """Test vector search functionality."""
    cosmosdb_tool.search_type = "vector"
    cosmosdb_tool._container = mock_cosmos_container

    # Mock query execution
    mock_cosmos_container.query_items.return_value = [
        {
            "id": "1",
            "description": "Sample document about Azure AI",
            "SimilarityScore": 0.8,
            "metadata": {"category": "AI"}
        }
    ]

    results = cosmosdb_tool._run("Azure artificial intelligence")
    parsed_results = json.loads(results)

    assert len(parsed_results) == 1
    assert parsed_results[0]["id"] == "1"
    assert parsed_results[0]["SimilarityScore"] == 0.8
    mock_cosmos_container.query_items.assert_called_once()


def test_full_text_search_query(cosmosdb_tool, mock_cosmos_container):
    """Test full text search functionality."""
    cosmosdb_tool.search_type = "full_text_search"
    cosmosdb_tool._container = mock_cosmos_container

    # Mock query execution for full text search
    mock_cosmos_container.query_items.return_value = [
        {
            "id": "2",
            "description": "Document containing search terms",
            "metadata": {"category": "search"}
        }
    ]

    results = cosmosdb_tool._run("search terms")
    parsed_results = json.loads(results)

    assert len(parsed_results) == 1
    assert parsed_results[0]["id"] == "2"
    mock_cosmos_container.query_items.assert_called_once()


def test_full_text_ranking_query(cosmosdb_tool, mock_cosmos_container):
    """Test full text ranking search functionality."""
    cosmosdb_tool.search_type = "full_text_ranking"
    cosmosdb_tool.query_config = AzureCosmosDBNoSqlSearchConfig(
        full_text_rank_filter=[
            {"search_field": "title", "search_text": "Azure machine learning"}
        ]
    )
    cosmosdb_tool._container = mock_cosmos_container

    # Mock query execution for full text ranking
    mock_cosmos_container.query_items.return_value = [
        {
            "id": "3",
            "title": "Azure machine learning guide",
            "description": "Comprehensive guide to ML on Azure",
            "metadata": {"category": "guide"}
        }
    ]

    results = cosmosdb_tool._run("machine learning")
    parsed_results = json.loads(results)

    assert len(parsed_results) == 1
    assert parsed_results[0]["id"] == "3"
    assert "title" in parsed_results[0]
    mock_cosmos_container.query_items.assert_called_once()


def test_hybrid_search_query(cosmosdb_tool, mock_cosmos_container):
    """Test hybrid search functionality (combines vector and full text)."""
    cosmosdb_tool.search_type = "hybrid"
    cosmosdb_tool.query_config = AzureCosmosDBNoSqlSearchConfig(
        full_text_rank_filter=[
            {"search_field": "content", "search_text": "Azure AI services"}
        ],
        weights=[0.5, 0.5]  # Equal weight for vector and text search
    )
    cosmosdb_tool._container = mock_cosmos_container

    # Mock query execution for hybrid search
    mock_cosmos_container.query_items.return_value = [
        {
            "id": "4",
            "content": "Azure AI services documentation",
            "description": "Complete guide to Azure AI",
            "SimilarityScore": 0.9,
            "metadata": {"category": "documentation"}
        }
    ]

    results = cosmosdb_tool._run("AI services")
    parsed_results = json.loads(results)

    assert len(parsed_results) == 1
    assert parsed_results[0]["id"] == "4"
    assert parsed_results[0]["SimilarityScore"] == 0.9
    assert "content" in parsed_results[0]
    mock_cosmos_container.query_items.assert_called_once()


def test_search_with_config_parameters(cosmosdb_tool, mock_cosmos_container):
    """Test search with various configuration parameters."""
    config = AzureCosmosDBNoSqlSearchConfig(
        max_results=10,
        with_embedding=True,
        threshold=0.6,
        where="metadata.category = 'AI'"
    )
    cosmosdb_tool.query_config = config
    cosmosdb_tool._container = mock_cosmos_container

    # Mock query execution with config
    mock_cosmos_container.query_items.return_value = [
        {
            "id": "5",
            "description": "AI document",
            "SimilarityScore": 0.7,
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {"category": "AI"}
        }
    ]

    results = cosmosdb_tool._run("artificial intelligence")
    parsed_results = json.loads(results)

    assert len(parsed_results) == 1
    assert parsed_results[0]["SimilarityScore"] > config.threshold
    mock_cosmos_container.query_items.assert_called_once()


def test_search_with_threshold_filtering(cosmosdb_tool, mock_cosmos_container):
    """Test that results below threshold are filtered out."""
    cosmosdb_tool.query_config = AzureCosmosDBNoSqlSearchConfig(threshold=0.8)
    cosmosdb_tool._container = mock_cosmos_container

    # Mock query execution with low similarity score
    mock_cosmos_container.query_items.return_value = [
        {
            "id": "6",
            "description": "Low relevance document",
            "SimilarityScore": 0.5,  # Below threshold
            "metadata": {"category": "test"}
        }
    ]

    results = cosmosdb_tool._run("test query")
    parsed_results = json.loads(results)

    # Should return empty array due to threshold filtering
    assert len(parsed_results) == 0
    mock_cosmos_container.query_items.assert_called_once()


def test_query_construction_for_different_search_types(cosmosdb_tool):
    """Test that different search types generate appropriate queries."""

    # Test vector search query construction
    cosmosdb_tool.search_type = "vector"
    query, params = cosmosdb_tool._construct_query("test query")
    assert "VectorDistance" in query
    assert "ORDER BY" in query

    # Test full text ranking query construction
    cosmosdb_tool.search_type = "full_text_ranking"
    cosmosdb_tool.query_config = AzureCosmosDBNoSqlSearchConfig(
        full_text_rank_filter=[{"search_field": "title", "search_text": "test"}]
    )
    query, params = cosmosdb_tool._construct_query("test query")
    assert "FullTextScore" in query
    assert "RANK" in query


def test_embedding_generation(cosmosdb_tool):
    """Test that embeddings are generated correctly."""
    test_texts = ["Azure AI", "Machine Learning", "CosmosDB"]
    embeddings = cosmosdb_tool._embed_texts(test_texts)

    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)  # Default dimension size


def test_error_handling(cosmosdb_tool, mock_cosmos_container):
    """Test error handling in query execution."""
    cosmosdb_tool._container = mock_cosmos_container

    # Mock an exception during query execution
    mock_cosmos_container.query_items.side_effect = Exception("Database connection error")

    results = cosmosdb_tool._run("test query")

    # Should return empty string on error
    assert results == ""


def test_config_validation():
    """Test configuration validation."""
    # Test valid search type
    valid_config = AzureCosmosDBNoSqlSearchConfig()
    assert valid_config.max_results == 5  # Default value

    # Test configuration with custom values
    custom_config = AzureCosmosDBNoSqlSearchConfig(
        max_results=20,
        with_embedding=True,
        threshold=0.7
    )
    assert custom_config.max_results == 20
    assert custom_config.with_embedding is True
    assert custom_config.threshold == 0.7


def test_add_texts_functionality(cosmosdb_tool):
    """Test adding texts to the vector store."""
    # Mock the container's execute_item_batch method
    mock_result = MagicMock()
    cosmosdb_tool._container.execute_item_batch.return_value = mock_result

    texts = ["Document 1", "Document 2"]
    metadatas = [{"type": "test"}, {"type": "sample"}]

    # Mock the partition key property
    cosmosdb_tool.cosmos_container_properties = {"partition_key": "id"}

    doc_ids = cosmosdb_tool.add_texts(texts, metadatas)

    assert len(doc_ids) == 2
    cosmosdb_tool._container.execute_item_batch.assert_called()
