import unittest
import sys
from unittest.mock import patch, MagicMock

# Mock the firecrawl module before importing FirecrawlCrawlWebsiteTool
with patch.dict('sys.modules', {'firecrawl': MagicMock()}):
    from crewai_tools import FirecrawlCrawlWebsiteTool


class TestFirecrawlCrawlWebsiteTool(unittest.TestCase):
    @patch('firecrawl.FirecrawlApp')
    @patch('click.confirm', return_value=False)
    def test_crawl_url_calls_with_correct_arguments(self, mock_confirm, mock_firecrawl_app):
        mock_instance = MagicMock()
        mock_firecrawl_app.return_value = mock_instance
        
        tool = FirecrawlCrawlWebsiteTool(api_key="test_key")
        
        url = "https://example.com"
        tool._run(url=url)
        
        mock_instance.crawl_url.assert_called_once()
        args, kwargs = mock_instance.crawl_url.call_args
        
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0], url)
        
        self.assertIn("maxDepth", kwargs)
        self.assertIn("limit", kwargs)
        self.assertIn("allowExternalLinks", kwargs)
        self.assertIn("scrapeOptions", kwargs)


if __name__ == "__main__":
    unittest.main()
