# DesearchTool Documentation

## Description

This tool provides a real-time AI-powered search experience, utilizing the https://desearch.ai/ API to deliver the most relevant results for your query. It seamlessly scans the internet, delivering accurate, up-to-date information by understanding the semantic context of your request.

## Installation

To incorporate this tool into your project, follow the installation instructions below:

```shell
uv add crewai[tools] desearch_py
```

## Example

The following example demonstrates how to initialize the tool and execute a search with a given query:

```python
from crewai_tools import DesearchTool

# Initialize the tool for internet searching capabilities
tool = DesearchTool(api_key="your_api_key")
```

## Steps to Get Started

To effectively use the `DesearchTool`, follow these steps:

1. **Package Installation**: Confirm that the `crewai[tools]` package is installed in your Python environment.
2. **API Key Acquisition**: Acquire a `https://desearch.ai/` API key by registering for a free account at `https://desearch.ai/`.
3. **Environment Configuration**: Store your obtained API key in an environment variable named `DESEARCH_API_KEY` to facilitate its use by the tool.

## Conclusion

By integrating the `DesearchTool` into Python projects, users gain the ability to conduct real-time, relevant searches across the internet directly from their applications. By adhering to the setup and usage guidelines provided, incorporating this tool into projects is streamlined and straightforward.
