# SteelScrapeWebsiteTool

## Description

[Steel](https://steel.dev) is an open-source browser API that makes it easy to build AI apps and agents that interact with the web. Instead of building automation infrastructure from scratch, you can focus on your AI application while Steel handles the complexity.

## Installation

- Get an API key from [steel.dev](https://app.steel.dev) and set it in environment variables (`STEEL_API_KEY`).
- Install the [Steel SDK](https://github.com/steel-dev/steel-python) along with `crewai[tools]`:

```bash
pip install steel-sdk 'crewai[tools]'
```

## Example

U the SteelScrapeWebsiteTool as follows to allow your agent to load websites:

```python
from crewai_tools import SteelScrapeWebsiteTool

tool = SteelScrapeWebsiteTool(formats=["markdown"], proxy=True)
```

## Arguments

- `api_key` Optional. Steel API key. Default is `STEEL_API_KEY` env variable.
- `formats` Optional[List[str]]. Content formats to return. Default: `["markdown"]`.
- `proxy` Optional. Enable/Disable proxies.
