"""
StagehandTool Example

This example demonstrates how to use the StagehandTool in a CrewAI workflow.
It shows how to use the three main primitives: act, extract, and observe.

Prerequisites:
1. A Browserbase account with API key and project ID
2. An LLM API key (OpenAI or Anthropic)
3. Installed dependencies: crewai, crewai-tools, stagehand-py

Usage:
- Set your API keys in environment variables (recommended)
- Or modify the script to include your API keys directly
- Run the script: python stagehand_example.py
"""

import os

from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv
from stagehand.schemas import AvailableModel

from crewai_tools import StagehandTool

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
# You can set these in your shell or in a .env file
browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
model_api_key = os.environ.get("ANTHROPIC_API_KEY")  # or OPENAI_API_KEY

# Initialize the StagehandTool with your credentials
stagehand_tool = StagehandTool(
    api_key=browserbase_api_key,  # New parameter naming
    project_id=browserbase_project_id,  # New parameter naming
    model_api_key=model_api_key,
    model_name=AvailableModel.GPT_4O,  # Using the enum from schemas
)

# Create a web researcher agent with the StagehandTool
researcher = Agent(
    role="Web Researcher",
    goal="Find and extract information from websites using different Stagehand primitives",
    backstory=(
        "You are an expert at navigating websites and extracting valuable information. "
        "You know when to use act, extract, or observe functions to get the best results."  # todo more backstory re stagehand
    ),
    verbose=True,
    allow_delegation=False,
    tools=[stagehand_tool],
)


# Define a research task that demonstrates all three primitives
research_task = Task(
    description=(
        "Demonstrate Stagehand capabilities by performing the following steps:\n"
        "1. Go to https://www.stagehand.dev\n"
        "2. Extract all the text content from the page\n"
        "3. Go to https://httpbin.org/forms/post and observe what elements are available on the page\n"
        "4. Fill out the form\n"
        "5. Provide a summary of what you learned about using these different commands"
    ),
    expected_output=(
        "A demonstration of all three Stagehand primitives (act, extract, observe) "
        "with examples of how each was used and what information was gathered."
    ),
    agent=researcher,
)

# Alternative task: Real research using the primitives
web_research_task = Task(
    description=(
        "Research AI in browser automation by:\n"
        "1. Go to https://browserbase.com.\n"
        "2. Observe navigation elements.\n"
        "3. Find the pricing page.\n"
        "4. Extract pricing information.\n"
        "5. Compile all information into a short summary report"
    ),
    expected_output=(
        "A summary report about Stagehand's capabilities and pricing, demonstrating how "
        "the different primitives can be used together for effective web research."
    ),
    agent=researcher,
)

# Set up the crew
crew = Crew(
    agents=[researcher],
    tasks=[web_research_task],  # You can switch this to web_research_task if you prefer
    verbose=True,
    process=Process.sequential,
)

# Run the crew and get the result
result = crew.kickoff()

print("\n==== RESULTS ====\n")
print(result)

# Make sure to clean up stagehand resources
stagehand_tool.close()
