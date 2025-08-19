# ChromaSearchTool

## Description

Use this tool to do semantic search in a Chroma collection.

Chroma is the search and retrieval database built for AI. Chroma can search
documents using semantic search, full-text search, regex search, and metadata
tags. You can follow their docs here: <https://docs.trychroma.com/docs/overview/introduction>

## Installation

Install the crewai_tools package by executing the following command in your terminal:

```shell
uv pip install 'crewai[tools]' chromadb
```

## Basic Usage

The `ChromaSearchTool` takes a Chroma collection directly. See the Chroma
docs on how you can [configure your collection](https://docs.trychroma.com/docs/collections/configure)
or [choose which embedding model is used](https://docs.trychroma.com/docs/embeddings/embedding-functions)

```python
import chromadb
from crewai_tools import ChromaSearchTool

# 1. Create your Chroma client
client = chromadb.PersistentClient(path="./chroma_db")
# or client = chromadb.HttpClient(...)
# or client = chromadb.CloudClient(...)

# 2. Get or create your collection
collection = client.get_or_create_collection(name="my_documents")

# 3. Create the tool using the collections
tool = ChromaSearchTool(
    collection=collection,
    limit=5  # optional, default is 3
)
```

## Usage Examples

### Usage with Agent

```python
import chromadb
from crewai_tools import ChromaSearchTool
from crewai import Agent

# Setup your Chroma collection
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="my_documents")

# Create the search tool
tool = ChromaSearchTool(collection=collection)

# Add the tool to an agent
rag_agent = Agent(
    name="rag_agent",
    role="You are a helpful assistant that can answer questions with the help of the Chroma tool.",
    llm="gpt-4o-mini",
    tools=[tool],
)
```

## Arguments

- `collection` : A Chroma collection object to search in. (Required)
- `limit` : The number of results to return. (Optional, default: 3)

## Query Parameters

- `query` : The search query text. (Required)
- `where` : Optional metadata filter to apply to the search. (Optional)
- `where_document` : Optional document content filter to apply to the search. (Optional)
