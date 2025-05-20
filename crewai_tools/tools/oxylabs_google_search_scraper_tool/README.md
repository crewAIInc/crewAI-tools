# OxylabsGoogleSearchScraperTool

Scrape any website with `OxylabsGoogleSearchScraperTool`

## Installation

```
pip install 'crewai[tools]' oxylabs
```

## Example

```python
from crewai_tools import OxylabsGoogleSearchScraperTool

tool = OxylabsGoogleSearchScraperTool(
    username="OXYLABS_USERNAME",
    password="OXYLABS_PASSWORD",
)
result = tool.run(query="iPhone 16")

print(result.results[0].content)
```

## Arguments

- `username`: Oxylabs username.
- `password`: Oxylabs password.

Get the credentials by creating an Oxylabs Account [here](https://oxylabs.io).

## Advanced example

Check out the Oxylabs [documentation](https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/google/search/search) to get the full list of parameters.

```python
from crewai_tools import OxylabsGoogleSearchScraperTool

tool = OxylabsGoogleSearchScraperTool(
    username="OXYLABS_USERNAME",
    password="OXYLABS_PASSWORD",
)
result = tool.run(
    query="iPhone 16",
    parse=True,
    geo_location="Paris, France",
    user_agent_type="tablet"
)

print(result.results[0].content)
```
