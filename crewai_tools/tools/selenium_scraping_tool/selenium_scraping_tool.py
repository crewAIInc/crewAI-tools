import re
import time
from typing import Any, Optional, Type
from urllib.parse import urlparse

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, validator


class FixedSeleniumScrapingToolSchema(BaseModel):
    """Input for SeleniumScrapingTool."""


class SeleniumScrapingToolSchema(FixedSeleniumScrapingToolSchema):
    """Input for SeleniumScrapingTool."""

    website_url: str = Field(
        ...,
        description="Mandatory website url to read the file. Must start with http:// or https://",
    )
    css_element: str = Field(
        ...,
        description="Mandatory css reference for element to scrape from the website",
    )

    @validator("website_url")
    def validate_website_url(cls, v):
        if not v:
            raise ValueError("Website URL cannot be empty")

        if len(v) > 2048:  # Common maximum URL length
            raise ValueError("URL is too long (max 2048 characters)")

        if not re.match(r"^https?://", v):
            raise ValueError("URL must start with http:// or https://")

        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")

        if re.search(r"\s", v):
            raise ValueError("URL cannot contain whitespace")

        return v


class SeleniumScrapingTool(BaseTool):
    """A tool for scraping web content using Selenium WebDriver.
    
    This tool provides functionality to scrape content from websites, particularly
    those requiring JavaScript execution. It supports:
    - Lazy WebDriver initialization
    - Cookie handling
    - Custom CSS selectors for targeted scraping
    - Configurable headless mode
    - Context manager interface for proper resource cleanup
    
    Attributes:
        name (str): Name of the tool
        description (str): Description of the tool's functionality
        website_url (Optional[str]): URL to scrape
        cookie (Optional[dict]): Cookie to set for requests
        wait_time (int): Maximum time to wait for page loads in seconds
        css_element (Optional[str]): CSS selector to target specific elements
        return_html (bool): Whether to return HTML content instead of text
        headless (bool): Whether to run Chrome in headless mode
    """
    name: str = "Read a website content"
    description: str = "A tool that can be used to read a website content."
    args_schema: Type[BaseModel] = SeleniumScrapingToolSchema
    
    # Public configuration
    website_url: Optional[str] = None  # URL to scrape
    cookie: Optional[dict] = None  # Cookie format: {"name": str, "value": str, ...}
    wait_time: int = 10  # Maximum time to wait for page loads in seconds
    css_element: Optional[str] = None  # CSS selector for targeting elements
    return_html: bool = False  # Whether to return HTML instead of text
    headless: bool = True  # Whether to run Chrome in headless mode
    chrome_options: Optional[list] = None  # Additional Chrome options to pass to WebDriver
    
    # Private attributes
    _driver: Optional[Any] = None  # Lazy-loaded WebDriver instance
    _options: Optional[Any] = None  # Chrome options instance
    _by: Optional[Any] = None  # Selenium By class for element location

    def __init__(
        self,
        website_url: Optional[str] = None,
        cookie: Optional[dict] = None,
        css_element: Optional[str] = None,
        headless: bool = True,
        **kwargs,
    ):
        """Initialize SeleniumScrapingTool.
        
        Args:
            website_url: Optional URL to scrape
            cookie: Optional cookie to set for requests
            css_element: Optional CSS selector to target specific elements
            headless: Whether to run Chrome in headless mode (default: True)
            **kwargs: Additional arguments passed to BaseTool
        """
        super().__init__(**kwargs)
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Store selenium modules as instance variables
            self._webdriver = webdriver
            self._Options = Options
            self._By = By
            self._WebDriverWait = WebDriverWait
            self._EC = EC
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'selenium' package. Would you like to install it?"
            ):
                import subprocess
                subprocess.run(
                    ["uv", "pip", "install", "selenium"],
                    check=True,
                )
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                # Store selenium modules as instance variables
                self._webdriver = webdriver
                self._Options = Options
                self._By = By
                self._WebDriverWait = WebDriverWait
                self._EC = EC
            else:
                raise ImportError(
                    "`selenium` package not found, please run `uv add selenium`"
                )
        
        self._options = self._Options()
        if headless:
            self._options.add_argument("--headless")
        self.headless = headless
        self._by = self._By
        if cookie is not None:
            self.cookie = cookie

        if css_element is not None:
            self.css_element = css_element

        if website_url is not None:
            self.website_url = website_url
            self.description = (
                f"A tool that can be used to read {website_url}'s content."
            )
            self.args_schema = FixedSeleniumScrapingToolSchema

        self._generate_description()

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        """Execute the web scraping operation.
        
        Args:
            **kwargs: Keyword arguments including:
                website_url (str): URL to scrape
                css_element (str): CSS selector for targeting elements
                return_html (bool): Whether to return HTML instead of text
                
        Returns:
            str: Scraped content joined with newlines
        """
        website_url = kwargs.get("website_url", self.website_url)
        css_element = kwargs.get("css_element", self.css_element)
        return_html = kwargs.get("return_html", self.return_html)
        driver = self._create_driver(website_url, self.cookie, self.wait_time)

        content = self._get_content(driver, css_element, return_html)
        driver.close()

        return "\n".join(content)

    def _get_content(self, driver: Any, css_element: Optional[str], return_html: bool) -> list:
        """Get content from the webpage using optional CSS selector.
        
        Args:
            driver: WebDriver instance
            css_element: Optional CSS selector to target specific elements
            return_html: Whether to return HTML content instead of text
            
        Returns:
            list: List of scraped content strings
        """
        content = []

        if self._is_css_element_empty(css_element):
            content.append(self._get_body_content(driver, return_html))
        else:
            content.extend(self._get_elements_content(driver, css_element, return_html))

        return content

    def _is_css_element_empty(self, css_element: Optional[str]) -> bool:
        """Check if CSS selector is empty or None.
        
        Args:
            css_element: CSS selector to check
            
        Returns:
            bool: True if selector is empty or None
        """
        return css_element is None or css_element.strip() == ""

    def _get_body_content(self, driver: Any, return_html: bool) -> str:
        """Get content from the page body.
        
        Args:
            driver: WebDriver instance
            return_html: Whether to return HTML content
            
        Returns:
            str: Body content as HTML or text
        """
        body_element = driver.find_element(self._by.TAG_NAME, "body")

        return (
            body_element.get_attribute("outerHTML")
            if return_html
            else body_element.text
        )

    def _get_elements_content(self, driver: Any, css_element: str, return_html: bool) -> list:
        """Get content from elements matching CSS selector.
        
        Args:
            driver: WebDriver instance
            css_element: CSS selector to target elements
            return_html: Whether to return HTML content
            
        Returns:
            list: List of element contents as HTML or text
        """
        elements_content = []

        for element in driver.find_elements(self._by.CSS_SELECTOR, css_element):
            elements_content.append(
                element.get_attribute("outerHTML") if return_html else element.text
            )

        return elements_content

    def _create_driver(self, url: str, cookie: Optional[dict], wait_time: int) -> Any:
        """Create and configure a WebDriver instance.
        
        Args:
            url: The URL to navigate to
            cookie: Optional cookie to set
            wait_time: Maximum time to wait for page load in seconds
            
        Returns:
            Configured WebDriver instance
            
        Raises:
            ValueError: If URL is empty or invalid
            RuntimeError: If page load or cookie setting fails
        """
        if not url:
            raise ValueError("URL cannot be empty")

        if not re.match(r"^https?://", url):
            raise ValueError("URL must start with http:// or https://")

        self.driver.get(url)
        wait = self._WebDriverWait(self.driver, wait_time)
        try:
            wait.until(self._EC.presence_of_element_located((self._By.TAG_NAME, "body")))
        except Exception as e:
            raise RuntimeError(f"Failed to load page: {str(e)}")

        if cookie:
            try:
                self.driver.add_cookie(cookie)
                self.driver.get(url)  # Reload with cookie
                wait.until(self._EC.presence_of_element_located((self._By.TAG_NAME, "body")))
            except Exception as e:
                raise RuntimeError(f"Failed to set cookie: {str(e)}")

        return self.driver

    @property
    def driver(self) -> Any:
        """Lazily initialize and return the WebDriver instance.
        
        Returns:
            Chrome WebDriver instance
            
        Raises:
            RuntimeError: If WebDriver initialization fails
        """
        if self._driver is None:
            try:
                self._driver = self._webdriver.Chrome(options=self._options)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize WebDriver: {str(e)}")
        return self._driver

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper cleanup."""
        self.close()

    def close(self):
        """Close the WebDriver and clean up resources."""
        if self._driver is not None:
            try:
                self._driver.quit()
            finally:
                self._driver = None
