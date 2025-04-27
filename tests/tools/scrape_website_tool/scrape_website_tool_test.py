import unittest
from unittest.mock import MagicMock, patch

from crewai_tools.tools.scrape_website_tool.scrape_website_tool import ScrapeWebsiteTool


class TestScrapeWebsiteTool(unittest.TestCase):
    @patch("requests.get")
    def test_scrape_website_normal(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Test content</p></body></html>"
        mock_response.apparent_encoding = "utf-8"
        mock_get.return_value = mock_response

        tool = ScrapeWebsiteTool()
        with patch.object(tool, '_count_tokens', return_value=500):
            result = tool._run(website_url="https://example.com")
        
        self.assertIn("Test content", result)
        self.assertNotIn("Content truncated", result)

    @patch("requests.get")
    def test_scrape_website_truncate(self, mock_get):
        mock_response = MagicMock()
        large_content = "<html><body>" + "<p>Long content</p>" * 1000 + "</body></html>"
        mock_response.text = large_content
        mock_response.apparent_encoding = "utf-8"
        mock_get.return_value = mock_response

        tool = ScrapeWebsiteTool(max_tokens=1000)
        with patch.object(tool, '_count_tokens', return_value=10000):
            result = tool._run(website_url="https://example.com")
        
        self.assertIn("Content truncated", result)
        self.assertIn("to 1000 tokens from original 10000 tokens", result)

    def test_count_tokens(self):
        tool = ScrapeWebsiteTool()
        test_text = "This is a test text for token counting."
        
        token_count = tool._count_tokens(test_text)
        self.assertGreater(token_count, 0)

    @patch("requests.get")
    def test_custom_max_tokens(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Test content</p></body></html>"
        mock_response.apparent_encoding = "utf-8"
        mock_get.return_value = mock_response

        custom_max = 500
        tool = ScrapeWebsiteTool(max_tokens=custom_max)
        with patch.object(tool, '_count_tokens', return_value=1000):
            result = tool._run(website_url="https://example.com")
        
        self.assertIn(f"to {custom_max} tokens", result)
