# OlostepGoogleSearchTool

## Description

The `OlostepGoogleSearchTool` allows you to perform a Google search using the Olostep API and receive structured JSON results.

## Installation

- Get an API key from [olostep.com](https://olostep.com) and set it in your environment variables as `OLOSTEP_API_KEY`.
- Install the `requests` package if you don't have it already:

```shell
pip install requests
```

## Example

Here's how to use the `OlostepGoogleSearchTool` to perform a Google search:

```python
from crewai_tools import OlostepGoogleSearchTool

# Initialize the tool
tool = OlostepGoogleSearchTool()

# Perform a search
results = tool.run(search_query="latest news on AI")
print(results)

# Perform a search with different location and language
results_localized = tool.run(search_query="best restaurants near me", location="fr", language="fr")
print(results_localized)
```

## Arguments

- `search_query` (str): The search query for Google.
- `location` (Optional[str]): The country to search from. It must be a two-letter country code (ISO 3166-1 alpha-2). Defaults to `"us"`.
- `language` (Optional[str]): The language for the search. It must be a two-letter language code (ISO 639-1). Defaults to `"en"`.
