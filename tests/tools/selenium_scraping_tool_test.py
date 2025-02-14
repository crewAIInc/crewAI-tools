import pytest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

from crewai_tools.tools.selenium_scraping_tool.selenium_scraping_tool import (
    SeleniumScrapingTool,
)


def mock_driver_with_html(html_content):
    driver = MagicMock()
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = html_content
    bs = BeautifulSoup(html_content, "html.parser")
    mock_element.text = bs.get_text()

    driver.find_elements.return_value = [mock_element]
    driver.find_element.return_value = mock_element

    return driver


def initialize_tool_with(mock_driver):
    tool = SeleniumScrapingTool()
    tool.driver = MagicMock(return_value=mock_driver)

    return tool


def test_tool_initialization():
    tool = SeleniumScrapingTool()

    assert tool.website_url is None
    assert tool.css_element is None
    assert tool.cookie is None
    assert tool.wait_time == 3
    assert tool.return_html is False


@patch("selenium.webdriver.Chrome")
def test_scrape_without_css_selector(_mocked_chrome_driver):
    html_content = "<html><body><div>test content</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    result = tool._run(website_url="https://example.com")

    assert "test content" in result
    mock_driver.get.assert_called_once_with("https://example.com")
    mock_driver.find_element.assert_called_with("tag name", "body")
    mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_scrape_with_css_selector(_mocked_chrome_driver):
    html_content = "<html><body><div>test content</div><div class='test'>test content in a specific div</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    result = tool._run(website_url="https://example.com", css_element="div.test")

    assert "test content in a specific div" in result
    mock_driver.get.assert_called_once_with("https://example.com")
    mock_driver.find_elements.assert_called_with("css selector", "div.test")
    mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_scrape_with_return_html_true(_mocked_chrome_driver):
    html_content = "<html><body><div>HTML content</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    result = tool._run(website_url="https://example.com", return_html=True)

    assert html_content in result
    mock_driver.get.assert_called_once_with("https://example.com")
    mock_driver.find_element.assert_called_with("tag name", "body")
    mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_scrape_with_return_html_false(_mocked_chrome_driver):
    html_content = "<html><body><div>HTML content</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    result = tool._run(website_url="https://example.com", return_html=False)

    assert "HTML content" in result
    mock_driver.get.assert_called_once_with("https://example.com")
    mock_driver.find_element.assert_called_with("tag name", "body")
    mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_webdriver_initialization(_mocked_chrome_driver):
    """Test that WebDriver is properly initialized in SeleniumScrapingTool."""
    tool = SeleniumScrapingTool()
    assert tool.driver is not None
    assert isinstance(tool.driver, MagicMock)
    _mocked_chrome_driver.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_webdriver_initialization_error(_mocked_chrome_driver):
    """Test WebDriver initialization error handling."""
    _mocked_chrome_driver.side_effect = Exception("Driver error")
    tool = SeleniumScrapingTool()
    with pytest.raises(RuntimeError) as exc_info:
        _ = tool.driver
    assert "Failed to initialize WebDriver" in str(exc_info.value)


@patch("selenium.webdriver.Chrome")
def test_cookie_handling(_mocked_chrome_driver):
    """Test cookie setting functionality."""
    mock_driver = MagicMock()
    _mocked_chrome_driver.return_value = mock_driver
    cookie = {"name": "test", "value": "value"}
    
    tool = SeleniumScrapingTool(cookie=cookie)
    tool._create_driver("https://example.com", cookie, 1)
    
    mock_driver.add_cookie.assert_called_once_with(cookie)
    mock_driver.get.assert_called_with("https://example.com")


@patch("selenium.webdriver.Chrome")
def test_context_manager(_mocked_chrome_driver):
    """Test context manager functionality."""
    mock_driver = MagicMock()
    _mocked_chrome_driver.return_value = mock_driver
    
    with SeleniumScrapingTool() as tool:
        tool.driver.get("https://example.com")
    
    mock_driver.quit.assert_called_once()
    assert tool._driver is None


@patch("selenium.webdriver.Chrome")
def test_page_load_timeout(_mocked_chrome_driver):
    """Test page load timeout handling."""
    mock_driver = MagicMock()
    _mocked_chrome_driver.return_value = mock_driver
    mock_driver.get.side_effect = Exception("Timeout")
    
    tool = SeleniumScrapingTool()
    with pytest.raises(RuntimeError) as exc_info:
        tool._create_driver("https://example.com", None, 1)
    assert "Failed to load page" in str(exc_info.value)
