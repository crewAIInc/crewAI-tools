import json
import os
from typing import Any, Literal

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# ================================
# LLMLayer Search Tool
# ================================


class LLMLayerSearchInput(BaseModel):
    """Input schema for LLMLayer Answer API."""

    query: str = Field(description="The search query or question to answer")
    model: str = Field(
        description="LLM model to use (e.g., openai/gpt-4o-mini, anthropic/claude-sonnet-4, groq/llama-3.3-70b-versatile)"
    )
    location: str = Field(
        default="us", description="Country code for localized search results"
    )
    provider_key: str | None = Field(
        default=None, description="Your own API key for the model provider (optional)"
    )
    system_prompt: str | None = Field(
        default=None, description="Custom system prompt to override default behavior"
    )
    response_language: str = Field(
        default="auto",
        description="Language for the response (auto detects from query)",
    )
    answer_type: Literal["markdown", "html", "json"] = Field(
        default="markdown", description="Format of the response"
    )
    search_type: Literal["general", "news"] = Field(
        default="general", description="Type of web search to perform"
    )
    json_schema: str | dict | None = Field(
        default=None,
        description="JSON schema as string or dict for structured responses (required when answer_type=json)",
    )
    citations: bool = Field(
        default=False, description="Include inline citations [1] in the response"
    )
    return_sources: bool = Field(
        default=False, description="Return source documents used for answer generation"
    )
    return_images: bool = Field(
        default=False, description="Return relevant images from search"
    )
    date_filter: Literal["anytime", "hour", "day", "week", "month", "year"] = Field(
        default="anytime", description="Filter search results by recency"
    )
    max_tokens: int = Field(
        default=1500, ge=1, description="Maximum tokens in the LLM response"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Controls randomness (0=deterministic, 2=very creative)",
    )
    domain_filter: list[str] | None = Field(
        default=None,
        description="Include/exclude domains (use '-' prefix to exclude, e.g., ['wikipedia.org', '-reddit.com'])",
    )
    max_queries: int = Field(
        default=1, ge=1, le=5, description="Number of search queries to generate"
    )
    search_context_size: Literal["low", "medium", "high"] = Field(
        default="medium", description="Amount of search context to extract"
    )


