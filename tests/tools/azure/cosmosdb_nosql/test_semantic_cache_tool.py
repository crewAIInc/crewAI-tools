import json
import os
from unittest.mock import Mock, patch

import pytest

from crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool import (
    AzureCosmosDBSemanticCacheConfig,
    AzureCosmosDBSemanticCacheTool,
    AzureCosmosDBSemanticCacheToolSchema,
)


class TestAzureCosmosDBSemanticCacheConfig:
    """Test suite for AzureCosmosDBSemanticCacheConfig."""

    def test_config_creation_minimal(self):
        """Test creating config with minimal required parameters."""
        indexing_policy = {
            "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}],
            "fullTextIndexes": [{"path": "/prompt"}]
        }

        config = AzureCosmosDBSemanticCacheConfig(
            cosmos_host="https://test.documents.azure.com:443/",
            key="dGVzdC1rZXk=",  # Valid base64 encoded "test-key"
            indexing_policy=indexing_policy
        )

        assert config.cosmos_host == "https://test.documents.azure.com:443/"
        assert config.key == "dGVzdC1rZXk="
        assert config.database_name == "memory_database"
        assert config.container_name == "memory_container"
        assert config.similarity_threshold == 0.85
        assert config.default_ttl == 86400
        assert config.enable_hybrid_search is True

    def test_config_custom_values(self):
        """Test creating config with custom values."""
        indexing_policy = {
            "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}],
            "fullTextIndexes": [{"path": "/prompt"}]
        }

        config = AzureCosmosDBSemanticCacheConfig(
            cosmos_host="https://custom.documents.azure.com:443/",
            key="Y3VzdG9tLWtleQ==",  # Valid base64 encoded "custom-key"
            database_name="custom_db",
            container_name="custom_container",
            similarity_threshold=0.9,
            default_ttl=3600,
            enable_hybrid_search=False,
            embedding_model="text-embedding-ada-002",
            embedding_dimensions=512,
            indexing_policy=indexing_policy
        )

        assert config.database_name == "custom_db"
        assert config.container_name == "custom_container"
        assert config.similarity_threshold == 0.9
        assert config.default_ttl == 3600
        assert config.enable_hybrid_search is False
        assert config.embedding_model == "text-embedding-ada-002"
        assert config.embedding_dimensions == 512

    def test_config_azure_openai_settings(self):
        """Test config with Azure OpenAI settings."""
        indexing_policy = {
            "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}],
            "fullTextIndexes": [{"path": "/prompt"}]
        }

        config = AzureCosmosDBSemanticCacheConfig(
            cosmos_host="https://test.documents.azure.com:443/",
            key="dGVzdC1rZXk=",  # Valid base64 encoded "test-key"
            azure_openai_endpoint="https://test.openai.azure.com/",
            openai_api_key="test-openai-key",
            indexing_policy=indexing_policy
        )

        assert config.azure_openai_endpoint == "https://test.openai.azure.com/"
        assert config.openai_api_key == "test-openai-key"


class TestAzureCosmosDBSemanticCacheToolSchema:
    """Test suite for AzureCosmosDBSemanticCacheToolSchema."""

    def test_schema_valid_operations(self):
        """Test schema with valid operations."""
        valid_operations = ["search", "update", "clear"]

        for operation in valid_operations:
            schema = AzureCosmosDBSemanticCacheToolSchema(operation=operation)
            assert schema.operation == operation

    def test_schema_operation_required(self):
        """Test that operation is required."""
        with pytest.raises(ValueError):
            AzureCosmosDBSemanticCacheToolSchema()


