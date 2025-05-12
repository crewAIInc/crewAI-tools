from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Literal, List

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from firecrawl import FirecrawlApp


try:
    from firecrawl import FirecrawlApp

    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False


class FirecrawlSearchToolSchema(BaseModel):
    query: str = Field(description="Search query")
    limit: Optional[int] = Field(
        default=5, description="Maximum number of results to return"
    )
    tbs: Optional[str] = Field(default=None, description="Time-based search parameter")
    lang: Optional[str] = Field(
        default="en", description="Language code for search results"
    )
    country: Optional[str] = Field(
        default="us", description="Country code for search results"
    )
    location: Optional[str] = Field(
        default=None, description="Location parameter for search results"
    )
    timeout: Optional[int] = Field(default=60000, description="Timeout in milliseconds")
    scrapeOptions: Optional[
        Dict[
            Literal["formats"],
            List[
                Literal[
                    "markdown",
                    "html",
                    "rawHtml",
                    "links",
                    "screenshot",
                    "screenshot@fullPage",
                    "extract",
                ]
            ],
        ]
    ] = Field(default=None, description="Options for scraping search results")


class FirecrawlSearchTool(BaseTool):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "Firecrawl web search tool"
    description: str = "Search webpages using Firecrawl and return the results"
    args_schema: Type[BaseModel] = FirecrawlSearchToolSchema
    api_key: Optional[str] = None
    query: Optional[str] = None
    limit: Optional[int] = None
    tbs: Optional[str] = None
    lang: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    timeout: Optional[int] = None
    scrapeOptions: Optional[
        Dict[
            Literal["formats"],
            List[
                Literal[
                    "markdown",
                    "html",
                    "rawHtml",
                    "links",
                    "screenshot",
                    "screenshot@fullPage",
                    "extract",
                ]
            ],
        ]
    ] = None
    _firecrawl: Optional["FirecrawlApp"] = PrivateAttr(None)

    def __init__(
        self,
        api_key: Optional[str] = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        tbs: Optional[str] = None,
        lang: Optional[str] = None,
        country: Optional[str] = None,
        location: Optional[str] = None,
        timeout: Optional[int] = None,
        scrapeOptions: Optional[
            Dict[
                Literal["formats"],
                List[
                    Literal[
                        "markdown",
                        "html",
                        "rawHtml",
                        "links",
                        "screenshot",
                        "screenshot@fullPage",
                        "extract",
                    ]
                ],
            ]
        ] = None,
    ):
        super().__init__()
        self.api_key = api_key
        self.query = query
        self.limit = limit
        self.tbs = tbs
        self.lang = lang
        self.country = country
        self.location = location
        self.timeout = timeout
        self.scrapeOptions = scrapeOptions
        self._initialize_firecrawl()

    def _initialize_firecrawl(self) -> None:
        try:
            if FIRECRAWL_AVAILABLE:
                from firecrawl import FirecrawlApp
                self._firecrawl = FirecrawlApp(api_key=self.api_key)
            else:
                raise ImportError
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

    def _run(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        tbs: Optional[str] = None,
        lang: Optional[str] = None,
        country: Optional[str] = None,
        location: Optional[str] = None,
        timeout: Optional[int] = None,
        scrapeOptions: Optional[
            Dict[
                Literal["formats"],
                List[
                    Literal[
                        "markdown",
                        "html",
                        "rawHtml",
                        "links",
                        "screenshot",
                        "screenshot@fullPage",
                        "extract",
                    ]
                ],
            ]
        ] = None,
    ) -> Any:
        if not self._firecrawl:
            raise RuntimeError("FirecrawlApp not properly initialized")
        
        query = query or self.query
        if not query:
            raise ValueError("Query must be provided either during initialization or execution")
        
        params = {}
        limit = limit or self.limit
        if limit:
            params["limit"] = limit
        tbs = tbs or self.tbs
        if tbs:
            params["tbs"] = tbs
        lang = lang or self.lang
        if lang:
            params["lang"] = lang
        country = country or self.country
        if country:
            params["country"] = country
        location = location or self.location
        if location:
            params["location"] = location
        timeout = timeout or self.timeout
        if timeout:
            params["timeout"] = timeout
        scrapeOptions = scrapeOptions or self.scrapeOptions
        if scrapeOptions:
            params["scrapeOptions"] = scrapeOptions
        return self._firecrawl.search(query=query, params=params)


try:
    from firecrawl import FirecrawlApp  # type: ignore

    # Only rebuild if the class hasn't been initialized yet
    if not hasattr(FirecrawlSearchTool, "_model_rebuilt"):
        FirecrawlSearchTool.model_rebuild()
        FirecrawlSearchTool._model_rebuilt = True
except ImportError:
    """
    When this tool is not used, then exception can be ignored.
    """
    pass