class LLMLayerSearchTool(BaseTool):
    name: str = "LLMLayer Answer API"
    description: str = (
        "Use this tool when you need web-enhanced AI answers with citations and sources. "
        "Combines real-time web search with AI to provide comprehensive answers to questions. "
        "Best for: research questions, current events, fact-checking, and detailed explanations. "
        "Choose this over LLMLayerWebSearchTool when you want AI-processed answers instead of raw search results."
    )
    args_schema: type[BaseModel] = LLMLayerSearchInput

    api_key: str = ""
    timeout: int = 90
    include_metadata: bool = False

    def __init__(
        self,
        api_key: str = "",
        timeout: int = 90,
        include_metadata: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("LLMLAYER_API_KEY", "")
        self.timeout = timeout
        self.include_metadata = include_metadata

    def _run(
        self,
        query: str,
        model: str,
        location: str = "us",
        provider_key: str | None = None,
        system_prompt: str | None = None,
        response_language: str = "auto",
        answer_type: str = "markdown",
        search_type: str = "general",
        json_schema: str | dict | None = None,
        citations: bool = False,
        return_sources: bool = False,
        return_images: bool = False,
        date_filter: str = "anytime",
        max_tokens: int = 1500,
        temperature: float = 0.7,
        domain_filter: list[str] | None = None,
        max_queries: int = 1,
        search_context_size: str = "medium",
    ) -> str:
        """Execute web search with AI-powered answer generation."""

        if not self.api_key:
            return "Error: LLMLAYER_API_KEY not set. Set it as environment variable or pass to tool initialization."

        payload: dict[str, Any] = {
            "query": query,
            "model": model,
            "location": location,
            "response_language": response_language,
            "answer_type": answer_type,
            "search_type": search_type,
            "citations": citations,
            "return_sources": return_sources,
            "return_images": return_images,
            "date_filter": date_filter,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "max_queries": max_queries,
            "search_context_size": search_context_size,
        }

        if provider_key:
            payload["provider_key"] = provider_key
        if system_prompt:
            payload["system_prompt"] = system_prompt
        if json_schema:
            payload["json_schema"] = (
                json.dumps(json_schema)
                if isinstance(json_schema, dict)
                else json_schema
            )
        if domain_filter:
            payload["domain_filter"] = domain_filter

        try:
            response = requests.post(
                "https://api.llmlayer.dev/api/v1/search",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    error_msg = detail.get("message", f"HTTP {response.status_code}")
                    error_code = detail.get("error_code", "unknown")
                    return f"Error: LLMLayer API error [{error_code}]: {error_msg}"
                except Exception:
                    return f"Error: HTTP {response.status_code} - {response.reason}"

            data = response.json()
            llm_response = data.get("llm_response", "")

            if answer_type == "json":
                result = (
                    json.dumps(llm_response, indent=2)
                    if isinstance(llm_response, dict)
                    else str(llm_response)
                )
            else:
                result = str(llm_response)

            sources = data.get("sources", [])
            if return_sources and sources:
                result += "\n\n### Sources\n"
                for i, source in enumerate(sources, 1):
                    title = source.get("title", "Source")
                    link = source.get("link", "")
                    snippet = source.get("snippet", "")
                    result += f"{i}. [{title}]({link})\n"
                    if snippet:
                        result += f"   {snippet}\n"

            images = data.get("images", [])
            if return_images and images:
                result += "\n\n### Images\n"
                for i, image in enumerate(images[:5], 1):
                    title = image.get("title", "Image")
                    image_url = image.get("imageUrl", "")
                    result += f"{i}. {title}: {image_url}\n"

            if self.include_metadata:
                response_time = data.get("response_time", "N/A")
                input_tokens = data.get("input_tokens", 0)
                output_tokens = data.get("output_tokens", 0)
                result += "\n\n---\n"
                result += f"Response time: {response_time}s | Tokens: {input_tokens} in / {output_tokens} out"

            return result

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds"
        except requests.exceptions.RequestException as e:
            return f"Error: {e!s}"


# ================================
# LLMLayer Web Search Tool
# ================================


class LLMLayerWebSearchInput(BaseModel):
    """Input schema for LLMLayer Web Search API."""

    query: str = Field(description="The search query")
    search_type: Literal[
        "general", "news", "shopping", "videos", "images", "scholar"
    ] = Field(default="general", description="Type of search to perform")
    location: str = Field(
        default="us", description="Country code for localized results"
    )
    recency: Literal["hour", "day", "week", "month", "year"] | None = Field(
        default=None, description="Filter by time period"
    )
    domain_filter: list[str] | None = Field(
        default=None, description="Include/exclude domains (prefix with '-' to exclude)"
    )


class LLMLayerWebSearchTool(BaseTool):
    name: str = "LLMLayer Web Search"
    description: str = (
        "Use this tool when you need raw web search results without AI processing. "
        "Returns unprocessed search results with titles, links, and snippets. "
        "Best for: finding specific URLs, getting multiple search results to analyze yourself, "
        "or when you need the raw data instead of an AI summary. "
        "Choose LLMLayerAnswerAPI if you want AI-processed answers with citations."
    )
    args_schema: type[BaseModel] = LLMLayerWebSearchInput

    api_key: str = ""
    timeout: int = 30
    include_metadata: bool = False

    def __init__(
        self,
        api_key: str = "",
        timeout: int = 30,
        include_metadata: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("LLMLAYER_API_KEY", "")
        self.timeout = timeout
        self.include_metadata = include_metadata

    def _run(
        self,
        query: str,
        search_type: str = "general",
        location: str = "us",
        recency: str | None = None,
        domain_filter: list[str] | None = None,
    ) -> str:
        """Execute web search without AI processing."""

        if not self.api_key:
            return "Error: LLMLAYER_API_KEY not set. Set it as environment variable or pass to tool initialization."

        payload: dict[str, Any] = {
            "query": query,
            "search_type": search_type,
            "location": location,
        }

        if recency:
            payload["recency"] = recency
        if domain_filter:
            payload["domain_filter"] = domain_filter

        try:
            response = requests.post(
                "https://api.llmlayer.dev/api/v1/web_search",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    error_msg = detail.get("message", f"HTTP {response.status_code}")
                    error_code = detail.get("error_code", "unknown")
                    return f"Error: LLMLayer API error [{error_code}]: {error_msg}"
                except Exception:
                    return f"Error: HTTP {response.status_code} - {response.reason}"

            data = response.json()
            results = data.get("results", [])

            if not results:
                return "No results found."

            output = (
                f"### {search_type.title()} Search Results ({len(results)} found)\n\n"
            )

            for i, result in enumerate(results[:20], 1):
                title = result.get("title", "No title")
                link = result.get("link", result.get("url", ""))
                snippet = result.get("snippet", result.get("description", ""))

                output += f"**{i}. {title}**\n"
                if link:
                    output += f"   URL: {link}\n"
                if snippet:
                    output += f"   {snippet}\n"
                output += "\n"

            if self.include_metadata:
                cost = data.get("cost")
                if cost is not None:
                    output += f"\n---\nCost: ${cost:.6f}"

            return output

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds"
        except requests.exceptions.RequestException as e:
            return f"Error: {e!s}"


# ================================
# LLMLayer Scraper Tool
# ================================


class LLMLayerScraperInput(BaseModel):
    """Input schema for LLMLayer Scraper API."""

    url: str = Field(description="URL to scrape")
    format: Literal["markdown", "html", "screenshot", "pdf"] = Field(
        default="markdown", description="Output format"
    )
    include_images: bool = Field(
        default=True, description="Include images in markdown output"
    )
    include_links: bool = Field(
        default=True, description="Include links in markdown output"
    )


class LLMLayerScraperTool(BaseTool):
    name: str = "LLMLayer Scraper"
    description: str = (
        "Use this tool to extract clean content from any webpage. "
        "Returns structured content in markdown (default), HTML, PDF, or screenshot format. "
        "Best for: extracting article text, documentation, blog posts, or any web content for analysis. "
        "Use this when you have a specific URL and need its content extracted."
    )
    args_schema: type[BaseModel] = LLMLayerScraperInput

    api_key: str = ""
    timeout: int = 30
    include_metadata: bool = False

    def __init__(
        self,
        api_key: str = "",
        timeout: int = 30,
        include_metadata: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("LLMLAYER_API_KEY", "")
        self.timeout = timeout
        self.include_metadata = include_metadata

    def _run(
        self,
        url: str,
        format: str = "markdown",
        include_images: bool = True,
        include_links: bool = True,
    ) -> str:
        """Extract content from URL."""

        if not self.api_key:
            return "Error: LLMLAYER_API_KEY not set. Set it as environment variable or pass to tool initialization."

        payload = {
            "url": url,
            "format": format,
            "include_images": include_images,
            "include_links": include_links,
        }

        try:
            response = requests.post(
                "https://api.llmlayer.dev/api/v1/scrape",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    error_msg = detail.get("message", f"HTTP {response.status_code}")
                    error_code = detail.get("error_code", "unknown")
                    return f"Error: LLMLayer API error [{error_code}]: {error_msg}"
                except Exception:
                    return f"Error: HTTP {response.status_code} - {response.reason}"

            data = response.json()
            final_url = data.get("url", url)
            markdown = data.get("markdown", "")
            html = data.get("html")
            screenshot_data = data.get("screenshot_data")
            pdf_data = data.get("pdf_data")

            if format == "markdown":
                result = f"# Content from {final_url}\n\n{markdown}"
            elif format == "html":
                result = f"# HTML from {final_url}\n\n{html or markdown}"
            elif format == "screenshot":
                if screenshot_data:
                    result = f"# Screenshot from {final_url}\n\nBase64 data length: {len(screenshot_data)} characters\n\n[Screenshot captured as base64]"
                else:
                    result = (
                        f"# Screenshot from {final_url}\n\nNo screenshot data returned"
                    )
            elif format == "pdf":
                if pdf_data:
                    result = f"# PDF from {final_url}\n\nBase64 data length: {len(pdf_data)} characters\n\n[PDF generated as base64]"
                else:
                    result = f"# PDF from {final_url}\n\nNo PDF data returned"
            else:
                result = markdown

            if self.include_metadata:
                status_code = data.get("status_code", 0)
                cost = data.get("cost")
                result += f"\n\n---\nStatus: {status_code}"
                if cost is not None:
                    result += f" | Cost: ${cost:.6f}"

            return result

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds"
        except requests.exceptions.RequestException as e:
            return f"Error: {e!s}"


# ================================
# LLMLayer PDF Tool
# ================================


class LLMLayerPDFInput(BaseModel):
    """Input schema for LLMLayer PDF Content API."""

    url: str = Field(description="Direct URL to PDF document")


class LLMLayerPDFTool(BaseTool):
    name: str = "LLMLayer PDF Extractor"
    description: str = (
        "Use this tool to extract text content from PDF documents via URL. "
        "Returns full text content with page count. "
        "Best for: reading research papers, documents, reports in PDF format. "
        "Requires a direct link to a PDF file."
    )
    args_schema: type[BaseModel] = LLMLayerPDFInput

    api_key: str = ""
    timeout: int = 30
    include_metadata: bool = False

    def __init__(
        self,
        api_key: str = "",
        timeout: int = 30,
        include_metadata: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("LLMLAYER_API_KEY", "")
        self.timeout = timeout
        self.include_metadata = include_metadata

    def _run(self, url: str) -> str:
        """Extract text from PDF."""

        if not self.api_key:
            return "Error: LLMLAYER_API_KEY not set. Set it as environment variable or pass to tool initialization."

        try:
            response = requests.post(
                "https://api.llmlayer.dev/api/v1/get_pdf_content",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"url": url},
                timeout=self.timeout,
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    error_msg = detail.get("message", f"HTTP {response.status_code}")
                    error_code = detail.get("error_code", "unknown")
                    return f"Error: LLMLayer API error [{error_code}]: {error_msg}"
                except Exception:
                    return f"Error: HTTP {response.status_code} - {response.reason}"

            data = response.json()
            text = data.get("text", "")
            pages = data.get("pages", 0)
            final_url = data.get("url", url)

            result = f"# PDF Content from {final_url}\n\n**Pages:** {pages}\n\n{text}"

            if self.include_metadata:
                status_code = data.get("status_code", 0)
                cost = data.get("cost")
                result += f"\n\n---\nStatus: {status_code}"
                if cost is not None:
                    result += f" | Cost: ${cost:.6f}"

            return result

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds"
        except requests.exceptions.RequestException as e:
            return f"Error: {e!s}"


# ================================
# LLMLayer YouTube Tool
# ================================


class LLMLayerYouTubeInput(BaseModel):
    """Input schema for LLMLayer YouTube Transcript API."""

    url: str = Field(description="YouTube video URL")
    language: str | None = Field(
        default=None, description="Language code for transcript (e.g., 'en', 'es')"
    )


class LLMLayerYouTubeTool(BaseTool):
    name: str = "LLMLayer YouTube Transcript"
    description: str = (
        "Use this tool to extract transcripts from YouTube videos. "
        "Returns full video transcript text in specified language. "
        "Best for: analyzing video content, extracting information from tutorials, "
        "lectures, interviews, or any YouTube video with available transcripts."
    )
    args_schema: type[BaseModel] = LLMLayerYouTubeInput

    api_key: str = ""
    timeout: int = 30
    include_metadata: bool = False

    def __init__(
        self,
        api_key: str = "",
        timeout: int = 30,
        include_metadata: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv("LLMLAYER_API_KEY", "")
        self.timeout = timeout
        self.include_metadata = include_metadata

    def _run(self, url: str, language: str | None = None) -> str:
        """Extract YouTube transcript."""

        if not self.api_key:
            return "Error: LLMLAYER_API_KEY not set. Set it as environment variable or pass to tool initialization."

        payload = {"url": url}
        if language:
            payload["language"] = language

        try:
            response = requests.post(
                "https://api.llmlayer.dev/api/v1/youtube_transcript",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    error_msg = detail.get("message", f"HTTP {response.status_code}")
                    error_code = detail.get("error_code", "unknown")
                    return f"Error: LLMLayer API error [{error_code}]: {error_msg}"
                except Exception:
                    return f"Error: HTTP {response.status_code} - {response.reason}"

            data = response.json()
            transcript = data.get("transcript", "")
            final_url = data.get("url", url)
            lang = data.get("language", "unknown")

            result = f"# YouTube Transcript\n\n**URL:** {final_url}\n**Language:** {lang}\n\n{transcript}"

            if self.include_metadata:
                cost = data.get("cost")
                if cost is not None:
                    result += f"\n\n---\nCost: ${cost:.6f}"

            return result

        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {self.timeout} seconds"
        except requests.exceptions.RequestException as e:
            return f"Error: {e!s}"
