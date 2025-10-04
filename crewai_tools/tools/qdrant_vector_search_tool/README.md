# QdrantVectorSearchTool

## Description

This tool is specifically crafted for conducting semantic searches within docs within a Qdrant vector database. Use this tool to find semantically similar docs to a given query.

Qdrant is a vector database that is used to store and query vector embeddings. You can follow their docs here: https://qdrant.tech/documentation/

## Installation

Install the crewai_tools package by executing the following command in your terminal:

```shell
uv pip install 'crewai[tools] qdrant-client openai'
```

## Example

To utilize the QdrantVectorSearchTool for different use cases, follow these examples: Default model is openai.

**Synchronous Usage:**

```python
from crewai import Agent
from crewai_tools import QdrantVectorSearchTool

# Initialize the tool
tool = QdrantVectorSearchTool(
    collection_name="example_collections",
    limit=3,
    qdrant_url="https://your-qdrant-cluster-url.com",
    qdrant_api_key="your-qdrant-api-key", # (optional)
)

# Adding the tool to an agent
rag_agent = Agent(
    name="rag_agent",
    role="You are a helpful assistant that can answer questions with the help of the QdrantVectorSearchTool. Retrieve the most relevant docs from the Qdrant database.",
    llm="gpt-4o-mini",
    tools=[tool],
)

# Example task execution (synchronous)
task = Task(description="Search for documents about 'machine learning'", agent=rag_agent)
result = task.execute()
```

**Asynchronous Usage:**

```python
import asyncio
from crewai import Agent
from crewai_tools import QdrantVectorSearchTool

# Initialize the tool (same as synchronous)
tool = QdrantVectorSearchTool(
    collection_name="example_collections",
    limit=3,
    qdrant_url="https://your-qdrant-cluster-url.com",
    qdrant_api_key="your-qdrant-api-key", # (optional)
)

# Adding the tool to an agent
rag_agent_async = Agent(
    name="rag_agent_async",
    role="You are a helpful assistant that can answer questions asynchronously with the help of the QdrantVectorSearchTool. Retrieve the most relevant docs from the Qdrant database.",
    llm="gpt-4o-mini",
    tools=[tool],
    allow_delegation=False,
    verbose=True
)

# Example task execution (asynchronous)
async def run_async_task():
    task = Task(description="Search for documents about 'artificial intelligence'", agent=rag_agent_async, async_execution=True)
    result = await task.execute_async()
    print(result)

asyncio.run(run_async_task())

# Direct async tool usage (outside of an agent)
async def direct_async_search():
    results = await tool._arun(query="deep learning trends")
    print(results)

asyncio.run(direct_async_search())
```

## Arguments

- `collection_name` : The name of the collection to search within. (Required)
- `qdrant_url` : The URL of the Qdrant cluster. (Required)
- `qdrant_api_key` : The API key for the Qdrant cluster. (Optional)
- `limit` : The number of results to return. Defaults to 3. (Optional)
- `score_threshold` : Minimum similarity score threshold for results. Defaults to 0.35. (Optional)
- `custom_embedding_fn` : A custom embedding function to use for vectorization. If not provided, the default OpenAI model will be used. (Optional)

**When using the tool within an agent:**

- `query`: The query string to search for in the Qdrant database. (Required)
- `filter_by`: The metadata field to filter results on. (Optional)
- `filter_value`: The value to filter by for the specified `filter_by` field. (Optional)
