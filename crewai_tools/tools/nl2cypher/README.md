# NL2Cypher Tool

## Description

This tool is used to convert natural language into Cypher queries for Neo4j. When integrated into an agent, it enables the generation of Cypher queries to interact with a Neo4j database.

This facilitates various workflows, such as enabling an agent to retrieve graph data based on a given goal and use that information to generate responses, reports, or other outputs. Additionally, it allows the agent to update the database as needed.

**Attention**: Ensure that the agent has appropriate permissions and that the operations it performs align with the intended database usage.

## Requirements

- Neo4j Python Driver (`neo4j`)
- `neo4j_graphrag` for schema extraction and sanitization

## Installation

Install the required package:
```shell
pip install 'crewai[tools]'
```

## Usage

To use the NL2CypherTool, you need to provide the Neo4j connection parameters, including the URI, username, password, and database name.

```python
from crewai_tools import NL2CypherTool

nl2cypher = NL2CypherTool(
    uri="neo4j://localhost:7687",
    username="neo4j",
    password="password",
    database="neo4j"
)

@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config["researcher"],
        allow_delegation=False,
        tools=[nl2cypher]
    )
```

## Example


## Workflow

This tool enables dynamic interactions between agents and the Neo4j database, supporting iterative query refinement and data-driven decision-making.

```
DB -> Agent -> ... -> Agent -> DB
```