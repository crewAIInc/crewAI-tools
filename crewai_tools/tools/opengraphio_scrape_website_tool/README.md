# OpenGraphIOScrapeWebsiteTool

## Description

The `OpenGraphIOScrapeWebsiteTool` (https://opengraph.io) is a tool for scraping the full content from a URL using the 
OpenGraph.io API. The API will automatically leverage proxies as needed and return the full contents of the page for 
your agent to interact with.

## Installation

To use the `OpenGraphIOScrapeWebsiteTool`, you need to install the `crewai[tools]` package:

## Example

```python
# To run the example, you will need to make sure you have your API keys set.
# 1. create a free account on https://opengraph.io/ 
# 2. set the OPENGRAPHIO_API_KEY environment variable to your API key
# 3. run the example

# Create a new agent
from crewai_tools.tools.opengraphio_scrape_website_tool.opengraphio_scrape_website_tool import OpenGraphScrapeWebsiteTool
from crewai import Agent, Task, Crew

# Create an instance of the OpenGraphTool
scrape_website = OpenGraphScrapeWebsiteTool()

# Create the agent with the OpenGraphTool
scraper_agent = Agent(
    role="Web Scraping Specialist",
    goal="Extract Summarize Website Content",
    backstory="A skilled data miner proficient in scraping raw HTML content and extracting useful information.",
    tools=[scrape_website],
    verbose=True,
    cache=False
)

# Define the tasks for the agent
summarize_site = Task(
    description="Scrape the OpenGraph metadata of https://securecoders.com and return a summary of its content",
    expected_output="A 1-2 sentence summary of the site that would be useful for someone interested in the site.",
    agent=scraper_agent
)


# Create a crew with the agent and tasks
crew = Crew(
    agents=[scraper_agent],
    tasks=[
        summarize_site
    ],
    verbose=True
)

# Kick off the crew to execute the tasks
crew.kickoff()
```
### Output
```bash

# Agent: Web Scraping Specialist
## Final Answer: 
SecureCoders is a security consulting firm that provides penetration testing and a range of cybersecurity services, aimed at helping startups and Fortune 100 companies improve their digital security posture. Their offerings include comprehensive security assessments, continuous threat exposure management, and custom software development services to protect vulnerable systems.


```

## Arguments
- `url` (string): The webpage URL to scrape.
- `full_render` (bool, optional): Whether to fully render the page before extracting metadata.
- `max_cache_age` (int, optional): The maximum cache age in milliseconds.
- `use_proxy` (bool, optional): Whether to use a proxy for scraping.
- `use_premium` (bool, optional): Whether to use the Premium Proxy feature.
- `use_superior` (bool, optional): Whether to use the Superior Proxy feature.
- `auto_proxy` (bool, optional): Whether to automatically use a proxy for domains that require one.
- `cache_ok` (bool, optional): Whether to allow cached responses.
- `accept_lang` (string, optional): The request language sent when requesting the URL.
- `ignore_scrape_failures` (bool, optional): Whether to ignore failures.

## API Key
To use the OpenGraph.io API, you need to create a free account on [https://opengraph.io](https://opengraph.io) and set the OPENGRAPHIO_API_KEY environment variable to your API key.
