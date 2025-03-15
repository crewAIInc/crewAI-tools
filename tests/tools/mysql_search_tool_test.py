import pytest
from unittest.mock import MagicMock, patch

from crewai_tools import MySQLSearchTool


@pytest.fixture
def mysql_tool():
    # Mock the mysql.connector module
    mysql_connector_mock = MagicMock()
    
    # Mock the MySQLLoader class
    mysql_loader_mock = MagicMock()
    
    # Apply patches to avoid actual imports
    with patch.dict('sys.modules', {'mysql': MagicMock(), 'mysql.connector': mysql_connector_mock}):
        with patch('embedchain.loaders.mysql.MySQLLoader', return_value=mysql_loader_mock):
            # Create the tool with mocked dependencies
            tool = MySQLSearchTool(db_uri='mysql://user:password@localhost:3306/mydatabase', table_name='employees')
            # Mock the adapter for search tests
            tool.adapter = MagicMock()
            yield tool


def test_mysql_tool_initialization(mysql_tool):
    """Test that MySQLSearchTool can be initialized with the correct dependencies."""
    assert mysql_tool is not None
    assert mysql_tool.db_uri == 'mysql://user:password@localhost:3306/mydatabase'
    assert "employees" in mysql_tool.description


def test_mysql_tool_uri_format():
    """Test MySQL tool with different URI formats."""
    with patch.dict('sys.modules', {'mysql': MagicMock(), 'mysql.connector': MagicMock()}):
        with patch('embedchain.loaders.mysql.MySQLLoader'):
            # Test with a standard MySQL URI
            tool = MySQLSearchTool(db_uri='mysql://user:password@localhost:3306/mydatabase', table_name='employees')
            assert tool.db_uri == 'mysql://user:password@localhost:3306/mydatabase'
            
            # Test with a URI containing additional parameters
            tool = MySQLSearchTool(
                db_uri='mysql://user:password@localhost:3306/mydatabase?charset=utf8', 
                table_name='employees'
            )
            assert 'charset=utf8' in tool.db_uri


def test_mysql_tool_search(mysql_tool):
    """Test search functionality."""
    # Mock query results
    mysql_tool.adapter.query.return_value = "John Doe, Employee ID: 1, Score: 0.95"
    
    # Call the _run method directly with a search query
    results = mysql_tool._run("John")
    
    # Verify the adapter's query method was called with the correct argument
    mysql_tool.adapter.query.assert_called_once_with("John")
    
    # Verify the results contain the expected content
    assert "John Doe" in results
