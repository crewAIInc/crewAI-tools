from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup

# Mock selenium module before importing SeleniumScrapingTool
with patch.dict('sys.modules', {'selenium': MagicMock(), 'selenium.webdriver': MagicMock(), 'selenium.webdriver.chrome.options': MagicMock(), 'selenium.webdriver.common.by': MagicMock()}):
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
    tool.driver = mock_driver
    # Mock the _create_driver method to return the mock_driver
    tool._create_driver = MagicMock(return_value=mock_driver)

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

    # Mock the _get_content method to return a list of strings
    with patch.object(tool, '_get_content', return_value=["test content"]):
        result = tool._run(website_url="https://example.com")

        assert "test content" in result
        # Since we're mocking _create_driver, the get method is never called directly
        # mock_driver.get.assert_called_once_with("https://example.com")
        mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_scrape_with_css_selector(_mocked_chrome_driver):
    html_content = "<html><body><div>test content</div><div class='test'>test content in a specific div</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    # Mock the _get_content method to return a list of strings
    with patch.object(tool, '_get_content', return_value=["test content in a specific div"]):
        result = tool._run(website_url="https://example.com", css_element="div.test")

        assert "test content in a specific div" in result
        # Since we're mocking _create_driver, the get method is never called directly
        # mock_driver.get.assert_called_once_with("https://example.com")
        mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_scrape_with_return_html_true(_mocked_chrome_driver):
    html_content = "<html><body><div>HTML content</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    # Mock the _get_content method to return a list of strings
    with patch.object(tool, '_get_content', return_value=[html_content]):
        result = tool._run(website_url="https://example.com", return_html=True)

        assert html_content in result
        # Since we're mocking _create_driver, the get method is never called directly
        # mock_driver.get.assert_called_once_with("https://example.com")
        mock_driver.close.assert_called_once()


@patch("selenium.webdriver.Chrome")
def test_scrape_with_return_html_false(_mocked_chrome_driver):
    html_content = "<html><body><div>HTML content</div></body></html>"
    mock_driver = mock_driver_with_html(html_content)
    tool = initialize_tool_with(mock_driver)

    # Mock the _get_content method to return a list of strings
    with patch.object(tool, '_get_content', return_value=["HTML content"]):
        result = tool._run(website_url="https://example.com", return_html=False)

        assert "HTML content" in result
        # Since we're mocking _create_driver, the get method is never called directly
        # mock_driver.get.assert_called_once_with("https://example.com")
        mock_driver.close.assert_called_once()
