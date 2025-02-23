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

Utilize the `FirecrawlCrawlWebsiteTool` as follows to allow your agent to load websites:

```python
from crewai_tools import FirecrawlCrawlWebsiteTool

tool = FirecrawlCrawlWebsiteTool(url='firecrawl.dev')
```

## Arguments

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
