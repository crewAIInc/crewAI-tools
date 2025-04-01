import pytest
from crewai_tools import JSONSearchTool


def test_json_search_tool_with_string_query():
    """Test JSONSearchTool with a string query."""
    tool = JSONSearchTool(json_path="example.json")
    tool._run = lambda search_query, **kwargs: f"Query: {search_query}"
    
    result = tool.run("test query")
    assert "Query: test query" == result


def test_json_search_tool_with_dict_query():
    """Test JSONSearchTool with a dictionary query."""
    tool = JSONSearchTool(json_path="example.json")
    tool._run = lambda search_query, **kwargs: f"Query: {search_query}"
    
    result = tool.run({"description": "test query", "type": "str"})
    assert "Query: test query" == result


def test_json_search_tool_with_invalid_query():
    """Test JSONSearchTool with an invalid query type."""
    tool = JSONSearchTool(json_path="example.json")
    
    with pytest.raises(ValueError, match="search_query must be a string or a dictionary with a 'description' key"):
        tool.run(123)  # Not a string or dict with description
