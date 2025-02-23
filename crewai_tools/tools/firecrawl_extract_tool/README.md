# FirecrawlExtractTool

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

Utilize the `FirecrawlExtractTool` as follows to extract structured data from websites:

```python
from crewai_tools import FirecrawlExtractTool

# Example schema for product information
schema = {
    "name": {"type": "string", "description": "Product name"},
    "price": {"type": "number", "description": "Product price"},
    "description": {"type": "string", "description": "Product description"}
}

tool = FirecrawlExtractTool(
    urls=['https://example.com/products/*'],
    prompt="Extract product information from these pages",
    schema=schema,
    enable_web_search=True,
    include_subdomains=False,
    show_sources=True,
    scrape_options={"formats": ["markdown", "html"]}
)
```

## Arguments

| Parameter            | Required | Default                     | Description                                                                                       |
| -------------------- | -------- | --------------------------- | ------------------------------------------------------------------------------------------------- |
| `api_key`            | ✅       | `FIRECRAWL_API_KEY` env var | Specifies Firecrawl API key                                                                       |
| `urls`               | ✅       | -                           | List of URLs to extract data from. URLs can include glob patterns                                 |
| `prompt`             | ❌       | -                           | The prompt describing what information to extract from the pages                                  |
| `schema`             | ❌       | -                           | JSON schema defining the structure of the data to extract                                         |
| `enable_web_search`  | ❌       | `false`                     | When true, the extraction will use web search to find additional data                             |
| `ignore_site_map`    | ❌       | `false`                     | When true, the extraction will not use the _sitemap.xml_ to find additional data                  |
| `include_subdomains` | ❌       | `true`                      | When true, subdomains of the provided URLs will also be scanned                                   |
| `show_sources`       | ❌       | `false`                     | When true, the sources used to extract the data will be included in the response as `sources` key |
| `scrape_options`     | ❌       | `{}`                        | Additional options for the crawl request                                                          |
