"""
StagehandTool Example

This example demonstrates how to use the StagehandTool in a CrewAI workflow.
It uses a web researcher agent to search for information on a given topic.

Prerequisites:
1. A Browserbase account with API key and project ID
2. An Anthropic API key (or OpenAI API key)
3. Installed dependencies: crewai, crewai-tools, stagehand-py

Usage:
- Set your API keys in environment variables (recommended)
- Or modify the script to include your API keys directly
- Run the script: python stagehand_example.py
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import StagehandTool

# Get API keys from environment variables
# You can set these in your shell or in a .env file
browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID") 
model_api_key = os.environ.get("ANTHROPIC_API_KEY")  # or OPENAI_API_KEY

# Initialize the StagehandTool with your credentials
stagehand_tool = StagehandTool(
    browserbase_api_key=browserbase_api_key,
    browserbase_project_id=browserbase_project_id,
    model_api_key=model_api_key,
    model_name="gpt-4o",
    # Optional: customize the model
    # model_name="anthropic/claude-3-haiku-20240307"  # Default is claude-3-opus
)

# Create a web researcher agent with the StagehandTool
researcher = Agent(
    role="Web Researcher",
    goal="Find accurate and detailed information on specific topics by browsing the web",
    backstory=(
        "You are an expert at navigating websites and extracting valuable information. "
        "You're thorough, precise, and have a knack for finding exactly what the user needs."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[stagehand_tool],
)

# Define a research task
research_task = Task(
    description=(
        "Research the latest developments in AI and browser automation. "
        "1. Go to https://stagehand.dev and read about the tool "
        "2. Then search on Google for 'browser automation with AI' "
        "3. Find and visit at least 2 relevant websites "
        "4. Summarize your findings in a brief report focused on how AI is being used for browser automation"
    ),
    expected_output=(
        "A summary report on AI browser automation technologies, their capabilities, "
        "and practical applications based on the websites visited."
    ),
    agent=researcher
)

# Set up the crew
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True,
    process=Process.sequential  # Run tasks sequentially
)

# Run the crew and get the result
result = crew.kickoff()

print("\n==== RESEARCH RESULTS ====\n")
print(result)

# Make sure to clean up stagehand resources
stagehand_tool.close() 