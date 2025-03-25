<div align="center">

![Logo of crewAI, two people rowing on a boat](./assets/crewai_logo.png)

<div align="left">

# CrewAI Tools

Empower your CrewAI agents with powerful, customizable tools to elevate their capabilities and tackle sophisticated, real-world tasks.

CrewAI Tools provide the essential functionality to extend your agents, helping you rapidly enhance your automations with reliable, ready-to-use tools or custom-built solutions tailored precisely to your needs.

---

## Quick Links

[Homepage](https://www.crewai.com/) | [Documentation](https://docs.crewai.com/) | [Examples](https://github.com/crewAIInc/crewAI-examples) | [Community](https://community.crewai.com/)

---

## Available Tools

CrewAI provides an extensive collection of powerful tools ready to enhance your agents:

- **File Management**: `FileReadTool`, `FileWriteTool`
- **Web Scraping**: `ScrapeWebsiteTool`, `SeleniumScrapingTool`
- **Database Integrations**: `PGSearchTool`, `MySQLSearchTool`
- **API Integrations**: `SerperApiTool`, `EXASearchTool`
- **AI-powered Tools**: `DallETool`, `VisionTool`

And many more robust tools to simplify your agent integrations.

---

## Creating Custom Tools

CrewAI offers two straightforward approaches to creating custom tools:

### Subclassing `BaseTool`

Define your tool by subclassing:

```python
from crewai.tools import BaseTool

class MyCustomTool(BaseTool):
    name: str = "Tool Name"
    description: str = "Detailed description here."

    def _run(self, *args, **kwargs):
        # Your tool logic here
```

### Using the `tool` Decorator

Quickly create lightweight tools using decorators:

```python
from crewai import tool

@tool("Tool Name")
def my_custom_function(input):
    # Tool logic here
    return output
```

---

## Why Use CrewAI Tools?

- **Simplicity & Flexibility**: Easy-to-use yet powerful enough for complex workflows.
- **Rapid Integration**: Seamlessly incorporate external services, APIs, and databases.
- **Enterprise Ready**: Built for stability, performance, and consistent results.

---

### Structured Tools

The `StructuredTool` class wraps functions as tools, providing flexibility and validation while reducing boilerplate. It supports custom schemas and dynamic logic for seamless integration of complex functionalities.

#### Example:
Using `StructuredTool.from_function`, you can wrap a function that interacts with an external API or system, providing a structured interface. This enables robust validation and consistent execution, making it easier to integrate complex functionalities into your applications as demonstrated in the following example:

```python
from langchain.tools.base import StructuredTool
from pydantic import BaseModel

# Define the schema for the tool's input using Pydantic
class APICallInput(BaseModel):
    endpoint: str
    parameters: dict

# Wrapper function to execute the API call
def tool_wrapper(*args, **kwargs):
    # Here, you would typically call the API using the parameters
    # For demonstration, we'll return a placeholder string
    return f"Call the API at {kwargs['endpoint']} with parameters {kwargs['parameters']}"

# Create and return the structured tool
def create_structured_tool():
    return StructuredTool.from_function(
        func=tool_wrapper,
        name='Wrapper API',
        description="A tool to wrap API calls with structured input.",
        args_schema=APICallInput
    )

# Example usage
structured_tool = create_structured_tool()

# Execute the tool with structured input
result = structured_tool.run({
    "endpoint": "https://example.com/api",
    "parameters": {"key1": "value1", "key2": "value2"}
})
print(result)  # Output: Call the API at https://example.com/api with parameters {'key1': 'value1', 'key2': 'value2'}
```

## Contribution Guidelines

We welcome contributions from the community!

1. Fork and clone the repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m 'Add my feature'`).
4. Push your branch (`git push origin feature/my-feature`).
5. Open a pull request.

---

## Developer Quickstart

```shell
pip install crewai[tools]
```

### Development Setup

- Install dependencies: `uv sync`
- Run tests: `uv run pytest`
- Run static type checking: `uv run pyright`
- Set up pre-commit hooks: `pre-commit install`

---

## Support and Community

Join our rapidly growing community and receive real-time support:

- [Discourse](https://community.crewai.com/)
- [Open an Issue](https://github.com/crewAIInc/crewAI/issues)

Build smarter, faster, and more powerful AI solutions—powered by CrewAI Tools.

