import unittest
import sys
from unittest.mock import MagicMock, patch

mock_firecrawl = MagicMock()
mock_firecrawl_app = MagicMock()
mock_firecrawl.FirecrawlApp = mock_firecrawl_app
sys.modules['firecrawl'] = mock_firecrawl

from crewai_tools import FirecrawlScrapeWebsiteTool


class TestIssue2783(unittest.TestCase):
    def setUp(self):
        self.mock_instance = MagicMock()
        self.mock_instance.scrape_url.return_value = "mocked response"
        mock_firecrawl_app.return_value = self.mock_instance

    def test_run_with_url_parameter(self):
        tool = FirecrawlScrapeWebsiteTool(api_key="test_key")
        result = tool.run(url="example.com")

        self.mock_instance.scrape_url.assert_called_once()
        args, kwargs = self.mock_instance.scrape_url.call_args
        self.assertEqual(len(args), 1)  # Only one positional argument (url)
        self.assertEqual(args[0], "example.com")
        self.assertEqual(result, "mocked response")

    def test_init_with_url_parameter(self):
        tool = FirecrawlScrapeWebsiteTool(api_key="test_key", url="example.com")
        
        result = tool.run()
        
        self.mock_instance.scrape_url.assert_called_once()
        args, kwargs = self.mock_instance.scrape_url.call_args
        self.assertEqual(len(args), 1)  # Only one positional argument (url)
        self.assertEqual(args[0], "example.com")
        self.assertEqual(result, "mocked response")

    def test_init_and_run_with_url_parameter(self):
        tool = FirecrawlScrapeWebsiteTool(api_key="test_key", url="example.com")
        
        result = tool.run(url="different-example.com")
        
        self.mock_instance.scrape_url.assert_called_once()
        args, kwargs = self.mock_instance.scrape_url.call_args
        self.assertEqual(len(args), 1)  # Only one positional argument (url)
        self.assertEqual(args[0], "different-example.com")
        self.assertEqual(result, "mocked response")

    def test_no_url_parameter(self):
        tool = FirecrawlScrapeWebsiteTool(api_key="test_key")
        
        with self.assertRaises(ValueError):
            tool.run()
