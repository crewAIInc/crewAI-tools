# Cognee Tools

## Description

These tools enable integration with [cognee](https://github.com/topoteretes/cognee), an AI memory library. With Cognee Tools, you can:

- Add text to the knowledge base
- Cognify the knowledge graph (process and structure the added information)
- Search for insights in the knowledge graph
- Prune the knowledge graph when needed

Cognee allows your agents to build and maintain a knowledge graph from text inputs, enabling more sophisticated reasoning and information retrieval.

## Installation

```bash
uv pip install 'crewai[tools] cognee'
```

### CrewAI Integration Example

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool
from crewai_tools import CogneeAddTool, CogneeCognifyTool, CogneeSearchTool, CogneePruneTool
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class ResearchMemoryCrew:
    """A crew that researches topics and builds a knowledge graph"""
    
    # Initialize tools
    search_tool = SerperDevTool()
    web_tool = WebsiteSearchTool()
    
    # Cognee memory tools
    cognee_add = CogneeAddTool()
    cognee_cognify = CogneeCognifyTool()
    cognee_search = CogneeSearchTool()
    cognee_prune = CogneePruneTool()
    
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config={
                "role": "Research Specialist",
                "goal": "Find and collect information on specific topics",
                "backstory": "You are an expert researcher who gathers information and stores it in a knowledge graph."
            },
            tools=[self.search_tool, self.web_tool, self.cognee_add]
        )
    
    @agent
    def knowledge_manager(self) -> Agent:
        return Agent(
            config={
                "role": "Knowledge Manager",
                "goal": "Process and organize information in the knowledge graph",
                "backstory": "You transform raw information into structured knowledge and extract insights."
            },
            tools=[self.cognee_cognify, self.cognee_search, self.cognee_prune]
        )
    
    @task
    def gather_information(self) -> Task:
        return Task(
            description="Research the given topic and add findings to the knowledge graph",
            expected_output="Confirmation that information has been added to Cognee",
            agent=self.researcher()
        )
    
    @task
    def process_knowledge(self) -> Task:
        return Task(
            description="Process the collected information and build the knowledge graph",
            expected_output="Confirmation that the knowledge graph has been built",
            agent=self.knowledge_manager()
        )
    
    @task
    def extract_insights(self) -> Task:
        return Task(
            description="Search the knowledge graph to extract insights on the topic",
            expected_output="A summary of insights extracted from the knowledge graph",
            agent=self.knowledge_manager()
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

def run():
    """Run the research memory crew"""
    topic = "artificial intelligence trends in 2024"
    
    crew_instance = ResearchMemoryCrew().crew()
    results = crew_instance.kickoff(
        inputs={
            "topic": topic,
            "search_depth": "comprehensive"
        }
    )
    
    print(f"Research results for '{topic}':")
    print(results)

if __name__ == "__main__":
    run()

```

## Available Query Types

When using the `CogneeSearchTool`, you can specify different query types:

- `INSIGHTS` (default)
- `SUMMARIES`
- `CHUNKS`
- `COMPLETION`
- `GRAPH_COMPLETION`
- `GRAPH_SUMMARY_COMPLETION`

Visit [cognee's repo](https://github.com/topoteretes/cognee) for details. 
## Note on Automatic Installation

The Cognee tools will attempt to automatically install the `cognee` package if it's not already installed.
