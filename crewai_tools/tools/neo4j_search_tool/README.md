# Neo4jSearchTool

## Description
This tool is designed to facilitate semantic searches within Neo4j graph databases. Leveraging the RAG (Retrieve and Generate) technology, the Neo4jSearchTool provides users with an efficient means of querying Neo4j database content using Cypher queries. It enables semantic search capabilities over graph data, making it an invaluable resource for users needing to perform intelligent queries on graph databases containing nodes, relationships, and properties.

## Installation
To install the `crewai_tools` package with Neo4j support, execute the following command in your terminal:

```shell
pip install 'crewai[tools]'
```

Or install with the Neo4j extra for the latest dependencies:

```shell
pip install 'crewai-tools[neo4j]'
```

Or install the required dependencies manually:

```shell
pip install neo4j>=5.0.0
```

## Example
Below is an example showcasing how to use the Neo4jSearchTool to conduct a semantic search on a Neo4j database:

```python
from crewai_tools import Neo4jSearchTool

# Initialize the tool with Neo4j connection details
tool = Neo4jSearchTool(
    neo4j_uri='bolt://localhost:7687',
    neo4j_user='neo4j',
    neo4j_password='your_password'
)

# Execute a semantic search query
result = tool._run(
    search_query="Find all users who follow John",
    similarity_threshold=0.7,
    limit=10
)
print(result)
```

## Arguments
The Neo4jSearchTool requires the following arguments for its operation:

- `neo4j_uri`: A string representing the URI of the Neo4j database (e.g., `bolt://localhost:7687` or `neo4j://localhost:7687`). This argument is mandatory.
- `neo4j_user`: A string specifying the username for Neo4j database authentication. This argument is mandatory.
- `neo4j_password`: A string specifying the password for Neo4j database authentication. This argument is mandatory.
- `search_query`: A string containing the semantic search query you want to perform. This is used when calling `_run()` method.
- `similarity_threshold` (optional): A float between 0 and 1 specifying the minimum similarity score for results. Defaults to 0.6.
- `limit` (optional): An integer specifying the maximum number of results to return. Defaults to 5.

## Usage with Cypher Queries

The tool automatically handles Cypher queries to extract data from your Neo4j database. When you add data using `tool.add()`, it executes your Cypher query and stores the results for semantic search:

```python
# Add data from a Cypher query
tool.add("MATCH (n:Person)-[:KNOWS]->(f:Person) RETURN n.name as person, f.name as friend")

# Now you can search semantically
result = tool._run(search_query="Find people who know others")
```

## Custom model and embeddings

By default, the tool uses OpenAI for both embeddings and summarization. To customize the model, you can use a config dictionary as follows:

```python
tool = Neo4jSearchTool(
    neo4j_uri='bolt://localhost:7687',
    neo4j_user='neo4j',
    neo4j_password='your_password',
    config=dict(
        llm=dict(
            provider="ollama", # or google, openai, anthropic, llama2, ...
            config=dict(
                model="llama2",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)
```

## Connection URI Formats

The `neo4j_uri` parameter supports several connection schemes:

- `bolt://` - Bolt protocol (recommended for most use cases)
- `neo4j://` - Neo4j URI scheme with Bolt
- `bolt+s://` - Bolt over TLS/SSL
- `neo4j+s://` - Neo4j URI scheme with Bolt over TLS/SSL

Examples:
```python
# Local database
neo4j_uri='bolt://localhost:7687'

# Remote database
neo4j_uri='bolt://neo4j.example.com:7687'

# Secure connection
neo4j_uri='bolt+s://neo4j.example.com:7687'

# Neo4j Aura (managed cloud service)
neo4j_uri='neo4j+s://your-instance.databases.neo4j.io:7687'
```

