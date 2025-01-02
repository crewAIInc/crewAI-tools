"""Example usage of MultiOnTool with secure API key handling."""

from crewai import Agent, Crew, Task
from multion_tool import MultiOnTool

# Make sure to set these environment variables before running:
# export OPENAI_API_KEY=your_openai_key
# export MULTION_API_KEY=your_multion_key


# Initialize the tool - it will automatically use MULTION_API_KEY from environment
multion_browse_tool = MultiOnTool()

# Create a new agent
Browser = Agent(
    role="Browser Agent",
    goal="control web browsers using natural language ",
    backstory="An expert browsing agent.",
    tools=[multion_browse_tool],
    verbose=True,
)

# Define tasks
browse = Task(
    description="Summarize the top 3 trending AI News headlines",
    expected_output="A summary of the top 3 trending AI News headlines",
    agent=Browser,
)


crew = Crew(agents=[Browser], tasks=[browse])

crew.kickoff()
