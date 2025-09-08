# YouSearchTool (You.com Search API)

Simple wrapper for the You.com Search API that returns structured web/news results with snippets and URLs.

Docs:
- Search API (Trusted, Recent info): https://documentation.you.com/api-modes/search-api#trustworthy-and-recent-informantion-for-your-research
- Quickstart (Search API): https://documentation.you.com/docs/quickstart#search-api

## What it's for

Use when you need accurate, up-to-date web snippets and URLs from trusted sources to ground agent answers without extra scraping. Results include long snippets, titles, and links suitable for direct LLM consumption.

## Environment

- YOU_API_KEY (required) — used as `X-API-Key`

## Usage (published)

```python
from crewai_tools import YouSearchTool

you = YouSearchTool()
resp = you.run(query="result of the political debate in EU")
print(resp)  # JSON string containing results.web/news arrays
```

## Example with agents

Here’s a minimal CrewAI agent that uses `YouSearchTool` as a tool. The agent will invoke the tool directly (no manual `run(...)` calls).

```python
import os
from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import YouSearchTool

# LLM (configure your provider keys, e.g., GEMINI_API_KEY or OPENAI_API_KEY)
llm = LLM(
  model="gemini/gemini-2.0-flash",
  temperature=0.5,
  api_key=os.getenv("GEMINI_API_KEY")
)

# You.com Web Search Tool
you = YouSearchTool()

# User query
query = "all the recent CrewAI news"

researcher = Agent(
  role="Senior Web Researcher",
  backstory="You are an expert web researcher.",
  goal="Find cited, high-quality sources and provide a detailed answer.",
  tools=[you],
  llm=llm,
  verbose=True,
)

# Research task
task = Task(
  description="""Use the You.com Web Search tool to research: {query}.
  Provide the answer in detail and cite sources (sources should be in the format of [source](url)).""",
  expected_output="A detailed, sourced answer to the question.",
  agent=researcher,
  output_file="answer.md",
)

# Crew
crew = Crew(
  agents=[researcher],
  tasks=[task],
  verbose=True,
  process=Process.sequential,
)

# Kickoff the crew
result = crew.kickoff(inputs={'query': query})
print(result)
```

## Notes

- Endpoint: `GET https://api.ydc-index.io/v1/search` with headers `{ "X-API-Key": YOU_API_KEY }` and params `{ query: ... }`
- Returns results grouped by sections (e.g., `results.web`, `results.news`) with URLs, titles, descriptions, and snippets.


