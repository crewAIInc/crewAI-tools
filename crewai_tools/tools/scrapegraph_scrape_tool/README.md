# ScrapegraphScrapeTool

## Description
A comprehensive tool that leverages multiple Scrapegraph AI APIs to handle various web scraping scenarios. This tool supports:

- **SmartScraper**: AI-powered content extraction with custom prompts
- **Basic Scrape**: Raw HTML extraction with JavaScript rendering support
- **SearchScraper**: Search the web and scrape relevant results
- **AgenticScraper**: Automated browser interactions (login, form filling, etc.)
- **Crawl**: Multi-page crawling with AI extraction
- **Markdownify**: Convert webpages to markdown format

Ideal for targeted data collection, content analysis, automated research, and complex web automation tasks.

## Installation
Install the required packages:
```shell
pip install 'crewai[tools]'
```

## Example Usage

### SmartScraper (AI-powered extraction)
```python
from crewai_tools import ScrapegraphScrapeTool
from crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool import ScrapingMode

# AI-powered content extraction (default mode)
tool = ScrapegraphScrapeTool(api_key="your_api_key")
result = tool.run(
    website_url="https://www.example.com",
    mode=ScrapingMode.SMARTSCRAPER,
    user_prompt="Extract the main heading, summary, and key features"
)
```

### Basic HTML Scraping
```python
# Raw HTML extraction with JavaScript support
result = tool.run(
    website_url="https://www.example.com",
    mode=ScrapingMode.SCRAPE,
    render_heavy_js=True,  # Enable for JavaScript-heavy sites
    headers={"User-Agent": "Custom Bot 1.0"}
)
```

### Search and Scrape
```python
# Search the web and scrape relevant results
result = tool.run(
    mode=ScrapingMode.SEARCHSCRAPER,
    user_prompt="What are the latest features in Python 3.12?",
    num_results=5  # Number of search results to analyze
)
```

### Automated Interactions (AgenticScraper)
```python
# Automate browser interactions like login and form filling
result = tool.run(
    website_url="https://dashboard.example.com",
    mode=ScrapingMode.AGENTICSCRAPER,
    steps=[
        "Type user@example.com in email input box",
        "Type password123 in password input box",
        "Click on login button",
        "Wait for dashboard to load"
    ],
    use_session=True,
    user_prompt="Extract user profile information and account details",
    ai_extraction=True
)
```

### Multi-page Crawling
```python
# Crawl multiple pages with AI extraction
result = tool.run(
    website_url="https://blog.example.com",
    mode=ScrapingMode.CRAWL,
    user_prompt="Extract article titles, authors, and publication dates",
    depth=2,
    max_pages=10,
    same_domain_only=True,
    cache_website=True
)
```

### Markdown Conversion
```python
# Convert webpage to markdown format
result = tool.run(
    website_url="https://www.example.com/article",
    mode=ScrapingMode.MARKDOWNIFY
)
```

### Structured Data Extraction with Schema
```python
# Define output schema for structured data
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"},
        "description": {"type": "string"},
        "features": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

result = tool.run(
    website_url="https://shop.example.com/product/123",
    mode=ScrapingMode.SMARTSCRAPER,
    user_prompt="Extract product information",
    output_schema=schema
)
```

### Fixed Website URL Setup
```python
# Initialize with a fixed website URL
tool = ScrapegraphScrapeTool(
    website_url="https://www.example.com",
    mode=ScrapingMode.SMARTSCRAPER,
    api_key="your_api_key"
)
result = tool.run(user_prompt="Extract main content")
```

### Error Handling
```python
try:
    tool = ScrapegraphScrapeTool(api_key="your_api_key")
    result = tool.run(
        website_url="https://www.example.com",
        user_prompt="Extract the main heading"
    )
except ValueError as e:
    print(f"Configuration error: {e}")  # Handles invalid URLs or missing API keys
except RuntimeError as e:
    print(f"Scraping error: {e}")  # Handles API or network errors
```

## Arguments
- `website_url`: The URL of the website to scrape (required for most modes, except searchscraper)
- `mode`: Scraping mode (`smartscraper`, `scrape`, `searchscraper`, `agenticscraper`, `crawl`, `markdownify`)
- `user_prompt`: Custom instructions for content extraction (required for AI-powered modes)
- `render_heavy_js`: Enable JavaScript rendering for dynamic content (scrape mode)
- `headers`: Custom HTTP headers for the request
- `output_schema`: JSON schema for structured output (smartscraper, agenticscraper, crawl modes)
- `steps`: Automation steps for agenticscraper mode
- `use_session`: Use session for agenticscraper mode
- `ai_extraction`: Enable AI extraction for agenticscraper mode
- `num_results`: Number of search results for searchscraper mode (3-20)
- `depth`: Crawl depth for crawl mode
- `max_pages`: Maximum pages to crawl for crawl mode
- `same_domain_only`: Stay within same domain for crawl mode
- `cache_website`: Cache website content for crawl mode
- `api_key`: Your Scrapegraph API key (required, can be set via SCRAPEGRAPH_API_KEY environment variable)

## Environment Variables
- `SCRAPEGRAPH_API_KEY`: Your Scrapegraph API key, you can obtain one [here](https://scrapegraphai.com)

## Rate Limiting and Credits
The Scrapegraph API uses a credit-based system that varies based on your subscription plan:

- **SmartScraper**: 10 credits per request
- **Scrape**: 1 credit per request
- **SearchScraper**: 10 credits per result (default 3 results = 30 credits)
- **AgenticScraper**: 20 credits per request
- **Crawl**: 10 credits per page crawled
- **Markdownify**: 5 credits per request

Best practices:
- Implement appropriate delays between requests when processing multiple URLs
- Handle rate limit errors gracefully in your application
- Choose the most efficient mode for your use case
- Use caching when appropriate to avoid repeated requests
- Monitor your credit usage on the Scrapegraph dashboard

## Error Handling
The tool may raise the following exceptions:
- `ValueError`: When API key is missing or URL format is invalid
- `RuntimeError`: When scraping operation fails (network issues, API errors)
- `RateLimitError`: When API rate limits are exceeded

## Scraping Modes

### SmartScraper (Default)
- **Use case**: AI-powered content extraction with custom prompts
- **Output**: Structured data based on your prompt
- **Best for**: Extracting specific information from web pages

### Scrape
- **Use case**: Raw HTML extraction
- **Output**: Raw HTML content
- **Best for**: Getting complete page source, especially for further processing

### SearchScraper
- **Use case**: Search the web and analyze results
- **Output**: Synthesized information from multiple sources
- **Best for**: Research tasks, finding current information

### AgenticScraper
- **Use case**: Automated browser interactions
- **Output**: Data from pages requiring interaction (login, forms, etc.)
- **Best for**: Accessing protected content, form automation

### Crawl
- **Use case**: Multi-page data extraction
- **Output**: Aggregated data from multiple pages
- **Best for**: Comprehensive site analysis, bulk data extraction

### Markdownify
- **Use case**: Convert web content to markdown
- **Output**: Clean markdown format
- **Best for**: Content migration, documentation creation

## Best Practices
1. Choose the appropriate mode for your use case
2. Always validate URLs before making requests
3. Implement proper error handling as shown in examples
4. Use structured schemas for consistent data extraction
5. Consider rate limits when processing multiple requests
6. Monitor your API usage through the Scrapegraph dashboard
7. Use caching for crawl mode when processing large sites
8. Test automation steps thoroughly for agenticscraper mode
