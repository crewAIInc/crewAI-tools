# ScrapeGraph AI Multi-Method Scraper Tool

## Description
A comprehensive CrewAI tool that integrates with ScrapeGraph AI to provide intelligent web scraping capabilities using multiple methods. This enhanced tool supports 6 different scraping approaches, from basic content extraction to complex interactive automation.

## Features

The tool supports 6 different scraping methods:

### 1. SmartScraper (Default)
Intelligent content extraction using AI to understand and extract relevant information from web pages.

```python
from crewai_tools import ScrapegraphScrapeTool, ScrapeMethod

tool = ScrapegraphScrapeTool()
result = tool.run(
    website_url="https://example.com",
    method=ScrapeMethod.SMARTSCRAPER,
    user_prompt="Extract company information"
)
```

### 2. SearchScraper
Search-based content gathering from multiple sources across the web.

```python
result = tool.run(
    method=ScrapeMethod.SEARCHSCRAPER,
    user_prompt="Latest AI developments",
    num_results=5  # 1-20 sources
)
```

### 3. AgenticScraper
Interactive scraping with automated actions like clicking buttons, filling forms, etc.

```python
result = tool.run(
    website_url="https://example.com",
    method=ScrapeMethod.AGENTICSCRAPER,
    steps=[
        "Type email@example.com in email field",
        "Type password123 in password field",
        "Click login button"
    ],
    use_session=True,
    ai_extraction=True,
    user_prompt="Extract dashboard information"
)
```

### 4. Crawl
Multi-page crawling with depth control and domain restrictions.

```python
result = tool.run(
    website_url="https://example.com",
    method=ScrapeMethod.CRAWL,
    user_prompt="Extract all product information",
    depth=2,
    max_pages=10,
    same_domain_only=True,
    cache_website=True
)
```

### 5. Scrape
Raw HTML extraction with JavaScript rendering support.

```python
result = tool.run(
    website_url="https://example.com",
    method=ScrapeMethod.SCRAPE,
    render_heavy_js=True,
    headers={"User-Agent": "Custom Agent"}
)
```

### 6. Markdownify
Convert web content to markdown format.

```python
result = tool.run(
    website_url="https://example.com",
    method=ScrapeMethod.MARKDOWNIFY
)
```

## Installation
Install the required packages:
```shell
pip install 'crewai[tools]'
pip install scrapegraph-py
```

## Schema Support

All methods support structured data extraction using JSON schemas:

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "authors": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

result = tool.run(
    website_url="https://example.com",
    method=ScrapeMethod.SMARTSCRAPER,
    data_schema=schema
)
```

## Configuration Options

- `method`: Scraping method (ScrapeMethod enum)
- `render_heavy_js`: Enable JavaScript rendering for dynamic content
- `headers`: Custom HTTP headers
- `data_schema`: JSON schema for structured data extraction
- `steps`: Action steps for agentic scraping (required for AgenticScraper)
- `num_results`: Number of search results (1-20, for SearchScraper)
- `depth`: Crawling depth (1-5, for Crawl)
- `max_pages`: Maximum pages to crawl
- `same_domain_only`: Restrict crawling to same domain
- `cache_website`: Cache content for faster subsequent requests
- `use_session`: Maintain session state for agentic scraping
- `ai_extraction`: Enable AI extraction for agentic scraping
- `timeout`: Request timeout (10-600 seconds)

## Setup

1. Set your API key:
```bash
export SCRAPEGRAPH_API_KEY="your-api-key-here"
```

Or use a `.env` file:
```
SCRAPEGRAPH_API_KEY=your-api-key-here
```

2. Initialize the tool:
```python
from crewai_tools import ScrapegraphScrapeTool, ScrapeMethod

# Basic initialization
tool = ScrapegraphScrapeTool()

# With fixed URL
tool = ScrapegraphScrapeTool(website_url="https://example.com")

