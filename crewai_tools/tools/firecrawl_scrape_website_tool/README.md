# FirecrawlScrapeWebsiteTool

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

Utilize the `FirecrawlScrapeWebsiteTool` as follows to allow your agent to load websites:

```python
from crewai_tools import FirecrawlScrapeWebsiteTool

tool = FirecrawlScrapeWebsiteTool(config={"formats": ['html']})
tool.run(url="firecrawl.dev")
```

## Arguments

- `api_key`: Optional. Specifies Firecrawl API key. Defaults is the `FIRECRAWL_API_KEY` environment variable.
- `config`: Optional. It contains Firecrawl API parameters.

This is the default configuration:

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

> Documentation for the parameters can be found
> [here](https://docs.firecrawl.dev/api-reference/endpoint/scrape).

| Parameter                    | Required | Default                     | Description                                                                                                                                                                                                                                                                                       |
| ---------------------------- | -------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_key`                    | ✅       | `FIRECRAWL_API_KEY` env var | Specifies Firecrawl API key                                                                                                                                                                                                                                                                       |
| `url`                        | ✅       | -                           | The URL to scrape                                                                                                                                                                                                                                                                                 |
| `formats`                    | ❌       | `["markdown"]`              | List of formats to include in the output (`markdown`, `html`, `rawHtml`, `links`, `screenshot`, `screenshot@fullPage`, `json`)                                                                                                                                                                    |
| `only_main_content`          | ❌       | `true`                      | Only return the main content of the page excluding headers, navs, footers, etc.                                                                                                                                                                                                                   |
| `include_tags`               | ❌       | -                           | List of HTML tags to include in the output                                                                                                                                                                                                                                                        |
| `exclude_tags`               | ❌       | -                           | List of HTML tags to exclude from the output                                                                                                                                                                                                                                                      |
| `headers`                    | ❌       | -                           | Headers to send with the request (e.g., cookies, user-agent)                                                                                                                                                                                                                                      |
| `wait_for`                   | ❌       | `0`                         | Delay in milliseconds before fetching content                                                                                                                                                                                                                                                     |
| `mobile`                     | ❌       | `false`                     | Set to true to emulate scraping from a mobile device                                                                                                                                                                                                                                              |
| `skip_tls_verification`      | ❌       | `false`                     | Skip TLS certificate verification when making requests                                                                                                                                                                                                                                            |
| `timeout`                    | ❌       | `30000`                     | Timeout in milliseconds for the request                                                                                                                                                                                                                                                           |
| `json_options`               | ❌       | -                           | Options for JSON extraction from the page                                                                                                                                                                                                                                                         |
| `json_options.schema`        | ❌       | -                           | The schema to use for the extraction                                                                                                                                                                                                                                                              |
| `json_options.system_prompt` | ❌       | -                           | The system prompt to use for the extraction                                                                                                                                                                                                                                                       |
| `json_options.prompt`        | ❌       | -                           | The prompt to use for the extraction without a schema                                                                                                                                                                                                                                             |
| `location`                   | ❌       | -                           | Location settings for the request (country code and languages)                                                                                                                                                                                                                                    |
| `remove_base64_images`       | ❌       | -                           | Remove base64 encoded images from output                                                                                                                                                                                                                                                          |
| `block_ads`                  | ❌       | `true`                      | Enables ad-blocking and cookie popup blocking.                                                                                                                                                                                                                                                    |
| `actions`                    | ❌       | -                           | List of actions to perform on the page before scraping (e.g., click, scroll, wait)                                                                                                                                                                                                                |
| `proxy`                      | ❌       | -                           | Specifies the type of proxy to use (`basic`, `stealth`).<br>**basic:** Proxies for scraping sites with none to basic anti-bot solutions. Fast and usually works.<br>**stealth:** Stealth proxies for scraping sites with advanced anti-bot solutions. Slower, but more reliable on certain sites. |
