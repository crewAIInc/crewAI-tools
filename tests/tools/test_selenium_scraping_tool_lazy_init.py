import pytest
from unittest.mock import patch, MagicMock

# Mock selenium module before importing SeleniumScrapingTool
with patch.dict('sys.modules', {'selenium': MagicMock(), 'selenium.webdriver': MagicMock(), 'selenium.webdriver.chrome.options': MagicMock(), 'selenium.webdriver.common.by': MagicMock()}):
    from crewai_tools.tools.selenium_scraping_tool.selenium_scraping_tool import (
        SeleniumScrapingTool,
    )

def test_lazy_initialization():
    """Test that the WebDriver is only initialized when needed."""
    # Creating the tool should not initialize Chrome
    tool = SeleniumScrapingTool()
    
    # The driver should be None initially
    assert tool.driver is None
    
    # Mock the _create_driver method to avoid actual WebDriver creation
    # and also mock the _get_content method to return a list of strings
    with patch.object(tool, '_create_driver', return_value=MagicMock()) as mock_create_driver:
        with patch.object(tool, '_get_content', return_value=["mocked content"]):
            tool._run(website_url="https://example.com")
            mock_create_driver.assert_called_once()
