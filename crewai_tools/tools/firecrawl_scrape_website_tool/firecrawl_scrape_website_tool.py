from typing import Any, Optional, Type, Dict, List, TYPE_CHECKING
from typing import Any, Optional, Type, List, Dict

from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from firecrawl import FirecrawlApp

try:
    from firecrawl import FirecrawlApp

    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False



class FirecrawlScrapeWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL")
    formats: Optional[List[str]] = Field(
        default=["markdown"],
        description="Formats to include in the output (markdown, html, rawHtml, links, screenshot)",
    )
    only_main_content: Optional[bool] = Field(
        default=True,
        description="Only return the main content of the page excluding headers, navs, footers, etc.",
    )
    include_tags: Optional[List[str]] = Field(
        default=None,
        description="Tags to include in the output",
    )
    exclude_tags: Optional[List[str]] = Field(
        default=None,
        description="Tags to exclude from the output",
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Headers to send with the request",
    )
    wait_for: Optional[int] = Field(
        default=0,
        description="Specify a delay in milliseconds before fetching the content",
    )
    mobile: Optional[bool] = Field(
        default=False,
        description="Set to true if you want to emulate scraping from a mobile device",
    )
    skip_tls_verification: Optional[bool] = Field(
        default=True,
        description="Skip TLS certificate verification when making requests",
    )
    timeout: Optional[int] = Field(
        default=30000,
        description="Timeout in milliseconds for the scraping operation",
    )
    parsers: Optional[List[str]] = Field(
        default=["pdf"],
        description="Parsers to use for the scraping operation",
    )
    actions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Actions to perform on the page before grabbing the content",
    )
    location: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Location settings for the request",
    )
    remove_base64_images: Optional[bool] = Field(
        default=False,
        description="Removes all base 64 images from the output",
    )
    block_ads: Optional[bool] = Field(
        default=True,
        description="Enables ad-blocking and cookie popup blocking",
    )
    proxy: Optional[str] = Field(
        default=None,
        description="Specifies the type of proxy to use",
    )
    store_in_cache: Optional[bool] = Field(
        default=True,
        description="Store in the Firecrawl index and cache",
    )
    zero_data_retention: Optional[bool] = Field(
        default=False,
        description="Enable zero data retention for this scrape",
    )

class FirecrawlScrapeWebsiteTool(BaseTool):
    """
    Tool for scraping webpages using Firecrawl. To run this tool, you need to have a Firecrawl API key.

    Args:
        api_key (str): Your Firecrawl API key.
        config (dict): Optional. It contains Firecrawl API parameters.

    Default configuration options:
        formats (list[str]): Content formats to return. Default: ["markdown"]
        onlyMainContent (bool): Only return main content. Default: True
        includeTags (list[str]): Tags to include. Default: []
        excludeTags (list[str]): Tags to exclude. Default: []
        headers (dict): Headers to include. Default: {}
        waitFor (int): Time to wait for page to load in ms. Default: 0
        json_options (dict): Options for JSON extraction. Default: None
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Firecrawl web scrape tool"
    description: str = "Scrape webpages using Firecrawl and return the contents"
    args_schema: Type[BaseModel] = FirecrawlScrapeWebsiteToolSchema
    api_key: Optional[str] = None
    config: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "includeTags": [],
            "excludeTags": [],
            "headers": {},
            "waitFor": 0,
            "mobile": False,
            "skipTlsVerification": True,
            "timeout": 30000,
            "parsers": ["pdf"],
            "actions": None,
            "location": None,
            "removeBase64Images": True,
            "blockAds": True,
            "proxy": None,
            "storeInCache": True,
            "zeroDataRetention": False
            "integration": "crewai",
        }
    )
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)
    package_dependencies: List[str] = ["firecrawl-py"]
    env_vars: List[EnvVar] = [
        EnvVar(name="FIRECRAWL_API_KEY", description="API key for Firecrawl services", required=True),
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        formats: Optional[List[str]] = None,
        only_main_content: Optional[bool] = None,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        wait_for: Optional[int] = None,
        mobile: Optional[bool] = None,
        skip_tls_verification: Optional[bool] = None,
        timeout: Optional[int] = None,
        parsers: Optional[List[str]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        location: Optional[Dict[str, Any]] = None,
        remove_base64_images: Optional[bool] = None,
        block_ads: Optional[bool] = None,
        proxy: Optional[str] = None,
        store_in_cache: Optional[bool] = None,
        zero_data_retention: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key
        if formats is not None:
            self.config["formats"] = formats
        if only_main_content is not None:
            self.config["only_main_content"] = only_main_content
        if include_tags is not None:
            self.config["include_tags"] = include_tags
        if exclude_tags is not None:
            self.config["exclude_tags"] = exclude_tags
        if headers is not None:
            self.config["headers"] = headers
        if wait_for is not None:
            self.config["wait_for"] = wait_for
        if mobile is not None:
            self.config["mobile"] = mobile
        if skip_tls_verification is not None:
            self.config["skip_tls_verification"] = skip_tls_verification
        if timeout is not None:
            self.config["timeout"] = timeout
        if parsers is not None:
            self.config["parsers"] = parsers
        if location is not None:
            self.config["location"] = location
        if remove_base64_images is not None:
            self.config["remove_base64_images"] = remove_base64_images
        if block_ads is not None:
            self.config["block_ads"] = block_ads
        if actions is not None:
            self.config["actions"] = actions
        if proxy is not None:
            self.config["proxy"] = proxy
        if store_in_cache is not None:
            self.config["store_in_cache"] = store_in_cache
        if zero_data_retention is not None:
            self.config["zero_data_retention"] = zero_data_retention
        self.config["integration"] = "crewai"
        self._initialize_firecrawl()

    def _initialize_firecrawl(self) -> None:
        try:
            from firecrawl import FirecrawlApp  # type: ignore

            self._firecrawl = FirecrawlApp(api_key=self.api_key)
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'firecrawl-py' package. Would you like to install it?"
            ):
                import subprocess

                try:
                    subprocess.run(["uv", "add", "firecrawl-py"], check=True)
                    from firecrawl import FirecrawlApp

                    self._firecrawl = FirecrawlApp(api_key=self.api_key)
                except subprocess.CalledProcessError:
                    raise ImportError("Failed to install firecrawl-py package")
            else:
                raise ImportError(
                    "`firecrawl-py` package not found, please run `uv add firecrawl-py`"
                )

    def _run(self, url: str) -> Any:
        self.config["integration"] = "crewai"
        return self._firecrawl.scrape_url(url, **self.config)

try:
    from firecrawl import FirecrawlApp

    # Must rebuild model after class is defined
    if not hasattr(FirecrawlScrapeWebsiteTool, "_model_rebuilt"):
        FirecrawlScrapeWebsiteTool.model_rebuild()
        FirecrawlScrapeWebsiteTool._model_rebuilt = True
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """