# FirecrawlSearchTool

## Description

[Firecrawl](https://firecrawl.dev) is a platform for crawling and convert any website into clean markdown or structured data.

The [search endpoint](https://docs.firecrawl.dev/api-reference/endpoint/search) combines web search (SERP) with Firecrawl's scraping capabilities to return full page content for any query.

## Installation

- Get an API key from [firecrawl.dev](https://firecrawl.dev) and set it in environment variables (`FIRECRAWL_API_KEY`).
- Install the [Firecrawl SDK](https://github.com/mendableai/firecrawl) along with `crewai[tools]` package:

```
pip install firecrawl-py 'crewai[tools]'
```

## Example

Utilize the FirecrawlSearchTool as follows to allow your agent to load websites:

```python
from crewai_tools import FirecrawlSearchTool

# Initialize the FirecrawlSearchTool with named parameters
tool = FirecrawlSearchTool(query='what is firecrawl?', limit=5, lang='en', country='us')
print(tool.run())

# Or use the `run` method with named parameters
tool = FirecrawlSearchTool()
print(tool.run(query='what is firecrawl?', limit=5, scrapeOptions={'formats': ['markdown', 'html']}))
```

## Output format

```json
{
  "success": true,
  "data": [
    {
      "title": "<string>",
      "description": "<string>",
      "url": "<string>",
      "markdown": "<string>",
      "html": "<string>",
      "rawHtml": "<string>",
      "links": [
        "<string>"
      ],
      "screenshot": "<string>",
      "metadata": {
        "title": "<string>",
        "description": "<string>",
        "sourceURL": "<string>",
        "statusCode": 123,
        "error": "<string>"
      }
    }
  ],
  "warning": "<string>"
}
```

## Arguments

| Argument       | Type     | Description                                                                                                                         |
|:---------------|:---------|:-------------------------------------------------------------------------------------------------------------------------------------|
| **api_key**     | `string` | **Optional**. Specifies Firecrawl API key. Defaults is the `FIRECRAWL_API_KEY` environment variable. |
| **query** | `string` | **Required**. The search query. |
| **limit** | `integer` | **Optional**. Maximum number of results to return. Default: 5. Required range: 1 <= x <= 10 |
| **tbs** | `string` | **Optional**. Time-based search parameter. |
| **lang** | `string` | **Optional**. Language code for search results. Default: "en". |
| **country** | `string` | **Optional**. Country code for search results. Default: "us". |
| **location** | `string` | **Optional**. Location parameter for search results. |
| **timeout** | `string` | **Optional**. Timeout in milliseconds. Default: 60000. |
| **scrapeOptions** | `object` | **Optional**. Options for scraping search results. |
| **scrapeOptions.formats** | `enum<string>[]` | **Optional**. Formats to include in the output. Available options: `markdown`, `html`, `rawHtml`, `links`, `screenshot`, `screenshot@fullPage`, `extract`. |
