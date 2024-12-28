import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from pydantic import BaseModel, ConfigDict, Field

from crewai.tools import BaseTool

# Type checking import
if TYPE_CHECKING:
    from firecrawl import FirecrawlApp


class FirecrawlCrawlWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL")

class FirecrawlCrawlWebsiteTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = Field(default="Firecrawl web crawl tool", description="Name of the tool")
    description: str = Field(
        default="Crawl webpages using Firecrawl and return the contents",
        description="Description of the tool's functionality"
    )
    args_schema: Type[BaseModel] = Field(
        default=FirecrawlCrawlWebsiteToolSchema,
        description="Schema for tool arguments"
    )
    firecrawl_app: Optional["FirecrawlApp"] = Field(
        default=None,
        description="Instance of FirecrawlApp for web crawling"
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Firecrawl authentication"
    )
    url: Optional[str] = Field(
        default=None,
        description="Base URL to crawl, can be overridden in _run method"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional parameters for the FirecrawlApp"
    )
    poll_interval: Optional[int] = Field(
        default=2,
        description="Interval in seconds between polling attempts"
    )
    idempotency_key: Optional[str] = Field(
        default=None,
        description="Key for ensuring idempotent operations"
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

    def _run(self, url: str):
        # Unless url has been previously set via constructor by the user,
        # use the url argument provided by the agent at runtime.
        base_url = self.url or url

        return self.firecrawl_app.crawl_url(
            base_url, 
            params=self.params, 
            poll_interval=self.poll_interval, 
            idempotency_key=self.idempotency_key
        )


try:
    from firecrawl import FirecrawlApp

    # Must rebuild model after class is defined
    FirecrawlCrawlWebsiteTool.model_rebuild()
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """
    pass
