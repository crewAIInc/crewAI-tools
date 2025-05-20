# OxylabsAmazonProductScraperTool

Scrape any website with `OxylabsAmazonProductScraperTool`

## Installation

```
pip install 'crewai[tools]' oxylabs
```

## Example

```python
from crewai_tools import OxylabsAmazonProductScraperTool

tool = OxylabsAmazonProductScraperTool(
    username="OXYLABS_USERNAME",
    password="OXYLABS_PASSWORD",
)
result = tool.run(query="AAAAABBBBCC")

print(result.results[0].content)
```

## Arguments

- `username`: Oxylabs username.
- `password`: Oxylabs password.

Get the credentials by creating an Oxylabs Account [here](https://oxylabs.io).

## Advanced example

Check out the Oxylabs [documentation](https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/product) to get the full list of parameters.

```python
from crewai_tools import OxylabsAmazonProductScraperTool

tool = OxylabsAmazonProductScraperTool(
    username="OXYLABS_USERNAME",
    password="OXYLABS_PASSWORD",
)
result = tool.run(
    query="AAAAABBBBCC",
    domain="nl",
    parse=True,
    context=[
        {
            "key": "autoselect_variant", 
            "value": True
        }
    ]
)

print(result.results[0].content)
```
