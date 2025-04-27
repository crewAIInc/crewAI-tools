import os
import re
import warnings
from typing import Any, Optional, Type

import requests
import tiktoken
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FixedScrapeWebsiteToolSchema(BaseModel):
    """Input for ScrapeWebsiteTool."""


class ScrapeWebsiteToolSchema(FixedScrapeWebsiteToolSchema):
    """Input for ScrapeWebsiteTool."""

    website_url: str = Field(..., description="Mandatory website url to read the file")


class ScrapeWebsiteTool(BaseTool):
    name: str = "Read website content"
    description: str = "A tool that can be used to read a website content."
    args_schema: Type[BaseModel] = ScrapeWebsiteToolSchema
    website_url: Optional[str] = None
    cookies: Optional[dict] = None
    headers: Optional[dict] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    max_tokens: Optional[int] = Field(
        default=8000,
        description="Maximum number of tokens for the scraped content. Default is 8000 which is 75% of the smallest common model's context window.",
    )

    def __init__(
        self,
        website_url: Optional[str] = None,
        cookies: Optional[dict] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if website_url is not None:
            self.website_url = website_url
            self.description = (
                f"A tool that can be used to read {website_url}'s content."
            )
            self.args_schema = FixedScrapeWebsiteToolSchema
            self._generate_description()
            if cookies is not None:
                self.cookies = {cookies["name"]: os.getenv(cookies["value"])}
        if max_tokens is not None:
            self.max_tokens = max_tokens

    def _count_tokens(self, text: str) -> int:
        """Count the number of tokens in the text."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except Exception:
            return len(text) // 4

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        website_url = kwargs.get("website_url", self.website_url)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        try:
            page = requests.get(
                website_url,
                timeout=15,
                headers=self.headers,
                cookies=self.cookies if self.cookies else {},
            )
            
            page.encoding = page.apparent_encoding
            parsed = BeautifulSoup(page.text, "html.parser")
            
            text = parsed.get_text(" ")
            text = re.sub("[ \t]+", " ", text)
            text = re.sub("\\s+\n\\s+", "\n", text)
            
            token_count = self._count_tokens(text)
            
            if max_tokens and token_count > max_tokens:
                truncate_ratio = max_tokens / token_count
                approx_char_limit = int(len(text) * truncate_ratio)
                
                truncated_text = text[:approx_char_limit]
                
                message = f"\n\n[Content truncated to {max_tokens} tokens from original {token_count} tokens due to LLM token limits]"
                return truncated_text + message
            
            return text
        except Exception as e:
            return f"Error scraping website: {str(e)}"
