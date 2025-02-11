import unittest
from unittest.mock import patch, MagicMock
from crewai_tools.tools.github_search_tool.github_search_tool import GithubSearchTool

class TestGithubSearchTool(unittest.TestCase):
    @patch('embedchain.App')
    def test_initialization_with_required_fields(self, mock_app):
        """Test that the tool can be initialized with required fields."""
        tool = GithubSearchTool(
            github_repo="test/repo",
            gh_token="test-token",
            content_types=["code"]
        )
        self.assertEqual(tool.gh_token, "test-token")
        self.assertEqual(tool.content_types, ["code"])
        self.assertEqual(tool.args_schema.__name__, "FixedGithubSearchToolSchema")
        self.assertIn("test/repo", tool.description)

    @patch('embedchain.App')
    def test_initialization_with_kwargs(self, mock_app):
        """Test that the tool can be initialized with kwargs."""
        tool = GithubSearchTool(
            gh_token="test-token",
            content_types=["code"]
        )
        self.assertEqual(tool.gh_token, "test-token")
        self.assertEqual(tool.content_types, ["code"])
        self.assertEqual(tool.args_schema.__name__, "GithubSearchToolSchema")

    @patch('embedchain.App')
    @patch('crewai_tools.tools.github_search_tool.github_search_tool.GithubLoader')
    def test_search_with_valid_inputs(self, mock_loader, mock_app):
        """Test search functionality with valid inputs."""
        # Setup mocks
        mock_loader_instance = MagicMock()
        mock_loader.return_value = mock_loader_instance
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.query.return_value = ("Test result", [])
        
        # Mock the adapter
        mock_adapter = MagicMock()
        mock_adapter.query.return_value = "Test result"
        
        tool = GithubSearchTool(
            gh_token="test-token",
            content_types=["code"]
        )
        tool.adapter = mock_adapter
        
        # Test search
        result = tool._run(
            search_query="test query",
            github_repo="test/repo"
        )
        
        # Verify that loader was called with correct parameters
        self.assertTrue(mock_loader.called)
        self.assertTrue(mock_loader.call_args[1]["config"]["token"] == "test-token")
        self.assertIn("Test result", result)

    @patch('embedchain.App')
    def test_validation_error_without_required_fields(self, mock_app):
        """Test that validation error is raised when required fields are missing."""
        with self.assertRaises(ValueError):
            tool = GithubSearchTool()
            tool._run(
                search_query="test query",
                github_repo="test/repo"
            )
