"""Tests for Neo4j search tool with mocked RAG adapter."""

from unittest.mock import Mock, patch, MagicMock
from typing import cast

import pytest

from crewai_tools import Neo4jSearchTool
from crewai_tools.adapters.crewai_rag_adapter import CrewAIRagAdapter
from crewai_tools.rag.base_loader import LoaderResult


@patch('crewai_tools.adapters.crewai_rag_adapter.get_rag_client')
@patch('crewai_tools.adapters.crewai_rag_adapter.create_client')
def test_neo4j_search_tool_initialization(
    mock_create_client: Mock,
    mock_get_rag_client: Mock
) -> None:
    """Test that Neo4jSearchTool initializes with CrewAI adapter."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=None)
    mock_get_rag_client.return_value = mock_client
    mock_create_client.return_value = mock_client

    tool = Neo4jSearchTool(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )
    
    assert tool.adapter is not None
    assert isinstance(tool.adapter, CrewAIRagAdapter)
    assert tool.neo4j_uri == "bolt://localhost:7687"
    assert tool.neo4j_user == "neo4j"
    assert tool.neo4j_password == "password"

    adapter = cast(CrewAIRagAdapter, tool.adapter)
    assert adapter.collection_name == "rag_tool_collection"
    assert adapter._client is not None


@patch('crewai_tools.adapters.crewai_rag_adapter.get_rag_client')
@patch('crewai_tools.adapters.crewai_rag_adapter.create_client')
@patch('crewai_tools.rag.loaders.neo4j_loader.Neo4jLoader.load')
def test_neo4j_search_tool_add(
    mock_neo4j_load: Mock,
    mock_create_client: Mock,
    mock_get_rag_client: Mock
) -> None:
    """Test adding content to Neo4jSearchTool."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=None)
    mock_client.add_documents = MagicMock(return_value=None)
    mock_get_rag_client.return_value = mock_client
    mock_create_client.return_value = mock_client
    mock_neo4j_load.return_value = LoaderResult(
        content="Test Neo4j content from query",
        metadata={"source": "MATCH (n) RETURN n LIMIT 10"},
        doc_id="test_doc_1"
    )

    tool = Neo4jSearchTool(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )

    query = "MATCH (n) RETURN n LIMIT 10"
    tool.add(query)

    # Verify that add_documents was called
    assert mock_client.add_documents.call_count == 1


@patch('crewai_tools.adapters.crewai_rag_adapter.get_rag_client')
@patch('crewai_tools.adapters.crewai_rag_adapter.create_client')
@patch('crewai_tools.rag.loaders.neo4j_loader.Neo4jLoader.load')
def test_neo4j_search_tool_run(
    mock_neo4j_load: Mock,
    mock_create_client: Mock,
    mock_get_rag_client: Mock
) -> None:
    """Test running a search query with Neo4jSearchTool."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=None)
    mock_client.add_documents = MagicMock(return_value=None)
    mock_client.search = MagicMock(return_value=[
        {
            "content": "Record 1:\n  name: Alice\n  age: 30",
            "metadata": {},
            "score": 0.9
        }
    ])
    mock_get_rag_client.return_value = mock_client
    mock_create_client.return_value = mock_client
    mock_neo4j_load.return_value = LoaderResult(
        content="MATCH (n) RETURN n LIMIT 10\nRecord 1:\n  name: Alice\n  age: 30",
        metadata={"source": "MATCH (n) RETURN n LIMIT 10"},
        doc_id="test_doc_1"
    )

    tool = Neo4jSearchTool(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )

    # First add some content
    tool.add("MATCH (n) RETURN n LIMIT 10")
    
    # Now run a query
    result = tool._run(search_query="Find all people named Alice")
    
    assert "Relevant Content:" in result
    assert "Alice" in result
    assert "Record 1" in result


@patch('crewai_tools.adapters.crewai_rag_adapter.get_rag_client')
@patch('crewai_tools.adapters.crewai_rag_adapter.create_client')
@patch('crewai_tools.rag.loaders.neo4j_loader.Neo4jLoader.load')
def test_neo4j_search_tool_run_with_custom_params(
    mock_neo4j_load: Mock,
    mock_create_client: Mock,
    mock_get_rag_client: Mock
) -> None:
    """Test running a search query with custom similarity threshold and limit."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=None)
    mock_client.add_documents = MagicMock(return_value=None)
    mock_client.search = MagicMock(return_value=[
        {
            "content": "Test record",
            "metadata": {},
            "score": 0.85
        }
    ])
    mock_get_rag_client.return_value = mock_client
    mock_create_client.return_value = mock_client
    mock_neo4j_load.return_value = LoaderResult(
        content="Test record\nFind nodes query result",
        metadata={"source": "Find nodes"},
        doc_id="test_doc_1"
    )

    tool = Neo4jSearchTool(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )

    result = tool._run(
        search_query="Find nodes",
        similarity_threshold=0.7,
        limit=3
    )
    
    assert "Relevant Content:" in result
    # Verify that search was called with custom parameters
    mock_client.search.assert_called_once()


@patch('crewai_tools.adapters.crewai_rag_adapter.get_rag_client')
@patch('crewai_tools.adapters.crewai_rag_adapter.create_client')
@patch('crewai_tools.rag.loaders.neo4j_loader.Neo4jLoader.load')
def test_neo4j_search_tool_no_results(
    mock_neo4j_load: Mock,
    mock_create_client: Mock,
    mock_get_rag_client: Mock
) -> None:
    """Test Neo4jSearchTool when no relevant content is found."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=None)
    mock_client.search = MagicMock(return_value=[])
    mock_get_rag_client.return_value = mock_client
    mock_create_client.return_value = mock_client
    mock_neo4j_load.return_value = LoaderResult(
        content="Non-existent query\nNo results found",
        metadata={"source": "Non-existent query"},
        doc_id="test_doc_1"
    )

    tool = Neo4jSearchTool(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )

    result = tool._run(search_query="Non-existent query")
    
    assert "Relevant Content:" in result
    # Should handle empty results gracefully
    mock_client.search.assert_called_once()


@patch('crewai_tools.adapters.crewai_rag_adapter.get_rag_client')
@patch('crewai_tools.adapters.crewai_rag_adapter.create_client')
def test_neo4j_search_tool_description(
    mock_create_client: Mock,
    mock_get_rag_client: Mock
) -> None:
    """Test that Neo4jSearchTool has the correct description."""
    mock_client = MagicMock()
    mock_client.get_or_create_collection = MagicMock(return_value=None)
    mock_get_rag_client.return_value = mock_client
    mock_create_client.return_value = mock_client

    tool = Neo4jSearchTool(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )
    
    assert "Neo4j" in tool.description
    assert tool.name == "Neo4j Search Tool"

