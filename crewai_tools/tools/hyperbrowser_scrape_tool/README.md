# HyperbrowserScrapeTool

## Description

[Hyperbrowser](https://hyperbrowser.ai) is a platform for running and scaling headless browsers. The `HyperbrowserScrapeTool` allows you to easily scrape web pages and extract their content using the Hyperbrowser API.

Key Features:
- Powerful Scraping - Extract content from any webpage in multiple formats (markdown, HTML, links, screenshots)
- Customizable Extraction - Include or exclude specific HTML tags, focus on main content
- Anti-Bot Bypassing - Built-in stealth mode, proxy support, and automatic CAPTCHA solving
- Session Options - Configure browser behavior with various session parameters
- Flexible Response Formats - Get data in multiple formats based on your needs

For more information about Hyperbrowser, please visit the [Hyperbrowser website](https://hyperbrowser.ai) or check out the [Hyperbrowser docs](https://docs.hyperbrowser.ai/guides/scraping) for detailed documentation on the scraping capabilities.

## Installation

- Head to [Hyperbrowser](https://app.hyperbrowser.ai/) to sign up and generate an API key. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserScrapeTool` constructor.
- Install the [Hyperbrowser SDK](https://github.com/hyperbrowserai/python-sdk):

```
pip install hyperbrowser 'crewai[tools]'
```

## Example

Utilize the HyperbrowserScrapeTool as follows to allow your agent to scrape websites:

```python
from crewai_tools import HyperbrowserScrapeTool
from hyperbrowser.models import CreateScrapeParams, SessionOptions

# Basic usage
tool = HyperbrowserScrapeTool()

# Advanced usage with options
tool = HyperbrowserScrapeTool(api_key="your-api-key")
result = tool.run(
    url="https://example.com",
    session_options=CreateSessionParams(
        use_stealth=True,
        solve_captchas=True,
        use_proxy=True
    ),
    scrape_options=ScrapeOptions(
        formats=["markdown", "html", "links"],
        only_main_content=True,
        exclude_tags=["span", "footer"],
        wait_for=2000
    )
)
```

## Arguments

`__init__` arguments:
- `api_key`: Optional. Specifies Hyperbrowser API key. Defaults to the `HYPERBROWSER_API_KEY` environment variable.

`_run` arguments:
- `url`: Required. The URL of the webpage to scrape.
- `session_options`: Optional. Configure browser behavior with options like:
  - `use_stealth`: Boolean. Enables stealth mode to avoid detection.
  - `solve_captchas`: Boolean. Automatically solve CAPTCHAs.
  - `use_proxy`: Boolean. Use rotating proxies.
  - `adblock`: Boolean. Block ads during scraping.

- `scrape_options`: Optional. Configure scraping behavior with options like:
  - `formats`: Array of strings. Response formats: "markdown", "html", "links", "screenshot".
  - `include_tags`: Array of strings. HTML tags, classes, or IDs to include.
  - `exclude_tags`: Array of strings. HTML tags, classes, or IDs to exclude.
  - `only_main_content`: Boolean. Extract only the main content of the page.
  - `wait_for`: Number. Milliseconds to wait after page load before scraping.
  - `timeout`: Number. Maximum time in milliseconds to wait for page load.
  - `wait_until`: String. Page load condition: "load", "domcontentloaded", "networkidle".
  - `screenshot_options`: Object. Configure screenshot behavior if format includes "screenshot".

For a comprehensive guide to all available options, visit the [Hyperbrowser Scraping Documentation](https://docs.hyperbrowser.ai/guides/scraping). 