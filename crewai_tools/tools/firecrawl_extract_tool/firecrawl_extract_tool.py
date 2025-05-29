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
    prompt: Optional[str] = Field(
        default=None,
        description="The prompt describing what information to extract from the pages"
    )
    schema: Optional[Dict[str, Any]] = Field(
        default=None,
        description="JSON schema defining the structure of the data to extract",
    )
    enable_web_search: Optional[bool] = Field(
        default=False,
        description="When true, the extraction will use web search to find additional data",
    )
    ignore_site_map: Optional[bool] = Field(
        default=False,
        description="When true, the extraction will not use the sitemap.xml to find additional data",
    )
    include_subdomains: Optional[bool] = Field(
        default=True,
        description="When true, subdomains of the provided URLs will also be scanned",
    )
    show_sources: Optional[bool] = Field(
        default=False,
        description="When true, the sources used to extract the data will be included in the response as sources key",
    )
    scrape_options: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional options for the crawl request",
    )


class FirecrawlExtractTool(BaseTool):
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
        }
    )
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)

    def __init__(
        self,
        api_key: Optional[str] = None,
        prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        enable_web_search: Optional[bool] = False,
        ignore_site_map: Optional[bool] = False,
        include_subdomains: Optional[bool] = True,
        show_sources: Optional[bool] = False,
        scrape_options: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.config.update({
            "prompt": prompt,
            "schema": schema,
            "enableWebSearch": enable_web_search,
            "ignoreSiteMap": ignore_site_map,
            "includeSubdomains": include_subdomains,
            "showSources": show_sources,
            "scrapeOptions": scrape_options or {},
        })
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
        if not self._firecrawl:
            raise RuntimeError("FirecrawlApp not properly initialized")

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