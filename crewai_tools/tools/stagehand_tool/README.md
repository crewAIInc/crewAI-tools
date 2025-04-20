# Stagehand Web Automation Tool

This tool integrates the [Stagehand](https://docs.stagehand.dev/) framework with CrewAI, allowing agents to interact with websites and automate browser tasks using natural language instructions.

## Description

Stagehand is a powerful browser automation framework built by Browserbase that allows AI agents to:

- Navigate to websites
- Click buttons, links, and other elements
- Fill in forms
- Extract data from web pages
- Observe and identify elements
- Perform complex workflows

The StagehandTool wraps the Stagehand Python SDK to provide CrewAI agents with the ability to control a real web browser and interact with websites using three core primitives:

1. **Act**: Perform actions like clicking, typing, or navigating
2. **Extract**: Extract structured data from web pages
3. **Observe**: Identify and analyze elements on the page

## Requirements

Before using this tool, you'll need:

1. A [Browserbase](https://www.browserbase.io/) account with API key and project ID
2. An API key for an LLM (OpenAI or Anthropic Claude)
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
from stagehand.schemas import AvailableModel

# Initialize the tool with your API keys
stagehand_tool = StagehandTool(
    api_key="your-browserbase-api-key",
    project_id="your-browserbase-project-id",
    model_api_key="your-llm-api-key",  # OpenAI or Anthropic API key
    model_name=AvailableModel.CLAUDE_3_7_SONNET_LATEST,  # Optional: specify which model to use
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

### Using Different Primitives

The StagehandTool now supports three different command types:

#### 1. Act - Perform actions on a page

```python
# Perform an action (default behavior)
result = stagehand_tool.run(
    instruction="Click the login button", 
    url="https://example.com",
    command_type="act"  # Default, so can be omitted
)
```

#### 2. Extract - Extract data from a page

```python
# Extract data from a page
result = stagehand_tool.run(
    instruction="Extract all the product prices and names", 
    url="https://example.com/products",
    command_type="extract",
    selector=".product-container"  # Optional CSS selector to limit extraction scope
)
```

#### 3. Observe - Identify elements on a page

```python
# Observe elements on a page
result = stagehand_tool.run(
    instruction="Find all navigation menu items", 
    url="https://example.com",
    command_type="observe"
)
```

### Advanced Configuration

You can customize the behavior of the StagehandTool by specifying different parameters:

```python
stagehand_tool = StagehandTool(
    api_key="your-browserbase-api-key",
    project_id="your-browserbase-project-id",
    model_api_key="your-llm-api-key",
    model_name=AvailableModel.GPT_4O,
    server_url="https://api.stagehand.dev",  # Default is https://api.stagehand.dev
    headless=True,  # Run in headless mode
    dom_settle_timeout_ms=5000,  # Wait longer for DOM to settle
)
```

## Complete Example

Here's a complete example showing how to use all three primitives:

```python
from crewai import Agent, Task, Crew
from crewai_tools import StagehandTool
from stagehand.schemas import AvailableModel
import os

# Get API keys from environment
browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
model_api_key = os.environ.get("OPENAI_API_KEY")  # or ANTHROPIC_API_KEY

# Initialize the tool
stagehand_tool = StagehandTool(
    api_key=browserbase_api_key,
    project_id=browserbase_project_id,
    model_api_key=model_api_key,
    model_name=AvailableModel.GPT_4O,
)

# Create an agent
researcher = Agent(
    role="Web Researcher",
    goal="Gather product information from an e-commerce website",
    backstory="I specialize in extracting and analyzing web data.",
    verbose=True,
    tools=[stagehand_tool],
)

# Create a task
research_task = Task(
    description=(
        "Analyze an e-commerce website by:\n"
        "1. Go to example.com (command_type='act')\n"
        "2. Observe the main navigation elements (command_type='observe')\n"
        "3. Navigate to a product page\n"
        "4. Extract product details (command_type='extract')\n"
        "5. Provide a summary of the findings"
    ),
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

# Clean up resources
stagehand_tool.close()
```

## Advanced Tips

1. **Session Reuse**: You can reuse a browser session by saving the `_session_id` property and passing it to a new instance of StagehandTool.

2. **Error Handling**: The tool includes error handling that returns error messages as strings, making it resilient in agent workflows.

3. **Resource Cleanup**: Call the `close()` method when you're done with the tool to properly clean up browser resources.

4. **Chaining Operations**: The most effective workflows often chain the three primitives together:
   - First, *observe* to identify elements on the page
   - Then, *act* to interact with those elements
   - Finally, *extract* to gather structured data

## How It Works

Under the hood, StagehandTool:

1. Initializes a Stagehand session connected to a remote browser via Browserbase
2. Uses the appropriate primitive (act, extract, or observe) based on the command_type
3. Handles the asynchronous browser control in a way that's compatible with CrewAI's synchronous execution model

## Documentation

For more information about Stagehand, visit the [official documentation](https://docs.stagehand.dev/). 