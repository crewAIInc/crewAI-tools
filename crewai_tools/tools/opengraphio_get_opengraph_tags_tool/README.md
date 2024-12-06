# OpenGraphIOGetOpenGraphTagsTool

## Description

The `OpenGraphIOGetOpenGraphTagsTool` is a tool for retrieving OpenGraph tags from websites using the OpenGraph.io API. 
It extracts key OpenGraph metadata, such as titles, descriptions, and images from webpages, allowing users to gather 
insights about any given URL.  In addition to the tags found on the site, the Opengraph.io API will infer values
that may be missing from the page.

## Installation

To use the `OpenGraphIOGetOpenGraphTagsTool`, you need to install the `crewai[tools]` package:

```sh
pip install crewai[tools]
```

## Example

```python
# To run the example, you will need to make sure you have your API keys set.
# 1. create a free account on https://opengraph.io/
# 2. set the OPENGRAPHIO_API_KEY environment variable to your API key
# 3. run the example

from crewai_tools.tools.opengraphio_get_opengraph_tags_tool.opengraphio_get_opengraph_tags_tool import GetOpengraphTagsTool
from crewai import Agent, Task, Crew

# Create an instance of the OpenGraphTool
opengraph_tags_tool = GetOpengraphTagsTool()

# Create the agent with the OpenGraphTool
opengraph_specialist = Agent(
    role="Open Graph Metadata Specialist",
    goal="Suggest most relevant Open Graph metadata tags for a website",
    backstory="A skilled SEO / SEM consultant with 20 years of experience.",
    tools=[opengraph_tags_tool],
    verbose=True,
    cache=False
)

# Define the tasks for the agent
suggest_opengraph_tags = Task(
    description="Review the OpenGraph metadata and the tags suggested from the Opengraph.io API for "
                "https://www.wunderground.com/ and suggest the most relevant Open Graph metadata tags.  "
                "The Opengraph.io API will return the following important properties:"
                "- hybridGraph - The tags that the Opengraph.io API suggests for the page"
                "- openGraph - The tags that are currently on the page",
    expected_output="Provide the tags that are currently on the page ('openGraph' property) and suggest HTML to be "
                    "inserted into the <HEAD> tag to provide more effective tags for sharing on social websites. "
                    "The response should look like this:"
                    "## Current Tags"
                    "You're assessment of the current tags"
                    "## Suggested Tags"
                    "You're suggested HTML content to add to the <HEAD> tag"
                    "### Explanation"
                    "Explain why you suggest these tags",
    agent=opengraph_specialist
)


# Create a crew with the agent and tasks
crew = Crew(
    agents=[opengraph_specialist],
    tasks=[
        suggest_opengraph_tags
    ],
    verbose=True
)

# Kick off the crew to execute the tasks
crew.kickoff()

```
### Output
```bash
# Agent: Open Graph Metadata Specialist
## Final Answer: 
## Current Tags  
The current Open Graph tags were not found on the page; however, there are inferred tags based on the content extracted:  
- Title: Local Weather Forecast, News and Conditions | Weather Underground  
- Description: Weather Underground provides local & long-range weather forecasts, weather reports, maps & tropical weather conditions for locations worldwide  
- Type: site  
- URL: https://www.wunderground.com/  
- Site Name: Local Weather Forecast, News and Conditions  
- Image: https://www.wunderground.com/static/i/misc/twc-white.svg  

## Suggested Tags  
To enhance social sharing, I suggest adding the following HTML content to the `<HEAD>` tag:  
\`\`\`html
<meta property="og:title" content="Local Weather Forecast, News and Conditions | Weather Underground" />  
<meta property="og:description" content="Weather Underground provides local & long-range weather forecasts, weather reports, maps & tropical weather conditions for locations worldwide" />  
<meta property="og:type" content="website" />  
<meta property="og:url" content="https://www.wunderground.com/" />  
<meta property="og:site_name" content="Weather Underground" />  
<meta property="og:image" content="https://www.wunderground.com/static/i/misc/twc-white.svg" />  
<meta property="og:image:alt" content="Weather Underground Logo" />  
\`\`\`

### Explanation  
I suggest these tags because they provide essential metadata for social platforms to display rich previews when the link to Weather Underground is shared. Including a specific image (`og:image`) enhances the visual appeal, while a clear and concise title and description (`og:title` and `og:description`) can help engage users and improve click-through rates. These elements ensure that the page is represented accurately and attractively on social media, which is crucial for driving traffic and improving user engagement.

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
To use the OpenGraph.io API, you need to create a free account on [https://opengraph.io](https://opengraph.io) and set 
the OPENGRAPHIO_API_KEY environment variable to your API key.

