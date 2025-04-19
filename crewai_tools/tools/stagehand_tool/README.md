# Stagehand Web Automation Tool

This tool integrates the [Stagehand](https://docs.stagehand.dev/) framework with CrewAI, allowing agents to interact with websites and automate browser tasks using natural language instructions.

## Description

Stagehand is a powerful browser automation framework built by Browserbase that allows AI agents to:

- Navigate to websites
- Click buttons, links, and other elements
- Fill in forms
- Extract data from web pages
- Perform complex workflows

The StagehandTool wraps the Stagehand Python SDK to provide CrewAI agents with the ability to control a real web browser and interact with websites using natural language commands.

## Requirements

Before using this tool, you'll need:

1. A [Browserbase](https://www.browserbase.io/) account with API key and project ID
2. An API key for an LLM (Anthropic Claude or OpenAI)
3. The Stagehand Python SDK installed

Install the dependencies:

```bash
pip install stagehand-py
```

## Usage

### Basic Usage

```python
from crewai import Agent, Task, Crew
from crewai_tools import StagehandTool

# Initialize the tool with your API keys
stagehand_tool = StagehandTool(
    browserbase_api_key="your-browserbase-api-key",
    browserbase_project_id="your-browserbase-project-id",
    model_api_key="your-llm-api-key",  # Anthropic or OpenAI API key
)

# Create an agent with the tool
researcher = Agent(
    role="Web Researcher",
    goal="Find and summarize information from websites",
    backstory="I'm an expert at finding information online.",
    verbose=True,
    tools=[stagehand_tool],
)

# Create a task that uses the tool
research_task = Task(
    description="Go to https://www.example.com and tell me what you see on the homepage.",
    agent=researcher,
)

# Run the crew
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
)

result = crew.kickoff()
print(result)
```

### Advanced Usage

You can customize the behavior of the StagehandTool by specifying different parameters:

```python
stagehand_tool = StagehandTool(
    browserbase_api_key="your-browserbase-api-key",
    browserbase_project_id="your-browserbase-project-id",
    model_api_key="your-llm-api-key",
    model_name="anthropic/claude-3-haiku-20240307",  # Choose a different model
    server_url="https://api.stagehand.dev",  # Default is https://api.stagehand.dev
)
```

## Example

Here's an example of using StagehandTool to search for information on Google:

```python
from crewai import Agent, Task, Crew
from crewai_tools import StagehandTool
import os

# Get API keys from environment
browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
model_api_key = os.environ.get("ANTHROPIC_API_KEY")  # or OPENAI_API_KEY

# Initialize the tool
stagehand_tool = StagehandTool(
    browserbase_api_key=browserbase_api_key,
    browserbase_project_id=browserbase_project_id,
    model_api_key=model_api_key,
)

# Create an agent
researcher = Agent(
    role="Web Researcher",
    goal="Search for information on the web",
    backstory="I specialize in finding information online.",
    verbose=True,
    tools=[stagehand_tool],
)

# Create a task
search_task = Task(
    description=(
        "Go to Google.com, search for 'latest AI developments', and summarize "
        "the top 3 results. Visit each result page to get more detailed information."
    ),
    agent=researcher,
)

# Run the crew
crew = Crew(
    agents=[researcher],
    tasks=[search_task],
    verbose=True,
)

result = crew.kickoff()
print(result)
```

## Advanced Tips

1. **Session Reuse**: You can reuse a browser session by saving the `_session_id` property and passing it to a new instance of StagehandTool.

2. **Error Handling**: The tool includes error handling that returns error messages as strings, making it resilient in agent workflows.

3. **Resource Cleanup**: Call the `close()` method when you're done with the tool to properly clean up browser resources.

## How It Works

Under the hood, StagehandTool:

1. Initializes a Stagehand session connected to a remote browser via Browserbase
2. Executes natural language instructions using the Stagehand agent
3. Handles the asynchronous browser control in a way that's compatible with CrewAI's synchronous execution model

## Documentation

For more information about Stagehand, visit the [official documentation](https://docs.stagehand.dev/). 