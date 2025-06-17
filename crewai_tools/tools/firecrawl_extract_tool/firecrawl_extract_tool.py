from typing import Any, Dict, List, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

try:
    from firecrawl import FirecrawlApp
except ImportError:
    FirecrawlApp = Any


class FirecrawlExtractToolSchema(BaseModel):
    urls: List[str] = Field(
        description="List of URLs to extract data from. URLs can include glob patterns"
    )


class FirecrawlExtractTool(BaseTool):
    """
    Tool for extracting structured data from webpages using Firecrawl and LLMs.

    Args:
        api_key (str): Your Firecrawl API key.
        config (dict): Configuration options for extraction. This should include any
            parameters supported by Firecrawl's extract method, such as:
                - prompt (str): The prompt describing what information to extract from the pages
                - schema (dict): JSON schema defining the structure of the data to extract
                - enableWebSearch (bool): Use web search to find additional data
                - ignoreSiteMap (bool): Ignore sitemap.xml
                - includeSubdomains (bool): Scan subdomains
                - showSources (bool): Include sources in the response
                - scrapeOptions (dict): Additional crawl options

    Note:
        The preferred and only supported way to set extraction options is via the config dictionary.
        Passing individual parameters is deprecated and not supported.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Firecrawl extract tool"
    description: str = "Extract structured data from webpages using Firecrawl and LLMs"
    args_schema: Type[BaseModel] = FirecrawlExtractToolSchema
    api_key: Optional[str] = None
    config: Optional[dict[str, Any]] = Field(
        default_factory=lambda: {
            "prompt": None,
            "schema": None,
            "enableWebSearch": False,
            "ignoreSiteMap": False,
            "includeSubdomains": True,
            "showSources": False,
            "scrapeOptions": {},
            "integration": "crewai",
        }
    )
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)

    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize FirecrawlExtractTool.

        Args:
            api_key (str): Your Firecrawl API key.
            config (dict): Configuration options for extraction. See class docstring for details.
        """
        super().__init__(**kwargs)
        self.api_key = api_key
        if config is not None:
            self.config = config
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

    def _run(self, urls: List[str]) -> Any:
        self.config["integration"] = "crewai"  # Ensure integration is always set
        options = {
            "urls": urls,
            **self.config,
        }
        return self._firecrawl.extract(**options)


try:
    from firecrawl import FirecrawlApp

    # Must rebuild model after class is defined
    if not hasattr(FirecrawlExtractTool, "_model_rebuilt"):
        FirecrawlExtractTool.model_rebuild()
        FirecrawlExtractTool._model_rebuilt = True
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """