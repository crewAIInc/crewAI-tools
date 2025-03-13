# Linkup Search Tool

## Description

This tool is designed to get contextual information from the web. It utilizes the `https://www.linkup.so/` API to fetch web content relevant to the query provided by the user.

## Installation

- Get an API key from [Linkup](https://app.linkup.so).
- Install the [Linkup SDK](https://github.com/LinkupPlatform/linkup-python-sdk) along with `crewai[tools]` package:

```
uv add crewai[tools] linkup-sdk
```

## Usage

```python
from crewai_tools import LinkupSearchTool

tool = LinkupSearchTool(api_key="your_api_key", depth="deep")
```