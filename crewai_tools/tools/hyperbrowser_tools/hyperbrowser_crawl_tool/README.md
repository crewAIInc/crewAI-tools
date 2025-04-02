# HyperbrowserCrawlTool

## Description

[Hyperbrowser](https://hyperbrowser.ai) is a platform for running and scaling headless browsers. The HyperbrowserCrawlTool lets you crawl websites starting from a specified URL, allowing you to systematically collect content from multiple pages within a domain.

Key Features:
- Multi-page Content Collection - Automatically crawl and extract content from multiple linked pages
- Customizable Crawl Behavior - Control which pages to include/exclude using patterns
- Format Options - Get results in various formats (markdown, HTML, links, screenshots)
- Bypass Anti-Bot Measures - Built-in stealth mode, ad blocking, automatic CAPTCHA solving, and rotating proxies

For more information about Hyperbrowser, please visit the [Hyperbrowser website](https://hyperbrowser.ai) or check the [Hyperbrowser docs](https://docs.hyperbrowser.ai).

## Installation

- Head to [Hyperbrowser](https://app.hyperbrowser.ai/) to sign up and generate an API key. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserCrawlTool` constructor.
- Install the [Hyperbrowser SDK](https://github.com/hyperbrowserai/python-sdk):

```
pip install hyperbrowser 'crewai[tools]'
```

## Example

Utilize the HyperbrowserCrawlTool as follows to allow your agent to crawl websites:

```python
from crewai_tools import HyperbrowserCrawlTool
from hyperbrowser.models import CreateSessionParams, ScrapeOptions
# Basic usage
tool = HyperbrowserCrawlTool()

# With custom API key
tool = HyperbrowserCrawlTool(api_key="your-api-key-here")

# Example usage with parameters
result = tool.run(
    url="https://example.com",
    max_pages=5,
    follow_links=True,
    include_patterns=["/blog/*"],
    exclude_patterns=["/author/*", "/tag/*"],
    session_options=CreateSessionParams(
        use_stealth=True,
        solve_captchas=True
    ),
    scrape_options=ScrapeOptions(
        formats=["markdown", "links"],
        only_main_content=True,
        exclude_tags=["span"],
        wait_for=2000
    )
)
```

## Arguments

`__init__` arguments:
- `api_key`: Optional. Specifies Hyperbrowser API key. Defaults to the `HYPERBROWSER_API_KEY` environment variable.

`run` arguments:
- `url`: The base URL to start crawling from.
- `max_pages`: Optional. The maximum number of pages to crawl before stopping. Default varies based on your Hyperbrowser plan.
- `follow_links`: Optional. When set to `True` (default), the crawler will follow links found on the pages it visits. When `False`, it will only visit the starting URL.
- `ignore_sitemap`: Optional. When set to `True`, the crawler will not pre-generate a list of URLs from potential sitemaps it finds. Default is `False`.
- `exclude_patterns`: Optional. An array of patterns specifying which URLs should be excluded from the crawl.
- `include_patterns`: Optional. An array of patterns specifying which URLs should be included in the crawl.
- `session_options`: Optional. Options for the browser session, such as:
  - `use_stealth`: Run in stealth mode to avoid detection
  - `solve_captchas`: Automatically solve CAPTCHAs
  - `use_proxy`: Use rotating proxies
  - `adblock`: Block ads for faster crawling
  - For more options, visit the [Hyperbrowser session parameters documentation](https://docs.hyperbrowser.ai/sessions/overview/session-parameters)
- `scrape_options`: Optional. Options for controlling the scraping behavior, such as:
  - `formats`: Array of formats to return (`html`, `links`, `markdown`, `screenshot`)
  - `only_main_content`: Whether to return only the main content of pages
  - `include_tags`: Array of HTML tags to include
  - `exclude_tags`: Array of HTML tags to exclude
  - `wait_for`: Time in milliseconds to wait after page load before scraping
  - For more options, see the [Hyperbrowser scrape options documentation](https://docs.hyperbrowser.ai/guides/scraping#scrape-options) 