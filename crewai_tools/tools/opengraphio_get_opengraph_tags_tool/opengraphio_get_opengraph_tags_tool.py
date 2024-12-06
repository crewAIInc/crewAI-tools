import logging
import os
from typing import Optional, Type

from pydantic import BaseModel, Field

from crewai_tools.tools.base_tool import BaseTool

logger = logging.getLogger(__file__)


class GetOpengraphTagsToolSchema(BaseModel):
    url: str = Field(description="Webpage URL")
    cache_ok: Optional[bool] = Field(
        default=None, description="Whether to allow cached responses"
    )
    full_render: Optional[bool] = Field(
        default=None,
        description="Whether to fully render the page before extracting metadata",
    )
    use_proxy: Optional[bool] = Field(
        default=None, description="Whether to use a proxy for scraping"
    )
    use_premium: Optional[bool] = Field(
        default=None, description="Whether to use the Premium Proxy feature"
    )
    use_superior: Optional[bool] = Field(
        default=None, description="Whether to use the Superior Proxy feature"
    )
    auto_proxy: Optional[bool] = Field(
        default=None,
        description="Whether to automatically use a proxy for domains that require one",
    )
    max_cache_age: Optional[int] = Field(
        default=None, description="The maximum cache age in milliseconds"
    )
    accept_lang: Optional[str] = Field(
        default=None, description="The request language sent when requesting the URL"
    )
    ignore_scrape_failures: Optional[bool] = Field(
        default=None, description="Whether to ignore failures"
    )


class GetOpengraphTagsTool(BaseTool):
    name: str = "OpenGraph.io tags extraction tool"
    description: str = "Extract OpenGraph tags from a webpage URL using OpenGraph.io"
    args_schema: Type[BaseModel] = GetOpengraphTagsToolSchema
    api_key: str = None

    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("OPENGRAPHIO_API_KEY")

    def _run(
        self,
        url: str,
        cache_ok: Optional[bool] = None,
        full_render: Optional[bool] = None,
        use_proxy: Optional[bool] = None,
        use_premium: Optional[bool] = None,
        use_superior: Optional[bool] = None,
        auto_proxy: Optional[bool] = None,
        max_cache_age: Optional[int] = None,
        accept_lang: Optional[str] = None,
        ignore_scrape_failures: Optional[bool] = None,
    ):
        import urllib.parse

        import requests

        encoded_url = urllib.parse.quote_plus(url)
        api_endpoint = f"https://opengraph.io/api/1.1/site/{encoded_url}"
        params = {"app_id": self.api_key}

        if cache_ok is not None:
            params["cache_ok"] = cache_ok
        if full_render is not None:
            params["full_render"] = full_render
        if use_proxy is not None:
            params["use_proxy"] = use_proxy
        if use_premium is not None:
            params["use_premium"] = use_premium
        if use_superior is not None:
            params["use_superior"] = use_superior
        if auto_proxy is not None:
            params["auto_proxy"] = auto_proxy
        if max_cache_age is not None:
            params["max_cache_age"] = max_cache_age
        if accept_lang is not None:
            params["accept_lang"] = accept_lang

        try:
            response = requests.get(api_endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            if ignore_scrape_failures:
                logger.error(
                    f"Error fetching OpenGraph tags from {url}, exception: {e}"
                )
                return None
            else:
                raise e
