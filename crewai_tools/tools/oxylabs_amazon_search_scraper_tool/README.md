# OxylabsAmazonSearchScraperTool

Scrape any website with `OxylabsAmazonSearchScraperTool`

## Installation

```
pip install 'crewai[tools]' oxylabs
```

## Example

```python
from crewai_tools import OxylabsAmazonSearchScraperTool

tool = OxylabsAmazonSearchScraperTool(
    username="OXYLABS_USERNAME",
    password="OXYLABS_PASSWORD",
)
result = tool.run(query="headsets")

print(result.results[0].content)
```

## Arguments

- `username`: Oxylabs username.
- `password`: Oxylabs password.

Get the credentials by creating an Oxylabs Account [here](https://oxylabs.io).

## Advanced example

Check out the Oxylabs [documentation](https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/amazon/search) to get the full list of parameters.

```python
from crewai_tools import OxylabsAmazonSearchScraperTool

tool = OxylabsAmazonSearchScraperTool(
    username="OXYLABS_USERNAME",
    password="OXYLABS_PASSWORD",
)
result = tool.run(
    query='nirvana tshirt',
    domain='nl',
    start_page=2,
    pages=2,
    parse=True,
    context=[
        {'key': 'category_id', 'value': 16391693031}
    ],
)

print(result.results[0].content)
```
