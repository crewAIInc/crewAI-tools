# ValyuContextTool Documentation

## Description

This tool enables semantic search across both proprietary and web content using the `https://valyu.network/` API. It allows users to search through programmatically licensed proprietary data from the [Valyu Exchange](https://exchange.valyu.network/) and web content, returning relevant results based on the provided query.

## Installation

Install the required packages using:

```shell
uv add crewai[tools] valyu
```

## Example

Here's how to initialize and use the ValyuContextTool:

```python
from crewai_tools import ValyuContextTool

# Initialize the tool
tool = ValyuContextTool(api_key="your_api_key")
```

## Steps to Get Started

Follow these steps to use the ValyuContextTool:

1. **Package Installation**: Install the `crewai[tools]` and `valyu` packages in your Python environment.
2. **API Key**: Get your API key by signing up at `https://exchange.valyu.network/`.
3. **Environment Setup**: Store your API key in an environment variable named `VALYU_API_KEY`

## Advanced Configuration

You can customize the parameters for the `ValyuContextTool`:

- `query`: The search term or phrase
- `search_type`: Type of search ("proprietary", "web", or "both")
- `data_sources`: Specific indexes to query from
- `num_query`: Number of query variations (default: 10)
- `num_results`: Maximum results to return (default: 10)
- `max_price`: Maximum price per content in PCM

Example:

```python
from crewai import Agent, Task, Crew

# Define the agent
research_agent = Agent(
    role="Research Analyst",
    goal="Find detailed information using Valyu's proprietary and web sources",
    backstory="An expert researcher specializing in comprehensive data analysis",
    tools=[valyu_tool],
    verbose=True
)

# Define the task
search_task = Task(
    expected_output="Detailed analysis of quantum computing advancements",
    description="Research recent breakthroughs in quantum computing",
    agent=research_agent
)

# Create and run the crew
crew = Crew(
    agents=[research_agent],
    tasks=[search_task]
)

result = crew.kickoff()
print(result)

# Direct tool usage example
response = valyu_tool._run(
    query="quantum computing breakthroughs 2024",
    search_type="both",
    num_query=10,
    num_results=10,
    max_price=100
)
```
