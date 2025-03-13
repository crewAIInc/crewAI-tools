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
            yield tool


def test_mysql_tool_initialization(mysql_tool):
    """Test that MySQLSearchTool can be initialized with the correct dependencies."""
    assert mysql_tool is not None
    assert mysql_tool.db_uri == 'mysql://user:password@localhost:3306/mydatabase'
    assert "employees" in mysql_tool.description
