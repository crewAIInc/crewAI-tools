"""Tests for MDXSearchTool with local provider configurations."""

import pytest
from unittest.mock import patch, MagicMock
from crewai_tools.tools.mdx_search_tool.mdx_search_tool import MDXSearchTool


class TestMDXSearchToolLocalConfig:
    """Test MDXSearchTool with local provider configurations."""

    def test_mdx_search_tool_with_local_ollama_config(self):
        """Test that MDXSearchTool can be created with local Ollama configuration without OpenAI API key."""
        config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.1:8b",
                    "base_url": "http://localhost:11434",
                    "temperature": 0.3,
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "embeddinggemma:latest",
                    "base_url": "http://localhost:11434",
                    "task_type": "retrieval_document",
                },
            },
        }

        with patch('crewai_tools.adapters.crewai_rag_adapter.CrewAIRagAdapter') as mock_adapter:
            mock_adapter_instance = MagicMock()
            mock_adapter.return_value = mock_adapter_instance
            
            tool = MDXSearchTool(config=config)
            
            assert tool is not None
            assert tool.name == "Search a MDX's content"
            assert "semantic search" in tool.description

    def test_mdx_search_tool_config_parsing_with_local_providers(self):
        """Test that the config parsing correctly handles local providers."""
        tool = MDXSearchTool()
        
        config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.1:8b",
                    "base_url": "http://localhost:11434",
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "embeddinggemma:latest",
                    "url": "http://localhost:11434/api/embeddings",
                },
            },
        }
        
        with patch('chromadb.utils.embedding_functions.ollama_embedding_function.OllamaEmbeddingFunction') as mock_ollama_func:
            mock_embedding_instance = MagicMock()
            mock_ollama_func.return_value = mock_embedding_instance
            
            parsed_config = tool._parse_config(config)
            
            assert parsed_config is not None
            assert hasattr(parsed_config, 'embedding_function')
            assert parsed_config.embedding_function is not None
            
            mock_ollama_func.assert_called_once_with(
                model_name="embeddinggemma:latest",
                url="http://localhost:11434/api/embeddings"
            )

    def test_mdx_search_tool_config_parsing_with_vectordb_config(self):
        """Test that the config parsing still works with vectordb configuration."""
        tool = MDXSearchTool()
        
        config = {
            "vectordb": {
                "provider": "chromadb",
                "config": {
                    "collection_name": "test_collection"
                }
            },
            "embedding_model": {
                "provider": "ollama",
                "config": {
                    "model": "embeddinggemma:latest"
                }
            }
        }
        
        with patch.object(tool, '_create_embedding_function') as mock_create_embedding, \
             patch.object(tool, '_create_provider_config') as mock_create_provider:
            
            mock_embedding_func = MagicMock()
            mock_create_embedding.return_value = mock_embedding_func
            mock_provider_config = MagicMock()
            mock_create_provider.return_value = mock_provider_config
            
            parsed_config = tool._parse_config(config)
            
            mock_create_embedding.assert_called_once_with(
                config["embedding_model"], "chromadb"
            )
            mock_create_provider.assert_called_once_with(
                "chromadb", {"collection_name": "test_collection"}, mock_embedding_func
            )
            assert parsed_config == mock_provider_config

    def test_mdx_search_tool_config_parsing_with_openai_still_works(self):
        """Test that OpenAI configuration still works (backward compatibility)."""
        tool = MDXSearchTool()
        
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "api_key": "test-key",
                },
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": "test-key",
                },
            },
        }
        
        with patch('crewai_tools.tools.rag.rag_tool.get_embedding_function') as mock_get_embedding:
            mock_embedding_func = MagicMock()
            mock_get_embedding.return_value = mock_embedding_func
            
            parsed_config = tool._parse_config(config)
            
            assert parsed_config is not None
            assert hasattr(parsed_config, 'embedding_function')
            assert parsed_config.embedding_function is not None
            
            mock_get_embedding.assert_called_once()
            call_args = mock_get_embedding.call_args[0][0]
            assert call_args["provider"] == "openai"
            assert call_args["api_key"] == "test-key"

    def test_mdx_search_tool_config_parsing_none_config(self):
        """Test that None config is handled correctly."""
        tool = MDXSearchTool()
        
        parsed_config = tool._parse_config(None)
        assert parsed_config is None

    def test_mdx_search_tool_config_parsing_provider_in_root(self):
        """Test that config with provider in root is returned as-is."""
        tool = MDXSearchTool()
        
        config = {"provider": "test_provider", "config": {"test": "value"}}
        parsed_config = tool._parse_config(config)
        
        assert parsed_config == config

    def test_mdx_search_tool_with_fixed_mdx_file(self):
        """Test MDXSearchTool with a fixed MDX file and local config."""
        config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "llama3.1:8b",
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "embeddinggemma:latest",
                },
            },
        }

        with patch('crewai_tools.adapters.crewai_rag_adapter.CrewAIRagAdapter') as mock_adapter:
            mock_adapter_instance = MagicMock()
            mock_adapter.return_value = mock_adapter_instance
            
            tool = MDXSearchTool(mdx="test.mdx", config=config)
            
            assert tool is not None
            assert "test.mdx" in tool.description
            assert tool.args_schema.__name__ == "FixedMDXSearchToolSchema"
