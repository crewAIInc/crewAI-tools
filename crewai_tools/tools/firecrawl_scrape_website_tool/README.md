# FirecrawlScrapeWebsiteTool

## Description

[Firecrawl](https://firecrawl.dev) is a platform for crawling and convert any website into clean markdown or structured data.

## Installation

- Get an API key from [firecrawl.dev](https://firecrawl.dev) and set it in environment variables (`FIRECRAWL_API_KEY`).
- Install the [Firecrawl SDK](https://github.com/mendableai/firecrawl) along with `crewai[tools]` package:

```
pip install firecrawl-py 'crewai[tools]'
```

## Example

Utilize the FirecrawlScrapeWebsiteTool as follows to allow your agent to load websites:

```python
from crewai_tools import FirecrawlScrapeWebsiteTool

# Method 1: Pass URL when running the tool
tool = FirecrawlScrapeWebsiteTool(config={"formats": ['html']})
tool.run(url="firecrawl.dev")

# Method 2: Pass URL when creating the tool
tool = FirecrawlScrapeWebsiteTool(url="firecrawl.dev")
tool.run()

# Method 3: Pass URL in both places (URL in run method takes precedence)
tool = FirecrawlScrapeWebsiteTool(url="firecrawl.dev")
tool.run(url="different-site.com")  # This will scrape different-site.com
```

## Arguments

- `api_key`: Optional. Specifies Firecrawl API key. Defaults is the `FIRECRAWL_API_KEY` environment variable.
- `url`: Optional. The URL to scrape. Can be provided when creating the tool or when calling run().
- `config`: Optional. It contains Firecrawl API parameters.


This is the default configuration

```python
{
    "formats": ["markdown"],
    "only_main_content": True,
    "include_tags": [],
    "exclude_tags": [],
    "headers": {},
    "wait_for": 0,
}
```