class TestAzureCosmosDBSemanticCacheTool:
    """Test suite for AzureCosmosDBSemanticCacheTool."""

    @pytest.fixture
    def valid_config(self):
        """Fixture providing a valid configuration."""
        return AzureCosmosDBSemanticCacheConfig(
            cosmos_host="https://test.documents.azure.com:443/",
            key="dGVzdC1rZXk=",  # Valid base64 encoded "test-key"
            database_name="test_db",
            container_name="test_container",
            indexing_policy={
                "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}],
                "fullTextIndexes": [{"path": "/prompt"}]
            },
            vector_embedding_policy={
                "vectorEmbeddings": [{"path": "/prompt_embedding", "dataType": "float32", "dimensions": 1536}]
            },
            full_text_policy={
                "fullTextPaths": [{"path": "/prompt"}]
            },
            openai_api_key="test-openai-key"
        )

    @pytest.fixture
    def minimal_config(self):
        """Fixture providing a minimal configuration for vector-only search."""
        return AzureCosmosDBSemanticCacheConfig(
            cosmos_host="https://test.documents.azure.com:443/",
            key="dGVzdC1rZXk=",  # Valid base64 encoded "test-key"
            indexing_policy={
                "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}]
            },
            vector_embedding_policy={
                "vectorEmbeddings": [{"path": "/prompt_embedding", "dataType": "float32", "dimensions": 1536}]
            },
            enable_hybrid_search=False,
            openai_api_key="test-openai-key"
        )

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_tool_initialization_success(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test successful tool initialization."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)

        assert tool.name == "AzureCosmosDBSemanticCacheTool"
        assert tool.config == valid_config
        mock_cosmos_client.assert_called_once()
        mock_openai_client.assert_called_once()

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.AzureOpenAI')
    def test_tool_initialization_azure_openai(self, mock_azure_openai, mock_cosmos_client, valid_config):
        """Test tool initialization with Azure OpenAI."""
        valid_config.azure_openai_endpoint = "https://test.openai.azure.com/"

        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)

        mock_azure_openai.assert_called_once()

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    def test_tool_initialization_missing_auth(self, mock_cosmos_client, valid_config):
        """Test tool initialization with missing authentication."""
        valid_config.key = None
        valid_config.token_credential = None

        with pytest.raises(ValueError, match="Either 'key' or 'token_credential' must be provided"):
            AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    def test_tool_initialization_missing_openai(self, mock_cosmos_client, valid_config):
        """Test tool initialization with missing OpenAI configuration."""
        valid_config.openai_api_key = None

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Either Azure OpenAI endpoint or OpenAI API key must be provided"):
                AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', False)
    @patch('click.confirm')
    def test_tool_initialization_missing_dependencies_decline(self, mock_confirm):
        """Test tool initialization with missing dependencies - user declines installation."""
        mock_confirm.return_value = False

        config = AzureCosmosDBSemanticCacheConfig(
            cosmos_host="https://test.documents.azure.com:443/",
            key="dGVzdC1rZXk=",  # Valid base64 encoded "test-key"
            indexing_policy={
                "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}]
            },
            vector_embedding_policy={
                "vectorEmbeddings": [{"path": "/prompt_embedding", "dataType": "float32", "dimensions": 1536}]
            },
            enable_hybrid_search=False,
            openai_api_key="test-openai-key"
        )

        with pytest.raises(ImportError, match="You are missing required packages"):
            AzureCosmosDBSemanticCacheTool(config=config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_validate_params_success(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test successful parameter validation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        # Should not raise any exception
        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        assert tool is not None

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    def test_validate_params_missing_vector_indexes(self, valid_config):
        """Test validation with missing vector indexes."""
        valid_config.indexing_policy = {"vectorIndexes": []}

        with pytest.raises(ValueError, match="vectorIndexes cannot be null or empty"):
            AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    def test_validate_params_missing_vector_embeddings(self, valid_config):
        """Test validation with missing vector embeddings."""
        valid_config.vector_embedding_policy = {"vectorEmbeddings": []}

        with pytest.raises(ValueError, match="vectorEmbeddings cannot be null"):
            AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    def test_validate_params_missing_partition_key(self, valid_config):
        """Test validation with missing partition key."""
        valid_config.cosmos_container_properties = {"partition_key": None}

        with pytest.raises(ValueError, match="partition_key cannot be null or empty"):
            AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    def test_validate_params_hybrid_search_missing_full_text_indexes(self, valid_config):
        """Test validation with hybrid search enabled but missing full text indexes."""
        valid_config.indexing_policy = {
            "vectorIndexes": [{"path": "/prompt_embedding", "type": "quantizedFlat"}],
            "fullTextIndexes": []
        }

        with pytest.raises(ValueError, match="fullTextIndexes cannot be null or empty"):
            AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    def test_validate_params_hybrid_search_missing_full_text_policy(self, valid_config):
        """Test validation with hybrid search enabled but missing full text policy."""
        valid_config.full_text_policy = {"fullTextPaths": []}

        with pytest.raises(ValueError, match="fullTextPaths cannot be null or empty"):
            AzureCosmosDBSemanticCacheTool(config=valid_config)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_generate_embedding_success(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test successful embedding generation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        embedding = tool._generate_embedding("test prompt")

        assert embedding == [0.1, 0.2, 0.3]
        mock_openai_instance.embeddings.create.assert_called_once_with(
            input="test prompt",
            model=valid_config.embedding_model,
            dimensions=valid_config.embedding_dimensions
        )

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_generate_embedding_failure(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test embedding generation failure."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_openai_instance.embeddings.create.side_effect = Exception("API Error")
        mock_openai_client.return_value = mock_openai_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)

        with pytest.raises(Exception, match="API Error"):
            tool._generate_embedding("test prompt")

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_run_unknown_operation(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test _run with unknown operation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._run(operation="invalid")

        result_data = json.loads(result)
        assert "error" in result_data
        assert "Unknown operation: invalid" in result_data["error"]
        assert result_data["valid_operations"] == ["search", "update", "clear"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_search_cache_missing_prompt(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test search cache with missing prompt."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._search_cache("")

        result_data = json.loads(result)
        assert result_data["error"] == "prompt is required for search operation"

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_search_cache_hit_hybrid(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test successful cache hit with hybrid search."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock container query result with high similarity
        mock_item = {
            "id": "test-id",
            "prompt": "test prompt",
            "response": "test response",
            "similarity_score": 0.1,  # Distance, will be converted to 0.9 similarity
            "metadata": {"timestamp": "2024-01-01T00:00:00Z"}
        }
        mock_container.query_items.return_value = [mock_item]

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._search_cache("test prompt")

        result_data = json.loads(result)
        assert result_data["cache_hit"] is True
        assert result_data["similarity_score"] == 0.9
        assert result_data["cached_response"] == "test response"
        assert result_data["cache_id"] == "test-id"

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_search_cache_hit_vector_only(self, mock_openai_client, mock_cosmos_client, minimal_config):
        """Test successful cache hit with vector-only search."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock container query result
        mock_item = {
            "id": "test-id",
            "prompt": "test prompt",
            "response": "test response",
            "similarity_score": 0.1,  # Distance, will be converted to 0.9 similarity
            "metadata": {"timestamp": "2024-01-01T00:00:00Z"}
        }
        mock_container.query_items.return_value = [mock_item]

        tool = AzureCosmosDBSemanticCacheTool(config=minimal_config)
        result = tool._search_cache("test prompt")

        result_data = json.loads(result)
        assert result_data["cache_hit"] is True
        assert result_data["similarity_score"] == 0.9

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_search_cache_miss_low_similarity(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test cache miss due to low similarity score."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock container query result with low similarity
        mock_item = {
            "id": "test-id",
            "similarity_score": 0.8,  # Distance, will be converted to 0.2 similarity
        }
        mock_container.query_items.return_value = [mock_item]

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._search_cache("test prompt")

        result_data = json.loads(result)
        assert result_data["cache_hit"] is False
        assert result_data["similarity_score"] == 0.0
        assert f"No cached response found above similarity threshold {valid_config.similarity_threshold}" in \
               result_data["message"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_search_cache_miss_no_results(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test cache miss with no results from query."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock empty query result
        mock_container.query_items.return_value = []

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._search_cache("test prompt")

        result_data = json.loads(result)
        assert result_data["cache_hit"] is False
        assert result_data["similarity_score"] == 0.0

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_search_cache_error(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test search cache with database error."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock container query error
        mock_container.query_items.side_effect = Exception("Database error")

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._search_cache("test prompt")

        result_data = json.loads(result)
        assert "error" in result_data
        assert "Failed to search cache: Database error" in result_data["error"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_update_cache_missing_prompt(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test update cache with missing prompt."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._update_cache("", "response")

        result_data = json.loads(result)
        assert result_data["error"] == "prompt is required for update operation"

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_update_cache_missing_response(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test update cache with missing response."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._update_cache("prompt", "")

        result_data = json.loads(result)
        assert result_data["error"] == "response is required for update operation"

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    @patch('uuid.uuid4')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.datetime')
    def test_update_cache_success(self, mock_datetime, mock_uuid, mock_openai_client, mock_cosmos_client, valid_config):
        """Test successful cache update."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock UUID and datetime
        mock_uuid.return_value = "test-uuid"
        mock_now = Mock()
        mock_now.isoformat.return_value = "2024-01-01T00:00:00Z"
        mock_datetime.now.return_value = mock_now

        # Mock successful upsert
        stored_item = {
            "id": "test-uuid",
            "prompt": "test prompt",
            "response": "test response"
        }
        mock_container.upsert_item.return_value = stored_item

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._update_cache("test prompt", "test response")

        result_data = json.loads(result)
        assert result_data["id"] == "test-uuid"
        assert result_data["prompt"] == "test prompt"
        assert result_data["response"] == "test response"

        # Verify upsert was called with correct document structure
        mock_container.upsert_item.assert_called_once()
        call_args = mock_container.upsert_item.call_args[1]["body"]
        assert call_args["id"] == "test-uuid"
        assert call_args["prompt"] == "test prompt"
        assert call_args["response"] == "test response"
        assert call_args["prompt_embedding"] == [0.1, 0.2, 0.3]
        assert call_args["ttl"] == valid_config.default_ttl

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_update_cache_no_ttl(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test cache update without TTL."""
        valid_config.default_ttl = None

        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        mock_container.upsert_item.return_value = {"id": "test"}

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        tool._update_cache("test prompt", "test response")

        # Verify TTL was not added to document
        call_args = mock_container.upsert_item.call_args[1]["body"]
        assert "ttl" not in call_args

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_update_cache_error(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test update cache with database error."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock container upsert error
        mock_container.upsert_item.side_effect = Exception("Database error")

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._update_cache("test prompt", "test response")

        result_data = json.loads(result)
        assert "error" in result_data
        assert "Failed to update cache: Database error" in result_data["error"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_clear_cache_success(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test successful cache clearing."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._clear_cache()

        assert result == "Cache is cleared."
        mock_cosmos_instance.delete_database.assert_called_once_with(valid_config.database_name)

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_clear_cache_error(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test cache clearing with database error."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        # Mock delete database error
        mock_cosmos_instance.delete_database.side_effect = Exception("Database error")

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._clear_cache()

        result_data = json.loads(result)
        assert "error" in result_data
        assert "Failed to clear cache: Database error" in result_data["error"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_run_search_operation(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test _run method with search operation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        mock_container.query_items.return_value = []

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._run(operation="search", prompt="test prompt")

        result_data = json.loads(result)
        assert result_data["cache_hit"] is False

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_run_update_operation(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test _run method with update operation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        mock_container.upsert_item.return_value = {"id": "test"}

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._run(operation="update", prompt="test prompt", response="test response")

        result_data = json.loads(result)
        assert result_data["id"] == "test"

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_run_clear_operation(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test _run method with clear operation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._run(operation="clear")

        assert result == "Cache is cleared."

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_run_operation_exception(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test _run method with exception during operation."""
        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_openai_instance.embeddings.create.side_effect = Exception("OpenAI error")
        mock_openai_client.return_value = mock_openai_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._run(operation="search", prompt="test prompt")

        result_data = json.loads(result)
        assert "error" in result_data
        assert "OpenAI error" in result_data["error"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    def test_custom_similarity_threshold(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test cache with custom similarity threshold."""
        valid_config.similarity_threshold = 0.95

        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        mock_openai_instance = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_openai_instance.embeddings.create.return_value = mock_response
        mock_openai_client.return_value = mock_openai_instance

        # Mock item with similarity 0.9 (below 0.95 threshold)
        mock_item = {
            "id": "test-id",
            "similarity_score": 0.1,  # Distance, converts to 0.9 similarity
        }
        mock_container.query_items.return_value = [mock_item]

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)
        result = tool._search_cache("test prompt")

        result_data = json.loads(result)
        assert result_data["cache_hit"] is False
        assert "0.95" in result_data["message"]

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.TokenCredential')
    def test_token_credential_initialization(self, mock_token_credential_class, mock_openai_client, mock_cosmos_client,
                                             valid_config):
        """Test initialization with token credential instead of key."""
        mock_credential = mock_token_credential_class.return_value
        valid_config.key = None
        valid_config.token_credential = mock_credential

        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)

        # Verify CosmosClient was called with token credential
        mock_cosmos_client.assert_called_once_with(
            valid_config.cosmos_host,
            mock_credential,
            user_agent=AzureCosmosDBSemanticCacheTool.USER_AGENT
        )

    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.COSMOSDB_AVAILABLE', True)
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.CosmosClient')
    @patch('crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool.Client')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env-openai-key'})
    def test_openai_from_environment(self, mock_openai_client, mock_cosmos_client, valid_config):
        """Test OpenAI client initialization from environment variable."""
        valid_config.openai_api_key = None

        mock_database = Mock()
        mock_container = Mock()
        mock_cosmos_instance = Mock()
        mock_cosmos_instance.create_database_if_not_exists.return_value = mock_database
        mock_database.create_container_if_not_exists.return_value = mock_container
        mock_cosmos_client.return_value = mock_cosmos_instance

        tool = AzureCosmosDBSemanticCacheTool(config=valid_config)

        # Verify OpenAI Client was called with environment variable
        mock_openai_client.assert_called_once_with(api_key='env-openai-key')