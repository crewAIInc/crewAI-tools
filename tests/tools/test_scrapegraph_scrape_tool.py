import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

from crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool import (
    ScrapegraphScrapeTool,
    ScrapegraphScrapeToolSchema,
    FixedScrapegraphScrapeToolSchema,
    ScrapeMethod,
    ScrapegraphError,
    RateLimitError,
)


class TestScrapegraphScrapeToolSchema:
    """Test the schema validation"""

    def test_valid_url(self):
        schema = ScrapegraphScrapeToolSchema(
            website_url="https://example.com",
            user_prompt="Test prompt"
        )
        assert schema.website_url == "https://example.com"
        assert schema.user_prompt == "Test prompt"

    def test_invalid_url_format(self):
        with pytest.raises(ValidationError, match="Invalid URL format"):
            ScrapegraphScrapeToolSchema(website_url="not-a-url")

    def test_invalid_num_results(self):
        with pytest.raises(ValidationError, match="num_results must be between 1 and 20"):
            ScrapegraphScrapeToolSchema(
                website_url="https://example.com",
                num_results=25
            )

    def test_invalid_depth(self):
        with pytest.raises(ValidationError, match="depth must be between 1 and 5"):
            ScrapegraphScrapeToolSchema(
                website_url="https://example.com",
                depth=10
            )

    def test_invalid_timeout(self):
        with pytest.raises(ValidationError, match="timeout must be between 10 and 600"):
            ScrapegraphScrapeToolSchema(
                website_url="https://example.com",
                timeout=1000
            )

    def test_default_values(self):
        schema = ScrapegraphScrapeToolSchema(website_url="https://example.com")
        assert schema.method == ScrapeMethod.SMARTSCRAPER
        assert schema.render_heavy_js is False
        assert schema.num_results == 3
        assert schema.depth == 1
        assert schema.same_domain_only is True


