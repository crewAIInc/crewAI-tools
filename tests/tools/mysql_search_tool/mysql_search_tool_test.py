import pytest
from unittest.mock import patch, MagicMock, Mock

from crewai_tools.tools.mysql_search_tool.mysql_search_tool import (
    MySQLSearchTool,
)


class TestMySQLSearchTool:
    """Test suite for MySQLSearchTool."""

    def test_parse_uri_to_config(self):
        """Test the URI parsing functionality."""
        uri = "mysql://user:pass@hostname:3307/database"
        config = MySQLSearchTool._parse_uri_to_config(uri)
        assert config == {
            "user": "user",
            "password": "pass",
            "host": "hostname",
            "port": 3307,
            "database": "database",
        }

        uri = "mysql://user:p@ss#w0rd@hostname:3307/database"
        config = MySQLSearchTool._parse_uri_to_config(uri)
        assert config == {
            "user": "user",
            "password": "p@ss#w0rd",
            "host": "hostname",
            "port": 3307,
            "database": "database",
        }

        uri = "mysql://user:pass@hostname/database"
        config = MySQLSearchTool._parse_uri_to_config(uri)
        assert config == {
            "user": "user",
            "password": "pass",
            "host": "hostname",
            "port": 3306,
            "database": "database",
        }

        uri = "mysql://hostname/database"
        config = MySQLSearchTool._parse_uri_to_config(uri)
        assert config == {
            "host": "hostname",
            "port": 3306,
            "database": "database",
        }

        uri = "mysql://user@hostname/database"
        config = MySQLSearchTool._parse_uri_to_config(uri)
        assert config == {
            "user": "user",
            "host": "hostname",
            "port": 3306,
            "database": "database",
        }

    def test_invalid_uri_formats(self):
        """Test that invalid URI formats raise appropriate errors."""
        with pytest.raises(ValueError, match="Database name missing in the URI path"):
            MySQLSearchTool._parse_uri_to_config("mysql://hostname/")

        with pytest.raises(ValueError, match="Invalid scheme"):
            MySQLSearchTool._parse_uri_to_config("postgresql://user:pass@hostname/database")

        with pytest.raises(ValueError, match="Invalid port number"):
            MySQLSearchTool._parse_uri_to_config("mysql://hostname:abc/database")
            
        with pytest.raises(ValueError, match="Hostname missing in the URI"):
            MySQLSearchTool._parse_uri_to_config("mysql://:/database")

    @patch("crewai_tools.tools.mysql_search_tool.mysql_search_tool.MySQLLoader")
    def test_tool_initialization(self, mock_mysql_loader):
        """Test the tool initialization with various URI formats."""
        mock_loader_instance = MagicMock()
        mock_mysql_loader.return_value = mock_loader_instance

        tool = MySQLSearchTool(
            db_uri="mysql://user:pass@hostname:3307/database",
            table_name="employees"
        )
        
        assert tool.db_uri == "mysql://user:pass@hostname:3307/database"
        assert tool.table_name == "employees"
        assert tool.description == "Performs semantic search on the 'employees' table in the specified MySQL database. Input is the search query."

        mock_mysql_loader.assert_called_once()
        call_args = mock_mysql_loader.call_args[1]
        assert "config" in call_args
        assert call_args["config"]["host"] == "hostname"
        assert call_args["config"]["port"] == 3307
        assert call_args["config"]["database"] == "database"
        assert call_args["config"]["user"] == "user"
        assert call_args["config"]["password"] == "pass"

    @patch("crewai_tools.tools.mysql_search_tool.mysql_search_tool.MySQLLoader")
    def test_add_method(self, mock_mysql_loader):
        """Test the add method."""
        mock_loader_instance = MagicMock()
        mock_mysql_loader.return_value = mock_loader_instance
        
        tool = MySQLSearchTool(
            db_uri="mysql://user:pass@hostname/database",
            table_name="employees"
        )
        
        mock_adapter = MagicMock()
        tool.adapter = mock_adapter
        
        tool.add()
        
        mock_adapter.add.assert_called_once_with(
            "SELECT * FROM `employees`;", 
            data_type="mysql", 
            loader=tool._mysql_loader
        )
        
        assert tool._initial_data_added is True
        
        tool._initial_data_added = False  # Reset flag
        tool.add("custom_table")
        
        mock_adapter.add.assert_called_with(
            "SELECT * FROM `custom_table`;", 
            data_type="mysql", 
            loader=tool._mysql_loader
        )
        
        assert tool._initial_data_added is False

    @patch("crewai_tools.tools.mysql_search_tool.mysql_search_tool.MySQLLoader")
    def test_run_method(self, mock_mysql_loader):
        """Test the _run method."""
        mock_loader_instance = MagicMock()
        mock_mysql_loader.return_value = mock_loader_instance
        
        with patch("crewai_tools.tools.rag.rag_tool.RagTool._run") as mock_super_run:
            mock_super_run.return_value = "Test result"
            
            tool = MySQLSearchTool(
                db_uri="mysql://user:pass@hostname/database",
                table_name="employees"
            )
            
            mock_adapter = MagicMock()
            tool.adapter = mock_adapter
            
            tool._initial_data_added = True
            result = tool._run("search query")
            
            mock_super_run.assert_called_once_with(query="search query")
            assert result == "Test result"
            
            tool._initial_data_added = False
            
            original_add = tool.add
            try:
                mock_add = MagicMock()
                tool.add = mock_add
                
                result = tool._run("another query")
                
                mock_add.assert_called_once()
                assert mock_super_run.call_count == 2
                assert result == "Test result"
            finally:
                tool.add = original_add
