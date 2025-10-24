# FirecrawlCrawlWebsiteTool

## Description

[Firecrawl](https://firecrawl.dev) is a platform for crawling and convert any website into clean
markdown or structured data.

## Installation

- Get an API key from [firecrawl.dev](https://firecrawl.dev) and set it in environment variables
  (`FIRECRAWL_API_KEY`).
- Install the [Firecrawl SDK](https://github.com/mendableai/firecrawl) along with `crewai[tools]`
  package:

```
pip install firecrawl-py 'crewai[tools]'
```

## Example

Utilize the `FirecrawlCrawlWebsiteTool` as follows to allow your agent to search the web:

```python
from crewai_tools import FirecrawlCrawlWebsiteTool
from firecrawl import ScrapeOptions

tool = FirecrawlCrawlWebsiteTool(
    config={
        "limit": 100,
        "scrape_options": ScrapeOptions(formats=["markdown"]),
    }
)
tool.run(url="firecrawl.dev")
```

## Arguments

- `api_key`: Optional. Specifies Firecrawl API key. Defaults is the `FIRECRAWL_API_KEY` environment variable.
- `config`: Optional. It contains Firecrawl API parameters.

This is the default configuration

```python
from firecrawl import ScrapeOptions
{
  "max_depth": 2,
  "ignore_sitemap": True,
  "limit": 100,
  "allow_backward_links": False,
  "allow_external_links": False,
  "scrape_options": ScrapeOptions(
    formats=["markdown", "screenshot", "links"],
    only_main_content=True,
    timeout=30000
  )
}
```

> Documentation for the parameters can be found
> [here](https://docs.firecrawl.dev/api-reference/endpoint/crawl-post).

| Parameter                 | Required | Default                     | Description                                                              |
| ------------------------- | -------- | --------------------------- | ------------------------------------------------------------------------ |
| `api_key`                 | ✅       | `FIRECRAWL_API_KEY` env var | Specifies Firecrawl API key                                              |
| `url`                     | ✅       | -                           | The base URL to start crawling from                                      |
| `exclude_paths`           | ❌       | -                           | URL patterns to exclude from the crawl                                   |
| `include_paths`           | ❌       | -                           | URL patterns to include in the crawl                                     |
| `max_depth`               | ❌       | `2`                         | Maximum depth to crawl relative to the entered URL                       |
| `ignore_sitemap`          | ❌       | `false`                     | Ignore the website sitemap when crawling                                 |
| `ignore_query_parameters` | ❌       | `false`                     | Do not re-scrape the same path with different (or none) query parameters |
| `limit`                   | ❌       | `10000`                     | Maximum number of pages to crawl                                         |
| `allow_backward_links`    | ❌       | `false`                     | Enables crawling previously linked pages                                 |
| `allow_external_links`    | ❌       | `false`                     | Allows crawling external websites                                        |
| `webhook`                 | ❌       | -                           | Webhook configuration for crawl notifications                            |
| `scrape_options`          | ❌       | -                           | Options for scraping pages during crawl                                  |
