from typing import Any, Optional, Type, List, Dict

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = Any


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
        default=False,
        description="Skip TLS certificate verification when making requests",
    )
    timeout: Optional[int] = Field(
        default=30000,
        description="Timeout in milliseconds for the scraping operation",
    )
    json_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Options for JSON extraction from the page",
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
    actions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Actions to perform on the page before grabbing the content",
    )
    proxy: Optional[str] = Field(
        default=None,
        description="Specifies the type of proxy to use",
    )


class FirecrawlScrapeWebsiteTool(BaseTool):
    """
    Tool for scraping webpages using Firecrawl. To run this tool, you need to have a Firecrawl API key.

    Args:
        api_key (str): Your Firecrawl API key.
        config (dict): Optional. It contains Firecrawl API parameters.

    Default configuration options:
        formats (list[str]): Content formats to return. Default: ["markdown"]
        only_main_content (bool): Only return main content. Default: True
        include_tags (list[str]): Tags to include. Default: []
        exclude_tags (list[str]): Tags to exclude. Default: []
        headers (dict): Headers to include. Default: {}
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
            "only_main_content": True,
            "include_tags": [],
            "exclude_tags": [],
            "headers": {},
            "wait_for": 0,
            "mobile": False,
            "skip_tls_verification": False,
            "timeout": 30000,
            "json_options": None,
            "location": None,
            "remove_base64_images": False,
            "block_ads": True,
            "actions": None,
            "proxy": None,
            "integration": "crewai",
        }
    )
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)

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
        json_options: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, Any]] = None,
        remove_base64_images: Optional[bool] = None,
        block_ads: Optional[bool] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        proxy: Optional[str] = None,
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
        if json_options is not None:
            self.config["json_options"] = json_options
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