# OlostepWebScraperTool

## Description

The `OlostepWebScraperTool` allows you to scrape web pages using the Olostep API and receive the content in either markdown or HTML format.

## Installation

- Get an API key from [olostep.com](https://olostep.com) and set it in your environment variables as `OLOSTEP_API_KEY`.
- Install the `requests` package if you don't have it already:

```shell
pip install requests
```

## Example

Here's how to use the `OlostepWebScraperTool` to scrape a website:

```python
from crewai_tools import OlostepWebScraperTool

# Initialize the tool
tool = OlostepWebScraperTool()

# Scrape a URL and get the content in markdown (default)
result_md = tool.run(url_to_scrape="https://www.example.com")
print(result_md)

# Scrape a URL and get the content in both HTML and markdown
result_both = tool.run(url_to_scrape="https://www.example.com", formats=["html", "markdown"])
print(result_both)
```

## Arguments

- `url_to_scrape` (str): The URL of the webpage to scrape.
- `formats` (Optional[List[str]]): A list of formats to return. Can be `["markdown"]`, `["html"]`, or `["markdown", "html"]`. Defaults to `["markdown"]`.
