# Standard library imports
import os
import re
import time
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type
from urllib.parse import urlparse

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, validator

# Local imports
from crewai.tools import BaseTool

# Type checking imports
if TYPE_CHECKING:
    from firecrawl import FirecrawlApp  # type: ignore


class FirecrawlCrawlWebsiteToolSchema(BaseModel):
    url: str = Field(
        description="Website URL to crawl (must be a valid HTTP/HTTPS URL)"
    )
    crawler_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Options for configuring the crawler behavior"
    )
    page_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Options for configuring page processing"
    )

    @validator("crawler_options")
    def validate_crawler_options(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and set default crawler options.

        Args:
            v (Optional[Dict[str, Any]]): Crawler options to validate

        Returns:
            Dict[str, Any]: Validated crawler options with defaults
        """
        default_options = {
            "maxDepth": 2,
            "maxPages": 10,
            "allowedDomains": [],
            "excludePatterns": [],
            "followLinks": True,
            "respectRobotsTxt": True,
            "userAgent": "FirecrawlBot/1.0",
        }

        if v is None:
            return default_options

        # Validate and merge with defaults
        validated = default_options.copy()
        for key, value in v.items():
            if key not in default_options:
                raise ValueError(f"Invalid crawler option: {key}")
            if key in ["maxDepth", "maxPages"] and not isinstance(value, int):
                raise ValueError(f"{key} must be an integer")
            if key in ["allowedDomains", "excludePatterns"] and not isinstance(
                value, list
            ):
                raise ValueError(f"{key} must be a list")
            if key in ["followLinks", "respectRobotsTxt"] and not isinstance(
                value, bool
            ):
                raise ValueError(f"{key} must be a boolean")
            validated[key] = value

        return validated

    @validator("page_options")
    def validate_page_options(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate and set default page options.

        Args:
            v (Optional[Dict[str, Any]]): Page options to validate

        Returns:
            Dict[str, Any]: Validated page options with defaults
        """
        default_options = {
            "waitForSelector": None,
            "timeout": 30000,
            "extractImages": False,
            "extractLinks": True,
            "extractMetadata": True,
            "javascript": True,
        }

        if v is None:
            return default_options

        # Validate and merge with defaults
        validated = default_options.copy()
        for key, value in v.items():
            if key not in default_options:
                raise ValueError(f"Invalid page option: {key}")
            if key == "timeout" and not isinstance(value, int):
                raise ValueError("timeout must be an integer")
            if key in [
                "extractImages",
                "extractLinks",
                "extractMetadata",
                "javascript",
            ] and not isinstance(value, bool):
                raise ValueError(f"{key} must be a boolean")
            if (
                key == "waitForSelector"
                and value is not None
                and not isinstance(value, str)
            ):
                raise ValueError("waitForSelector must be a string or None")
            validated[key] = value

        return validated

    @validator("url")
    def validate_url(cls, url: str) -> str:
        """Validate the URL format and scheme.

        Args:
            url (str): The URL to validate

        Returns:
            str: The validated URL

        Raises:
            ValueError: If the URL is invalid or uses an unsupported scheme
        """
        # Check if URL is empty or None
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        # Parse the URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {str(e)}")

        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            raise ValueError(
                "Invalid URL scheme. Only HTTP and HTTPS URLs are supported. "
                f"Got: {parsed.scheme or 'no scheme'}"
            )

        # Check if netloc (domain) exists
        if not parsed.netloc:
            raise ValueError("Invalid URL: missing domain name")

        # Basic format validation using regex
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ip address
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(url):
            raise ValueError(
                "Invalid URL format. URL must be a valid HTTP/HTTPS URL. "
                "Example: https://example.com"
            )

        return url


class FirecrawlCrawlWebsiteTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = Field(
        default="Firecrawl web crawl tool", description="Name of the tool"
    )
    description: str = Field(
        default="Crawl webpages using Firecrawl and return the contents",
        description="Description of the tool's functionality",
    )
    args_schema: Type[BaseModel] = Field(
        default=FirecrawlCrawlWebsiteToolSchema, description="Schema for tool arguments"
    )
    firecrawl_app: Optional["FirecrawlApp"] = Field(
        default=None, description="Instance of FirecrawlApp for web crawling"
    )
    api_key: Optional[str] = Field(
        default=None, description="API key for Firecrawl authentication"
    )
    url: Optional[str] = Field(
        default=None, description="Base URL to crawl, can be overridden in _run method"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional parameters for the FirecrawlApp"
    )
    poll_interval: Optional[int] = Field(
        default=2, description="Interval in seconds between polling attempts"
    )
    idempotency_key: Optional[str] = Field(
        default=None, description="Key for ensuring idempotent operations"
    )
    cache_ttl: int = Field(
        default=300,  # 5 minutes
        description="Time-to-live for cached results in seconds",
    )
    max_cache_size: int = Field(
        default=1000,
        description="Maximum number of entries in the cache",
    )

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Initialize FirecrawlCrawlWebsiteTool.

        This tool provides web crawling functionality using the Firecrawl service. It can be initialized
        with various configuration options to customize the crawling behavior.

        Args:
            api_key (Optional[str]): Firecrawl API key. If not provided, will check FIRECRAWL_API_KEY env var.
            url (Optional[str]): Base URL to crawl. Can be overridden by the _run method.
            firecrawl_app (Optional[FirecrawlApp]): Previously created FirecrawlApp instance.
            params (Optional[Dict[str, Any]]): Additional parameters to pass to the FirecrawlApp.
            poll_interval (Optional[int]): Poll interval in seconds for the FirecrawlApp. Defaults to 2.
            idempotency_key (Optional[str]): Idempotency key for ensuring unique crawl operations.
            **kwargs: Additional arguments passed to BaseTool.

        Examples:
            Basic usage with environment variable:
                >>> tool = FirecrawlCrawlWebsiteTool()  # Uses FIRECRAWL_API_KEY env var
                >>> result = tool.run("https://example.com")

            Using explicit API key:
                >>> tool = FirecrawlCrawlWebsiteTool(api_key="your-api-key")
                >>> result = tool.run("https://example.com")

            With pre-configured URL:
                >>> tool = FirecrawlCrawlWebsiteTool(
                ...     api_key="your-api-key",
                ...     url="https://example.com",
                ...     poll_interval=5
                ... )
                >>> result = tool.run()  # Uses pre-configured URL

            With custom FirecrawlApp instance:
                >>> app = FirecrawlApp(api_key="your-api-key")
                >>> tool = FirecrawlCrawlWebsiteTool(firecrawl_app=app)
                >>> result = tool.run("https://example.com")

        Raises:
            ValueError: If neither api_key argument nor FIRECRAWL_API_KEY env var is provided.
            ImportError: If firecrawl package is not installed.
        """
        super().__init__(**kwargs)
        try:
            from firecrawl import FirecrawlApp  # type: ignore
        except ImportError:
            raise ImportError(
                "`firecrawl` package not found, please run `pip install firecrawl-py`"
            )

        # Allows passing a previously created FirecrawlApp instance
        # or builds a new one with the provided API key
        if not self.firecrawl_app:
            client_api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
            if not client_api_key:
                raise ValueError(
                    "FIRECRAWL_API_KEY is not set. To resolve this:\n\n"
                    "1. Option 1 - Use constructor:\n"
                    "   tool = FirecrawlCrawlWebsiteTool(api_key='your-api-key')\n\n"
                    "2. Option 2 - Set environment variable:\n"
                    "   export FIRECRAWL_API_KEY='your-api-key'\n\n"
                    "You can obtain an API key by:\n"
                    "1. Visit https://firecrawl.com\n"
                    "2. Create an account or log in\n"
                    "3. Navigate to API Settings\n"
                    "4. Generate a new API key\n\n"
                    "For more information, see the Firecrawl documentation."
                )
            self.firecrawl_app = FirecrawlApp(api_key=client_api_key)

    @lru_cache(maxsize=1000)
    def _validate_url(self, url: str) -> str:
        """Validate and sanitize a URL.

        Performs comprehensive validation and sanitization of URLs:
        1. Validates URL format and scheme using schema validator
        2. Sanitizes URL by removing potentially dangerous characters
        3. Checks for common security issues
        4. Enforces rate limiting per domain

        Args:
            url (str): URL to validate and sanitize

        Returns:
            str: The validated and sanitized URL

        Raises:
            ValueError: If the URL is invalid, potentially malicious, or rate limit exceeded
        """
        # First pass: basic validation using schema
        schema = FirecrawlCrawlWebsiteToolSchema(url=url)
        validated_url = schema.url

        # Second pass: additional security checks
        parsed = urlparse(validated_url)
        
        # Check for potentially dangerous characters in URL
        dangerous_chars = ["<", ">", "'", '"', ";", "`", "{", "}", "|", "\\"]
        if any(char in validated_url for char in dangerous_chars):
            raise ValueError(
                "URL contains potentially dangerous characters. "
                "Please ensure the URL is properly encoded."
            )

        # Check for common attack patterns
        attack_patterns = [
            "javascript:", "data:", "vbscript:", "file:",  # Protocol attacks
            "/etc/", "/proc/", "/var/",  # Path traversal
            "../../", "..\\",  # Directory traversal
        ]
        if any(pattern in validated_url.lower() for pattern in attack_patterns):
            raise ValueError(
                "URL contains potentially malicious patterns. "
                "Please verify the URL is safe and properly formatted."
            )

        # Rate limiting check
        self._check_rate_limit(parsed.netloc)

        return validated_url

    def _check_rate_limit(self, domain: str) -> None:
        """Check if the request is within rate limits.

        Implements a rolling window rate limiter that tracks requests per domain
        over the last minute. Default limit is 60 requests per minute per domain.

        Args:
            domain (str): The domain being accessed

        Raises:
            ValueError: If rate limit is exceeded
        """
        # Initialize rate limiting state if not exists
        if not hasattr(self, "_rate_limit_state"):
            self._rate_limit_state: Dict[str, List[float]] = {}

        current_time = time.time()
        
        # Clean up old entries
        self._rate_limit_state = {
            d: ts for d, ts in self._rate_limit_state.items()
            if current_time - ts[-1] < 60  # Keep last minute's worth
        }

        # Get or initialize domain's request timestamps
        domain_requests = self._rate_limit_state.get(domain, [])
        
        # Remove timestamps older than 1 minute
        domain_requests = [
            ts for ts in domain_requests
            if current_time - ts < 60
        ]

        # Check rate limit (default: 60 requests per minute per domain)
        if len(domain_requests) >= 60:
            raise ValueError(
                f"Rate limit exceeded for domain {domain}. "
                "Please wait before making more requests."
            )

        # Add current timestamp and update state
        domain_requests.append(current_time)
        self._rate_limit_state[domain] = domain_requests

    def _get_cache_key(
        self,
        url: str,
        crawler_options: Optional[Dict[str, Any]] = None,
        page_options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a unique cache key for the request.

        Args:
            url (str): The URL to crawl
            crawler_options (Optional[Dict[str, Any]]): Crawler configuration options
            page_options (Optional[Dict[str, Any]]): Page processing options

        Returns:
            str: A unique cache key combining URL and options
        """
        # Convert options to sorted tuples for consistent hashing
        crawler_items = sorted(
            (crawler_options or {}).items(),
            key=lambda x: str(x[0]) + str(x[1])
        )
        page_items = sorted(
            (page_options or {}).items(),
            key=lambda x: str(x[0]) + str(x[1])
        )
        
        # Combine all components into a hashable tuple
        components = (url, tuple(crawler_items), tuple(page_items))
        return str(hash(components))

    def _run(
        self,
        url: str,
        crawler_options: Optional[Dict[str, Any]] = None,
        page_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the web crawling operation.

        Args:
            url (str): The URL to crawl. If None, uses the URL set in constructor.
            crawler_options (Optional[Dict[str, Any]]): Options for configuring crawler behavior.
                Supported options:
                - maxDepth (int): Maximum depth for crawling (default: 2)
                - maxPages (int): Maximum number of pages to crawl (default: 10)
                - allowedDomains (List[str]): List of allowed domains (default: [])
                - excludePatterns (List[str]): URL patterns to exclude (default: [])
                - followLinks (bool): Whether to follow links (default: True)
                - respectRobotsTxt (bool): Whether to respect robots.txt (default: True)
                - userAgent (str): User agent string (default: "FirecrawlBot/1.0")
            page_options (Optional[Dict[str, Any]]): Options for configuring page processing.
                Supported options:
                - waitForSelector (Optional[str]): CSS selector to wait for (default: None)
                - timeout (int): Page timeout in milliseconds (default: 30000)
                - extractImages (bool): Whether to extract images (default: False)
                - extractLinks (bool): Whether to extract links (default: True)
                - extractMetadata (bool): Whether to extract metadata (default: True)
                - javascript (bool): Whether to execute JavaScript (default: True)

        Returns:
            Dict[str, Any]: The crawling results

        Raises:
            ValueError: If the URL is invalid or if options are invalid
        """
        # Unless url has been previously set via constructor by the user,
        # use the url argument provided by the agent at runtime.
        base_url = self.url or url

        # Validate inputs using schema
        schema = FirecrawlCrawlWebsiteToolSchema(
            url=base_url, crawler_options=crawler_options, page_options=page_options
        )

        # Merge options with any pre-configured params
        merged_params = {
            "crawlerOptions": schema.crawler_options,
            "pageOptions": schema.page_options,
        }
        if self.params:
            merged_params.update(self.params)

        # Generate cache key
        cache_key = self._get_cache_key(schema.url, crawler_options, page_options)
        
        # Initialize result cache if not exists
        if not hasattr(self, "_result_cache"):
            self._result_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
            
        # Check cache
        if cache_key in self._result_cache:
            timestamp, result = self._result_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return result
            
        # Clean up old cache entries
        current_time = time.time()
        self._result_cache = {
            k: v for k, v in self._result_cache.items()
            if current_time - v[0] < self.cache_ttl
        }
        
        # Enforce cache size limit
        if len(self._result_cache) >= self.max_cache_size:
            # Remove oldest entries
            sorted_cache = sorted(
                self._result_cache.items(),
                key=lambda x: x[1][0]
            )
            self._result_cache = dict(sorted_cache[-self.max_cache_size:])
        
        # Perform the crawl
        result = self.firecrawl_app.crawl_url(
            schema.url,
            params=merged_params,
            poll_interval=self.poll_interval,
            idempotency_key=self.idempotency_key,
        )
        
        # Cache the result
        self._result_cache[cache_key] = (time.time(), result)
        
        return result


try:
    from firecrawl import FirecrawlApp

    # Must rebuild model after class is defined
    FirecrawlCrawlWebsiteTool.model_rebuild()
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """
