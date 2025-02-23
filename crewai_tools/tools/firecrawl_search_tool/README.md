# FirecrawlSearchTool

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

Utilize the `FirecrawlSearchTool` as follows to allow your agent to search the web:

```python
from crewai_tools import FirecrawlSearchTool

tool = FirecrawlSearchTool(config={"limit": 5})
tool.run(query="firecrawl web scraping")
```

## Arguments

- `api_key`: Optional. Specifies Firecrawl API key. Defaults is the `FIRECRAWL_API_KEY` environment variable.
- `config`: Optional. It contains Firecrawl API parameters.

This is the default configuration:

```python
{
  "limit": 5,
  "tbs": None,
  "lang": "en",
  "country": "us",
  "location": None,
  "timeout": 60000
}
```

| Parameter        | Required | Default                     | Description                                        |
| ---------------- | -------- | --------------------------- | -------------------------------------------------- |
| `api_key`        | ✅       | `FIRECRAWL_API_KEY` env var | Specifies Firecrawl API key                        |
| `query`          | ✅       | -                           | The search query string to be used for searching   |
| `limit`          | ❌       | `5`                         | Maximum number of results to return (between 1-10) |
| `tbs`            | ❌       | -                           | Time-based search parameter                        |
| `lang`           | ❌       | `"en"`                      | Language code for search results                   |
| `country`        | ❌       | `"us"`                      | Country code for search results                    |
| `location`       | ❌       | -                           | Location parameter for search results              |
| `timeout`        | ❌       | `60000`                     | Timeout in milliseconds                            |
| `scrape_options` | ❌       | -                           | Options for scraping search results                |
