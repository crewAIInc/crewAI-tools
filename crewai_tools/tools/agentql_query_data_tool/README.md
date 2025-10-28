# AgentQLQueryDataTool

## Description

[AgentQL](https://www.agentql.com/) is a tool that queries from any website using a structured query language.

## Installation

- Get an API key from [agentql.dev](https://dev.agentql.com/api-keys) and set it in environment variables (`AGENTQL_API_KEY`).
- Install the [AgentQL SDK](https://docs.agentql.com/python-sdk/installation) along with `crewai[tools]` package:

```
pip install 'crewai[tools]'
```

## Example

Utilize the AgentQLQueryDataTool as follows to allow your agent to query websites:

```python
from crewai_tools import AgentQLQueryDataTool

QUERY = """
{
  products[] {
    product_name
    price
  }
}
"""

tool = AgentQLQueryDataTool(url='https://scrapeme.live/?s=fish&post_type=product', query=QUERY)

## Arguments

- `url`: The base URL to extract data from.
- `query`: Optional. The query to use for the AgentQL to extract data from the url.
- `prompt`: Optional. A natural language description of the data you want to scrape.
```
