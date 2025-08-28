import json
from unittest.mock import Mock, patch

import pytest

from crewai_tools.tools.chroma_tool.chroma_search_tool import ChromaSearchTool


@pytest.fixture
def mock_collection():
    collection = Mock()
    collection.query.return_value = {
        "documents": [["Test document 1", "Test document 2"]],
        "metadatas": [[{"source": "test1.txt"}, {"source": "test2.txt"}]],
        "ids": [["doc1", "doc2"]]
    }
    return collection


@pytest.fixture
def chroma_tool(mock_collection):
    return ChromaSearchTool(collection=mock_collection)


def test_tool_initialization(mock_collection):
    tool = ChromaSearchTool(collection=mock_collection, limit=5)
        
    assert tool.collection == mock_collection
    assert tool.limit == 5
    assert tool.name == "ChromaSearchTool"


def test_missing_collection():
    """Test initialization fails without collection"""
    with pytest.raises(Exception):
        ChromaSearchTool()


def test_successful_search(chroma_tool):
    """Test successful search execution"""
    result = chroma_tool._run(query="test query")
    
    parsed_result = json.loads(result)
    assert len(parsed_result) == 2
    assert parsed_result[0]["document"] == "Test document 1"
    assert parsed_result[0]["metadata"]["source"] == "test1.txt"
    assert parsed_result[0]["id"] == "doc1"


def test_search_with_filter(chroma_tool):
    """Test search with metadata filtering"""
    chroma_tool.collection.query.return_value = {
        "documents": [["Filtered document"]],
        "metadatas": [[{"source": "filtered.txt"}]],
        "ids": [["filtered_doc"]]
    }
    
    result = chroma_tool._run(query="test query", where={"source": "filtered.txt"})
    
    parsed_result = json.loads(result)
    assert len(parsed_result) == 1
    assert parsed_result[0]["metadata"]["source"] == "filtered.txt"
    
    chroma_tool.collection.query.assert_called_with(
        query_texts=["test query"],
        n_results=3,
        where={"source": "filtered.txt"}
    )


def test_search_with_document_filter(chroma_tool):
    """Test search with document content filtering"""
    chroma_tool.collection.query.return_value = {
        "documents": [["Document containing specific text"]],
        "metadatas": [[{"source": "doc.txt"}]],
        "ids": [["doc_with_text"]]
    }
    
    result = chroma_tool._run(
        query="test query", 
        where_document={"$contains": "specific text"}
    )
    
    parsed_result = json.loads(result)
    assert len(parsed_result) == 1
    assert "specific text" in parsed_result[0]["document"]
    
    chroma_tool.collection.query.assert_called_with(
        query_texts=["test query"],
        n_results=3,
        where_document={"$contains": "specific text"}
    )


def test_search_with_both_filters(chroma_tool):
    """Test search with both metadata and document filtering"""
    chroma_tool.collection.query.return_value = {
        "documents": [["Filtered document with specific content"]],
        "metadatas": [[{"source": "special.txt", "category": "important"}]],
        "ids": [["special_doc"]]
    }
    
    result = chroma_tool._run(
        query="test query",
        where={"category": "important"},
        where_document={"$contains": "specific content"}
    )
    
    parsed_result = json.loads(result)
    assert len(parsed_result) == 1
    assert parsed_result[0]["metadata"]["category"] == "important"
    assert "specific content" in parsed_result[0]["document"]
    
    chroma_tool.collection.query.assert_called_with(
        query_texts=["test query"],
        n_results=3,
        where={"category": "important"},
        where_document={"$contains": "specific content"}
    )
