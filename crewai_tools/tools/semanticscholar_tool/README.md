# CrewAI Scholar Research Tools

This repository contains two custom tools for CrewAI: `ScholarResearchTool` and `ScholarStatusTool`. These tools utilize the LangChain framework and Semantic Scholar API to assist researchers in finding and summarizing important academic papers by a specific researcher on a given subject.

## About Semantic Scholar

Semantic Scholar provides free, AI-driven search and discovery tools, and open resources for the global research community. Indexing over 200 million academic papers from publisher partnerships, data providers, and web crawls, Semantic Scholar accelerates scientific breakthroughs using AI. Developed by the Allen Institute for AI, the platform offers tools that help researchers stay up-to-date with scientific literature by extracting meaning and identifying connections within papers. With a mission to promote equal access to science, Semantic Scholar values creative AI application, collaboration, bold measures, early learning, and trustworthiness. Resources such as the Semantic Scholar Academic Graph (S2AG) and the Semantic Scholar Open Research Corpus (S2ORC) provide datasets and APIs for developers to accelerate scientific progress. Launched in 2015 and founded by Paul Allen, Semantic Scholar contributes to humanity through high-impact AI research and engineering. Learn more at [Allen Institute for AI](https://allenai.org/) and [Semantic Scholar](https://www.semanticscholar.org/).

## Table of Contents

1. [Overview](#overview)
2. [Usage](#usage)
3. [Example](#example)

## Overview

### ScholarResearchTool

`ScholarResearchTool` is designed to find and summarize important papers by a specific researcher on a given subject. It provides a list of papers authored by the researcher, summaries of the most important papers, and a paragraph in markdown format summarizing the researcher's work in the field with references to relevant papers.

### ScholarStatusTool

`ScholarStatusTool` helps to determine the last time a specific researcher published a paper on a given subject. It returns a summary sentence about the researcher's most recent work in the field along with a link to the most recent paper.

## Usage

To use these tools in CrewAI, you need to integrate them into your CrewAI environment. Below is an example of how to create agents and tasks using these tools.

### Example

```python
import os
from crewai import Agent, Task, Crew, Process
from ScholarResearchTool import ScholarResearchTool
from ScholarStatusTool import ScholarStatusTool

# Set your OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"

# Initialize tools
research_tool = ScholarResearchTool()
status_tool = ScholarStatusTool()

# Create agents
researcher_agent = Agent(
    role='Researcher',
    goal='Find and summarize important papers by a specific researcher on a given subject.',
    verbose=True,
    memory=True,
    tools=[research_tool]
)

status_agent = Agent(
    role='Researcher',
    goal='Determine the last time a specific researcher published on a given subject.',
    verbose=True,
    memory=True,
    tools=[status_tool]
)

# Define tasks
research_task = Task(
    description="Find and summarize important papers by {researcher} on {research_subject}.",
    expected_output='A summary of important papers with links, and a markdown formatted paragraph summarizing the work.',
    tools=[research_tool],
    agent=researcher_agent,
)

status_task = Task(
    description="Determine the last time {researcher} published a paper on {research_subject}.",
    expected_output='A summary sentence with a link to the most recent paper.',
    tools=[status_tool],
    agent=status_agent,
)

# Form the crew
crew = Crew(
    agents=[researcher_agent, status_agent],
    tasks=[research_task, status_task],
    process=Process.sequential
)

# Kickoff the crew
result = crew.kickoff(inputs={'researcher': 'Albert Einstein', 'research_subject': 'Electrodynamics of Moving Bodie'})
print(result)
```
