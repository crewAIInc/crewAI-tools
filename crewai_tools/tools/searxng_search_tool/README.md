# SearxNG Search Tool

## Description

The SearxNGSearchTool is a powerful tool that allows you to perform web searches using a SearxNG instance. SearxNG is a free and open-source metasearch engine that respects user privacy. This tool provides an easy way to integrate SearxNG search capabilities into your crewAI projects.

## Installation

The SearxNGSearchTool is included in the crewAI-tools package. To use it, make sure you have crewAI-tools installed:

```bash
pip install crewai-tools
```

## Example Usage

Here's an example of how to use the SearxNGSearchTool:

```python
from crewai_tools import SearxNGSearchTool

# Initialize the tool with the base URL of your SearxNG instance
searxng_tool = SearxNGSearchTool(base_url="http://localhost:8080/search")

# Perform a search
results = searxng_tool.run(query="crewAI", num_results=5)
print(results)
```

## Arguments

- `base_url` (str): The base URL of the SearxNG instance to use for searches.
- `query` (str): The search query to be executed.
- `num_results` (int, optional): Number of results to return (default: 10).

## Custom Model and Embeddings

The SearxNGSearchTool does not require any custom models or embeddings. It relies on the SearxNG instance to perform the web search and return results.