class TestScrapegraphScrapeTool:
    """Test the main tool functionality"""

    @pytest.fixture
    def mock_client(self):
        with patch('crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool.Client') as mock:
            client_instance = Mock()
            mock.return_value = client_instance
            yield client_instance

    @pytest.fixture
    def tool_with_api_key(self, mock_client):
        with patch.dict(os.environ, {'SCRAPEGRAPH_API_KEY': 'test-api-key'}):
            return ScrapegraphScrapeTool()

    def test_initialization_without_api_key(self, mock_client):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Scrapegraph API key is required"):
                ScrapegraphScrapeTool()

    def test_initialization_with_api_key(self, mock_client):
        with patch.dict(os.environ, {'SCRAPEGRAPH_API_KEY': 'test-key'}):
            tool = ScrapegraphScrapeTool()
            assert tool.api_key == 'test-key'

    def test_initialization_with_fixed_url(self, mock_client):
        with patch.dict(os.environ, {'SCRAPEGRAPH_API_KEY': 'test-key'}):
            tool = ScrapegraphScrapeTool(website_url="https://example.com")
            assert tool.website_url == "https://example.com"
            assert tool.args_schema == FixedScrapegraphScrapeToolSchema

    def test_invalid_url_initialization(self, mock_client):
        with patch.dict(os.environ, {'SCRAPEGRAPH_API_KEY': 'test-key'}):
            with pytest.raises(ValueError, match="Invalid URL format"):
                ScrapegraphScrapeTool(website_url="invalid-url")

    def test_smartscraper_method(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.return_value = {"result": "Extracted content"}

        result = tool_with_api_key.run(
            website_url="https://example.com",
            method=ScrapeMethod.SMARTSCRAPER,
            user_prompt="Extract content"
        )

        assert result == "Extracted content"
        mock_client.smartscraper.assert_called_once_with(
            website_url="https://example.com",
            user_prompt="Extract content",
            data_schema=None
        )
        mock_client.close.assert_called_once()

    def test_searchscraper_method(self, tool_with_api_key, mock_client):
        mock_client.searchscraper.return_value = {
            "result": "Search results",
            "reference_urls": ["https://source1.com", "https://source2.com"]
        }

        result = tool_with_api_key.run(
            method=ScrapeMethod.SEARCHSCRAPER,
            user_prompt="Search for information",
            num_results=5
        )

        expected = {
            "result": "Search results",
            "reference_urls": ["https://source1.com", "https://source2.com"]
        }
        assert result == expected
        mock_client.searchscraper.assert_called_once_with(
            user_prompt="Search for information",
            num_results=5
        )

    def test_agenticscraper_method(self, tool_with_api_key, mock_client):
        mock_client.agenticscraper.return_value = {"result": "Agentic result"}

        steps = ["Click login button", "Enter credentials"]
        result = tool_with_api_key.run(
            website_url="https://example.com",
            method=ScrapeMethod.AGENTICSCRAPER,
            steps=steps,
            use_session=True,
            ai_extraction=True,
            user_prompt="Extract after login"
        )

        assert result == "Agentic result"
        mock_client.agenticscraper.assert_called_once_with(
            url="https://example.com",
            steps=steps,
            use_session=True,
            ai_extraction=True,
            user_prompt="Extract after login"
        )

    def test_agenticscraper_missing_steps(self, tool_with_api_key):
        with pytest.raises(ValueError, match="steps parameter is required for agentic scraping"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.AGENTICSCRAPER
            )

    def test_crawl_method(self, tool_with_api_key, mock_client):
        mock_client.crawl.return_value = {"result": "Crawl result"}

        result = tool_with_api_key.run(
            website_url="https://example.com",
            method=ScrapeMethod.CRAWL,
            user_prompt="Crawl website",
            depth=2,
            max_pages=5,
            same_domain_only=True
        )

        assert result == "Crawl result"
        mock_client.crawl.assert_called_once_with(
            url="https://example.com",
            prompt="Crawl website",
            depth=2,
            max_pages=5,
            same_domain_only=True,
            cache_website=False
        )

    def test_scrape_method(self, tool_with_api_key, mock_client):
        mock_client.scrape.return_value = {"html": "<html>Content</html>"}

        result = tool_with_api_key.run(
            website_url="https://example.com",
            method=ScrapeMethod.SCRAPE,
            render_heavy_js=True,
            headers={"User-Agent": "test"}
        )

        assert result == "<html>Content</html>"
        mock_client.scrape.assert_called_once_with(
            website_url="https://example.com",
            render_heavy_js=True,
            headers={"User-Agent": "test"}
        )

    def test_markdownify_method(self, tool_with_api_key, mock_client):
        mock_client.markdownify.return_value = {"result": "# Markdown content"}

        result = tool_with_api_key.run(
            website_url="https://example.com",
            method=ScrapeMethod.MARKDOWNIFY
        )

        assert result == "# Markdown content"
        mock_client.markdownify.assert_called_once_with(website_url="https://example.com")

    def test_missing_website_url(self, tool_with_api_key):
        with pytest.raises(ValueError, match="website_url is required for this method"):
            tool_with_api_key.run(method=ScrapeMethod.SMARTSCRAPER)

    def test_invalid_method(self, tool_with_api_key):
        with pytest.raises(ValueError, match="Unsupported scraping method"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method="invalid_method"
            )

    def test_rate_limit_error(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.return_value = {
            "error": {"message": "Rate limit exceeded"}
        }

        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.SMARTSCRAPER
            )

    def test_api_error(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.return_value = {
            "error": {"message": "API error occurred"}
        }

        with pytest.raises(RuntimeError, match="API error: API error occurred"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.SMARTSCRAPER
            )

    def test_empty_response(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.return_value = {}

        with pytest.raises(RuntimeError, match="Empty response from ScrapeGraph API"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.SMARTSCRAPER
            )

    def test_missing_result_in_response(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.return_value = {"status": "success"}

        with pytest.raises(RuntimeError, match="Invalid response format"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.SMARTSCRAPER
            )

    def test_async_crawl_success(self, tool_with_api_key, mock_client):
        # Simulate async crawl with polling
        mock_client.crawl.return_value = {"id": "task123"}
        mock_client.get_crawl.return_value = {
            "status": "success",
            "result": {"llm_result": "Final crawl result"}
        }

        with patch('time.sleep'):  # Mock sleep to speed up test
            result = tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.CRAWL,
                user_prompt="Crawl website"
            )

        assert result == "Final crawl result"
        mock_client.get_crawl.assert_called_with("task123")

    def test_async_crawl_failure(self, tool_with_api_key, mock_client):
        mock_client.crawl.return_value = {"id": "task123"}
        mock_client.get_crawl.return_value = {
            "status": "failed",
            "error": "Crawl failed"
        }

        with patch('time.sleep'):
            with pytest.raises(RuntimeError, match="Crawl operation failed: Crawl failed"):
                tool_with_api_key.run(
                    website_url="https://example.com",
                    method=ScrapeMethod.CRAWL
                )

    def test_client_close_called_on_exception(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.side_effect = Exception("Network error")

        with pytest.raises(RuntimeError, match="Scraping failed"):
            tool_with_api_key.run(
                website_url="https://example.com",
                method=ScrapeMethod.SMARTSCRAPER
            )

        mock_client.close.assert_called_once()

    def test_schema_with_data_schema(self, tool_with_api_key, mock_client):
        mock_client.smartscraper.return_value = {"result": "Structured data"}

        data_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            }
        }

        result = tool_with_api_key.run(
            website_url="https://example.com",
            method=ScrapeMethod.SMARTSCRAPER,
            data_schema=data_schema
        )

        assert result == "Structured data"
        mock_client.smartscraper.assert_called_once_with(
            website_url="https://example.com",
            user_prompt="Extract the main content of the webpage",
            data_schema=data_schema
        )


class TestScrapeMethod:
    """Test the ScrapeMethod enum"""

    def test_all_methods_defined(self):
        expected_methods = [
            "smartscraper",
            "searchscraper",
            "agenticscraper",
            "crawl",
            "scrape",
            "markdownify"
        ]

        actual_methods = [method.value for method in ScrapeMethod]
        assert set(expected_methods) == set(actual_methods)


if __name__ == "__main__":
    pytest.main([__file__])