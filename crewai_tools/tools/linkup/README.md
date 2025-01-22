# Linkup Search Tool

## Description

The `LinkupSearchTool` is a tool designed for integration with the CrewAI framework. It provides the ability to query the Linkup API for contextual information and retrieve structured results. This tool is ideal for enriching workflows with up-to-date and reliable information from Linkup.

---

## Features

- Perform API queries to the Linkup platform using customizable parameters (`query`, `depth`, `output_type`, `structured_output_schema`).

---

## Installation

### Prerequisites

- Linkup API Key

### Steps

1. ```shell
  pip install 'crewai[tools]'
  ```

---

## Usage

### Basic Example

Here is how to use the `LinkupSearchTool` in a CrewAI project:

1. **Import and Initialize**:
   ```python
   from tools.linkup_tools import LinkupSearchTool
   import os
   import json

    os.environ["LINKUP_API_KEY"] = "your_linkup_api_key"
    os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
    depth = "standard"  # or deep
    output_type = "sourcedAnswer"  # or searchResults or structured

    # If output_type = structured, define a structured schema
    structured_output_schema = {your schema}

    structured_output_schema_json = json.dumps(structured_output_schema)

    # Initialize the Linkup search tool

    linkup_tool = LinkupSearchTool(
        api_key=os.getenv("LINKUP_API_KEY"),
        depth=depth,
        output_type=output_type,
        structured_output_schema=structured_output_schema_json  # ONLY if output_type = structured
    )

   ```

2. **Set Up an Agent and Task**:
   ```python
    from crewai import Agent, Task, Crew

    # Create an agent
    researcher = Agent(
        role="Market Research Analyst",
        goal="Provide deep insights using Linkup for AI industry trends.",
        backstory="An experienced analyst skilled in using advanced tools for market insights.",
        tools=[linkup_tool],
        verbose=True, # change to False if you don't want to see execution logs
    )

    # Define a task
    research = Task(
        description="Research the latest trends in the AI industry using the Linkup tool and provide insights.",
        expected_output="A summary of the top 3 trends with context and relevance to the industry.",
        agent=researcher,
    )



    # Set up and execute the Crew
    crew = Crew(
        agents=[researcher],
        tasks=[research],
        verbose=True,
        planning=True, # or False if you don't want to see planning logs
    )
    crew.kickoff()

   ```
