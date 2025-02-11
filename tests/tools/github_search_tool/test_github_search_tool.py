import unittest
from typing import Any
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
from crewai_tools.tools.github_search_tool.github_search_tool import GithubSearchTool
from crewai_tools.tools.rag.rag_tool import Adapter

class TestGithubSearchTool(unittest.TestCase):
    @patch('embedchain.App')
    def test_initialization_with_required_fields(self, mock_app):
        """Test that the tool can be initialized with required fields."""
        tool = GithubSearchTool(
            github_repo="test/repo",
            gh_token="ghp_123456789012345678901234567890123456",
            content_types=["code"]
        )
        self.assertTrue(tool.gh_token.startswith("ghp_"))
        self.assertEqual(tool.content_types, ["code"])
        self.assertEqual(tool.args_schema.__name__, "FixedGithubSearchToolSchema")
        self.assertIn("test/repo", tool.description)

    @patch('embedchain.App')
    def test_initialization_with_kwargs(self, mock_app):
        """Test that the tool can be initialized with kwargs."""
        tool = GithubSearchTool(
            gh_token="ghp_123456789012345678901234567890123456",
            content_types=["code"]
        )
        self.assertTrue(tool.gh_token.startswith("ghp_"))
        self.assertEqual(tool.content_types, ["code"])
        self.assertEqual(tool.args_schema.__name__, "GithubSearchToolSchema")

    @patch('embedchain.App')
    def test_search_with_valid_inputs(self, mock_app):
        """Test search functionality with valid inputs."""
        # Setup mocks
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.query.return_value = ("Test result", [])
        
        # Create tool with mocked loader
        with patch('crewai_tools.tools.github_search_tool.github_search_tool.GithubLoader') as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader.return_value = mock_loader_instance
            tool = GithubSearchTool(
                gh_token="ghp_123456789012345678901234567890123456",
                content_types=["code"],
                github_repo="test/repo"
            )
            
            # Mock the adapter
            class MockAdapter:
                def query(self, question: str) -> str:
                    return "Test result"
                
                def add(self, *args: Any, **kwargs: Any) -> None:
                    pass
            
            tool.adapter = MockAdapter()
            
            # Verify that loader was called with correct parameters
            self.assertTrue(mock_loader.called)
            self.assertEqual(mock_loader.call_args[1]["config"]["token"], "ghp_123456789012345678901234567890123456")
            
            # Test search
            result = tool._run(
                search_query="test query"
            )
            
            # Verify that loader was called with correct parameters
            self.assertTrue(mock_loader.called)
            self.assertEqual(mock_loader.call_args[1]["config"]["token"], "ghp_123456789012345678901234567890123456")
            self.assertIn("Test result", result)
            
            # Verify that loader was called with correct parameters
            self.assertTrue(mock_loader.called)
            self.assertEqual(mock_loader.call_args[1]["config"]["token"], "ghp_123456789012345678901234567890123456")
            self.assertIn("Test result", result)

    @patch('embedchain.App')
    def test_validation_error_without_required_fields(self, mock_app):
        """Test that validation error is raised when required fields are missing."""
        with self.assertRaises(ValueError) as cm:
            GithubSearchTool()
        self.assertIn("Field required", str(cm.exception))

    @patch('embedchain.App')
    def test_validation_error_with_invalid_content_types(self, mock_app):
        """Test that validation error is raised with invalid content types."""
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.query.return_value = ("Test result", [])
        
        with self.assertRaises(ValueError) as cm:
            GithubSearchTool(
                github_repo="test/repo",
                gh_token="ghp_123456789012345678901234567890123456",
                content_types=["invalid_type"]
            )
        self.assertIn("Invalid content types", str(cm.exception))

    @patch('embedchain.App')
    def test_validation_error_with_invalid_token_format(self, mock_app):
        """Test that validation error is raised with invalid token format."""
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.query.return_value = ("Test result", [])
        
        with self.assertRaises(ValueError) as cm:
            GithubSearchTool(
                github_repo="test/repo",
                gh_token="invalid_token",
                content_types=["code"]
            )
        self.assertIn("String should match pattern", str(cm.exception))

    @patch('embedchain.App')
    def test_query_sanitization(self, mock_app):
        """Test that queries are properly sanitized."""
        tool = GithubSearchTool(
            gh_token="ghp_123456789012345678901234567890123456",
            content_types=["code"]
        )
        result = tool._sanitize_query("test!@#$%^&*()query")
        self.assertEqual(result, "testquery")

    @patch('embedchain.App')
    def test_cache_functionality(self, mock_app):
        """Test that caching works correctly."""
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.query.return_value = "Test result"
        
        # Create a mock adapter that inherits from Adapter
        class MockAdapter:
            def __init__(self):
                self.query_count = 0
                
            def query(self, question: str) -> str:
                self.query_count += 1
                return "Test result"
                
            def add(self, *args: Any, **kwargs: Any) -> None:
                pass
        
        tool = GithubSearchTool(
            gh_token="ghp_123456789012345678901234567890123456",
            content_types=["code"]
        )
        mock_adapter = MockAdapter()
        tool.adapter = mock_adapter
        
        query = "test query"
        first_result = tool._run(query, github_repo="test/repo")
        second_result = tool._run(query, github_repo="test/repo")
        self.assertEqual(first_result, second_result)
        # Verify query was only called once
        self.assertEqual(mock_adapter.query_count, 1)