# With custom API key
tool = ScrapegraphScrapeTool(api_key="your-api-key")
```

## Advanced Examples

### Interactive Form Automation
```python
result = tool.run(
    website_url="https://dashboard.example.com",
    method=ScrapeMethod.AGENTICSCRAPER,
    steps=[
        "Type username@email.com in the email input field",
        "Type mypassword in the password input field",
        "Click the login button",
        "Wait for the dashboard to load",
        "Click on the profile section"
    ],
    use_session=True,
    ai_extraction=True,
    user_prompt="Extract user profile information and account details"
)
```

### Multi-Source Research
```python
result = tool.run(
    method=ScrapeMethod.SEARCHSCRAPER,
    user_prompt="Latest developments in web scraping technology and tools",
    num_results=10
)
print(f"Research findings: {result['result']}")
print(f"Sources: {result['reference_urls']}")
```

### Comprehensive Website Crawling
```python
result = tool.run(
    website_url="https://company.com",
    method=ScrapeMethod.CRAWL,
    user_prompt="Extract all product information, pricing, and company details",
    depth=3,
    max_pages=20,
    same_domain_only=True,
    cache_website=True,
    data_schema={
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "string"},
                        "description": {"type": "string"}
                    }
                }
            },
            "company_info": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "contact": {"type": "string"}
                }
            }
        }
    }
)
```

## Error Handling

The tool handles various error conditions:

```python
from crewai_tools import ScrapegraphScrapeTool, ScrapegraphError, RateLimitError

try:
    tool = ScrapegraphScrapeTool()
    result = tool.run(
        website_url="https://example.com",
        method=ScrapeMethod.SMARTSCRAPER
    )
except ValueError as e:
    print(f"Configuration error: {e}")  # Invalid parameters or missing API key
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")  # API rate limits exceeded
except ScrapegraphError as e:
    print(f"ScrapeGraph API error: {e}")  # General API errors
except RuntimeError as e:
    print(f"Scraping operation failed: {e}")  # Other runtime errors
```

## Environment Variables
- `SCRAPEGRAPH_API_KEY`: Your ScrapeGraph API key, you can obtain one [here](https://scrapegraphai.com)

## Rate Limiting
The ScrapeGraph API has rate limits that vary based on your subscription plan. Consider the following best practices:
- Implement appropriate delays between requests when processing multiple URLs
- Handle rate limit errors gracefully in your application
- Check your API plan limits on the ScrapeGraph dashboard
- Use caching for frequently accessed content

## Best Practices

1. **Method Selection**: Choose the appropriate method for your use case:
   - Use `SmartScraper` for general content extraction
   - Use `SearchScraper` for research across multiple sources
   - Use `AgenticScraper` for sites requiring interaction
   - Use `Crawl` for comprehensive site mapping
   - Use `Scrape` for raw HTML when you need full control
   - Use `Markdownify` for content formatting

2. **Schema Design**: When using `data_schema`, design clear, specific schemas for better extraction results

3. **Session Management**: Use `use_session=True` for `AgenticScraper` when you need to maintain state across interactions

4. **Performance**: Enable `cache_website=True` for crawling operations to improve performance

5. **Error Handling**: Always implement proper error handling as shown in examples

6. **Validation**: Validate URLs and parameters before making requests

7. **Monitoring**: Monitor your API usage through the ScrapeGraph dashboard

## Examples

See `examples/scrapegraph_tool_examples.py` for complete working examples of all methods.

## API Reference

- **ScrapeMethod**: Enum of available scraping methods (SMARTSCRAPER, SEARCHSCRAPER, AGENTICSCRAPER, CRAWL, SCRAPE, MARKDOWNIFY)
- **ScrapegraphScrapeToolSchema**: Input validation schema for flexible URL usage
- **FixedScrapegraphScrapeToolSchema**: Schema for tools with fixed URLs
- **ScrapegraphError**: Base exception class for ScrapeGraph-related errors
- **RateLimitError**: Specialized exception for rate limiting scenarios