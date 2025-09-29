import os
import pytest
from unittest.mock import MagicMock, patch, Mock
from urllib.parse import urlparse

from crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool import (
    ScrapegraphScrapeTool,
    ScrapegraphError,
    RateLimitError,
    ScrapingMode,
    ScrapegraphScrapeToolSchema,
)


class TestScrapegraphScrapeTool:
    """Test suite for ScrapegraphScrapeTool"""

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_tool_initialization_with_api_key(self, mock_client_class):
        """Test tool initialization with API key"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        assert tool.api_key == "test_api_key"
        assert tool._client == mock_client
        assert tool.mode == ScrapingMode.SMARTSCRAPER
        mock_client_class.assert_called_once_with(api_key="test_api_key")

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    @patch.dict(os.environ, {"SCRAPEGRAPH_API_KEY": "env_api_key"})
    def test_tool_initialization_with_env_var(self, mock_client_class):
        """Test tool initialization with environment variable"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool()

        assert tool.api_key == "env_api_key"
        mock_client_class.assert_called_once_with(api_key="env_api_key")

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_tool_initialization_missing_api_key(self, mock_client_class):
        """Test tool initialization without API key raises ValueError"""
        with pytest.raises(ValueError, match="Scrapegraph API key is required"):
            ScrapegraphScrapeTool()

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_tool_initialization_with_fixed_url(self, mock_client_class):
        """Test tool initialization with fixed URL"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool(
            website_url="https://example.com",
            api_key="test_api_key"
        )

        assert tool.website_url == "https://example.com"
        assert "https://example.com" in tool.description

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_tool_initialization_with_custom_mode(self, mock_client_class):
        """Test tool initialization with custom scraping mode"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool(
            mode=ScrapingMode.CRAWL,
            api_key="test_api_key"
        )

        assert tool.mode == ScrapingMode.CRAWL

    def test_url_validation_valid(self):
        """Test URL validation with valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://test.org",
            "https://subdomain.example.com/path",
            "https://example.com:8080/path?query=value"
        ]

        for url in valid_urls:
            ScrapegraphScrapeTool._validate_url(url)  # Should not raise

    def test_url_validation_invalid(self):
        """Test URL validation with invalid URLs"""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",
            "example.com",
            "",
            "https://",
            "http://"
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid URL format"):
                ScrapegraphScrapeTool._validate_url(url)

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_smartscraper_mode(self, mock_client_class):
        """Test SmartScraper mode execution"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {
            "result": "Extracted content from webpage",
            "request_id": "test123"
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://example.com",
            mode=ScrapingMode.SMARTSCRAPER,
            user_prompt="Extract main content"
        )

        assert result == "Extracted content from webpage"
        mock_client.smartscraper.assert_called_once_with(
            website_url="https://example.com",
            user_prompt="Extract main content"
        )
        mock_client.close.assert_called_once()

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_smartscraper_with_schema(self, mock_client_class):
        """Test SmartScraper mode with output schema"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {
            "result": {"title": "Test Title", "content": "Test Content"}
        }

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            }
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://example.com",
            mode=ScrapingMode.SMARTSCRAPER,
            user_prompt="Extract structured data",
            output_schema=schema
        )

        assert result == {"title": "Test Title", "content": "Test Content"}
        mock_client.smartscraper.assert_called_once_with(
            website_url="https://example.com",
            user_prompt="Extract structured data",
            output_schema=schema
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_scrape_mode(self, mock_client_class):
        """Test basic scrape mode execution"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.scrape.return_value = {
            "result": "<html><body>Raw HTML content</body></html>",
            "request_id": "test123"
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://example.com",
            mode=ScrapingMode.SCRAPE,
            render_heavy_js=True
        )

        assert result == "<html><body>Raw HTML content</body></html>"
        mock_client.scrape.assert_called_once_with(
            website_url="https://example.com",
            render_heavy_js=True
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_scrape_mode_with_headers(self, mock_client_class):
        """Test basic scrape mode with custom headers"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.scrape.return_value = {
            "result": "<html><body>Content with headers</body></html>"
        }

        headers = {"User-Agent": "Custom Bot 1.0"}

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://example.com",
            mode=ScrapingMode.SCRAPE,
            headers=headers
        )

        assert result == "<html><body>Content with headers</body></html>"
        mock_client.scrape.assert_called_once_with(
            website_url="https://example.com",
            render_heavy_js=False,
            headers=headers
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_searchscraper_mode(self, mock_client_class):
        """Test SearchScraper mode execution"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.searchscraper.return_value = {
            "result": "Search results content",
            "reference_urls": ["https://url1.com", "https://url2.com"]
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            mode=ScrapingMode.SEARCHSCRAPER,
            user_prompt="What is the latest Python version?",
            num_results=5
        )

        assert result == "Search results content"
        mock_client.searchscraper.assert_called_once_with(
            user_prompt="What is the latest Python version?",
            num_results=5
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_agenticscraper_mode(self, mock_client_class):
        """Test AgenticScraper mode execution"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.agenticscraper.return_value = {
            "result": "Automated interaction result",
            "status": "success"
        }

        steps = [
            "Type user@example.com in email field",
            "Type password in password field",
            "Click login button"
        ]

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://dashboard.example.com",
            mode=ScrapingMode.AGENTICSCRAPER,
            steps=steps,
            use_session=True,
            user_prompt="Extract user profile data",
            ai_extraction=True
        )

        assert result == "Automated interaction result"
        mock_client.agenticscraper.assert_called_once_with(
            url="https://dashboard.example.com",
            steps=steps,
            use_session=True,
            ai_extraction=True,
            user_prompt="Extract user profile data"
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_agenticscraper_without_ai_extraction(self, mock_client_class):
        """Test AgenticScraper mode without AI extraction"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.agenticscraper.return_value = {
            "result": "Raw automation result"
        }

        steps = ["Click element"]

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://example.com",
            mode=ScrapingMode.AGENTICSCRAPER,
            steps=steps,
            ai_extraction=False
        )

        assert result == "Raw automation result"
        mock_client.agenticscraper.assert_called_once_with(
            url="https://example.com",
            steps=steps,
            use_session=False,
            ai_extraction=False
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_crawl_mode(self, mock_client_class):
        """Test Crawl mode execution"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.crawl.return_value = {
            "result": "Multi-page crawl results",
            "pages_crawled": 5
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://blog.example.com",
            mode=ScrapingMode.CRAWL,
            user_prompt="Extract article titles and authors",
            depth=2,
            max_pages=10,
            same_domain_only=True,
            cache_website=True
        )

        assert result == "Multi-page crawl results"
        mock_client.crawl.assert_called_once_with(
            url="https://blog.example.com",
            prompt="Extract article titles and authors",
            depth=2,
            max_pages=10,
            same_domain_only=True,
            cache_website=True
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_crawl_with_schema(self, mock_client_class):
        """Test Crawl mode with data schema"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.crawl.return_value = {
            "result": [{"title": "Article 1", "author": "Author 1"}]
        }

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "author": {"type": "string"}
                }
            }
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://blog.example.com",
            mode=ScrapingMode.CRAWL,
            user_prompt="Extract articles",
            output_schema=schema
        )

        assert result == [{"title": "Article 1", "author": "Author 1"}]
        mock_client.crawl.assert_called_once_with(
            url="https://blog.example.com",
            prompt="Extract articles",
            depth=1,
            max_pages=5,
            same_domain_only=True,
            cache_website=False,
            data_schema=schema
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_markdownify_mode(self, mock_client_class):
        """Test Markdownify mode execution"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.markdownify.return_value = {
            "result": "# Article Title\n\nThis is the content in markdown format."
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")
        result = tool.run(
            website_url="https://example.com/article",
            mode=ScrapingMode.MARKDOWNIFY
        )

        assert result == "# Article Title\n\nThis is the content in markdown format."
        mock_client.markdownify.assert_called_once_with(
            website_url="https://example.com/article"
        )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_error_handling_empty_response(self, mock_client_class):
        """Test error handling for empty API response"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {}

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(RuntimeError, match="Empty response from Scrapegraph API"):
            tool.run(
                website_url="https://example.com",
                mode=ScrapingMode.SMARTSCRAPER
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_error_handling_api_error(self, mock_client_class):
        """Test error handling for API errors"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {
            "error": {"message": "API key invalid"}
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(RuntimeError, match="API error: API key invalid"):
            tool.run(
                website_url="https://example.com",
                mode=ScrapingMode.SMARTSCRAPER
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_error_handling_rate_limit(self, mock_client_class):
        """Test error handling for rate limit errors"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {
            "error": {"message": "Rate limit exceeded. Please try again later."}
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            tool.run(
                website_url="https://example.com",
                mode=ScrapingMode.SMARTSCRAPER
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_error_handling_invalid_response_format(self, mock_client_class):
        """Test error handling for invalid response format"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {
            "status": "success"
            # Missing 'result' key
        }

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(RuntimeError, match="Invalid response format"):
            tool.run(
                website_url="https://example.com",
                mode=ScrapingMode.SMARTSCRAPER
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_error_handling_client_exception(self, mock_client_class):
        """Test error handling for client exceptions"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.side_effect = Exception("Network connection failed")

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(RuntimeError, match="Scraping failed: Network connection failed"):
            tool.run(
                website_url="https://example.com",
                mode=ScrapingMode.SMARTSCRAPER
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_missing_website_url_for_modes_requiring_it(self, mock_client_class):
        """Test error when website_url is missing for modes that require it"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(ValueError, match="website_url is required for this mode"):
            tool.run(mode=ScrapingMode.SMARTSCRAPER)

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_missing_user_prompt_for_searchscraper(self, mock_client_class):
        """Test error when user_prompt is missing for searchscraper mode"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(ValueError, match="user_prompt is required for searchscraper mode"):
            tool.run(mode=ScrapingMode.SEARCHSCRAPER)

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_unsupported_mode(self, mock_client_class):
        """Test error handling for unsupported scraping modes"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(ValueError, match="Unsupported scraping mode"):
            tool.run(
                website_url="https://example.com",
                mode="invalid_mode"
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_client_always_closed(self, mock_client_class):
        """Test that client is always closed, even on errors"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.side_effect = Exception("Test error")

        tool = ScrapegraphScrapeTool(api_key="test_api_key")

        with pytest.raises(RuntimeError):
            tool.run(
                website_url="https://example.com",
                mode=ScrapingMode.SMARTSCRAPER
            )

        mock_client.close.assert_called_once()

    def test_schema_validation(self):
        """Test schema validation"""
        # Valid schema
        valid_data = {
            "website_url": "https://example.com",
            "mode": ScrapingMode.SMARTSCRAPER,
            "user_prompt": "Extract content"
        }
        schema = ScrapegraphScrapeToolSchema(**valid_data)
        assert schema.website_url == "https://example.com"
        assert schema.mode == ScrapingMode.SMARTSCRAPER

        # Invalid URL
        with pytest.raises(ValueError):
            ScrapegraphScrapeToolSchema(
                website_url="invalid_url",
                mode=ScrapingMode.SMARTSCRAPER
            )

    @patch("crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client")
    def test_fixed_url_tool_usage(self, mock_client_class):
        """Test tool with fixed URL configured during initialization"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.smartscraper.return_value = {
            "result": "Fixed URL content"
        }

        tool = ScrapegraphScrapeTool(
            website_url="https://fixed.example.com",
            api_key="test_api_key"
        )

        result = tool.run(user_prompt="Extract from fixed URL")

        assert result == "Fixed URL content"
        mock_client.smartscraper.assert_called_once_with(
            website_url="https://fixed.example.com",
            user_prompt="Extract from fixed URL"
        )