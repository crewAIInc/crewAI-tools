# HyperbrowserExtractTool

## Description

[Hyperbrowser](https://hyperbrowser.ai) is a platform for running and scaling headless browsers. The HyperbrowserExtractTool allows you to extract structured data from websites using Hyperbrowser's AI-powered extraction capabilities, making it easy to convert unstructured web content into structured, usable data formats.

Key Features:
- AI-Powered Extraction - Extract structured data from any webpage with a simple prompt or schema
- Schema Validation - Define exactly what data structure you want with JSON schema or Pydantic models
- Multi-page Extraction - Crawl multiple pages for comprehensive data collection with a single request
- Bypass Protection - Built-in stealth mode, proxy rotation, and CAPTCHA solving for reliable extraction
- Scale Effortlessly - Process multiple extraction jobs in parallel without infrastructure management

For more information about Hyperbrowser, please visit the [Hyperbrowser website](https://hyperbrowser.ai) or check out the [Hyperbrowser docs](https://docs.hyperbrowser.ai).

## Installation

- Head to [Hyperbrowser](https://app.hyperbrowser.ai/) to sign up and generate an API key. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserExtractTool` constructor.
- Install the [Hyperbrowser SDK](https://github.com/hyperbrowserai/python-sdk):

```
pip install hyperbrowser 'crewai[tools]'
```

## Example

Utilize the HyperbrowserExtractTool as follows to allow your agent to extract structured data from websites:

```python
from crewai_tools import HyperbrowserExtractTool
from pydantic import BaseModel
from typing import List

# Define a schema for the data you want to extract
class PricingModel(BaseModel):
    plan: str
    price: str
    features: List[str]

class ProductInfo(BaseModel):
    product_name: str
    product_overview: str
    key_features: List[str]
    pricing: List[PricingModel]

# Create the tool
tool = HyperbrowserExtractTool()

# Run the extraction with a schema and prompt
result = tool.run(
    urls=["https://hyperbrowser.ai"],
    prompt="Extract the product name, an overview of the product, its key features, and a list of its pricing plans from the page.",
    schema_=ProductInfo,
)

print(result.data)
```

## Arguments

`__init__` arguments:
- `api_key`: Optional. Specifies Hyperbrowser API key. Defaults to the `HYPERBROWSER_API_KEY` environment variable.

`run` arguments:
- `urls`: List of URLs to extract data from. You can add `/*` to a URL to crawl linked pages on the same domain.
- `prompt`: Optional. A descriptive prompt explaining what data to extract and how it should be structured. Required if `schema_` is not provided.
- `schema_`: Optional. A Pydantic model or JSON schema defining the structure of the data to be returned. Required if `prompt` is not provided.
- `system_prompt`: Optional. A system prompt that provides additional context for the extraction.
- `wait_for`: Optional. Time in milliseconds to wait after page load before extracting data (useful for dynamic content).
- `session_options`: Optional. Configuration options for the browser session, such as using proxies or solving CAPTCHAs.
- `max_links`: Optional. Maximum number of links to follow when crawling from a URL with `/*`.

For more detailed information on extraction parameters, visit [Hyperbrowser Extract Documentation](https://docs.hyperbrowser.ai/web-scraping/extract). 