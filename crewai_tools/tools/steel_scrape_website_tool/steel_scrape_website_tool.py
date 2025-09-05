import os
from typing import TYPE_CHECKING, List, Optional, Type

from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

if TYPE_CHECKING:
    from steel import Steel

try:
    from steel import Steel

    STEEL_AVAILABLE = True
except ImportError:
    STEEL_AVAILABLE = False

class SteelScrapeWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL")


class SteelScrapeWebsiteTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=True, frozen=False)
    name: str = "Steel web scrape tool"
    description: str = "Scrape webpages using Steel and return the contents"
    args_schema: Type[BaseModel] = SteelScrapeWebsiteToolSchema
    api_key: Optional[str] = None
    formats: Optional[List[str]] = None
    proxy: Optional[bool] = None
    
    _steel: Optional["Steel"] = PrivateAttr(None)
    package_dependencies: List[str] = ["steel-sdk"]
    env_vars: List[EnvVar] = [
        EnvVar(name="STEEL_API_KEY", description="API key for Steel services", required=True),
    ]
    
    def __init__(
            self,
            api_key: Optional[str] = None,
            formats: Optional[List[str]] = None,
            proxy: Optional[bool] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("STEEL_API_KEY")
        if not self.api_key:
            raise EnvironmentError("STEEL_API_KEY environment variable or api_key is required")

        try:
            from steel import Steel  # type: ignore
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'steel-sdk' package. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(["uv", "add", "steel-sdk"], check=True)
                from steel import Steel  # type: ignore
            else:
                raise ImportError(
                    "`steel-sdk` package not found, please run `uv add steel-sdk`"
                )
        
        self._steel = Steel(steel_api_key=self.api_key)
        self.formats = formats or ["markdown"]
        self.proxy = proxy


    def _run(self, url: str):
        if not self._steel:
            raise RuntimeError("Steel not properly initialized")
        
        return self._steel.scrape(url=url, use_proxy=self.proxy, format=self.formats)

try:
    from steel import Steel

    if not hasattr(SteelScrapeWebsiteTool, "_model_rebuilt"):
        SteelScrapeWebsiteTool.model_rebuild()
        SteelScrapeWebsiteTool._model_rebuilt = True
except ImportError:
    pass
