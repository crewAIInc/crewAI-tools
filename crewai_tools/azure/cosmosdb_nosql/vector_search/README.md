# Azure CosmosDB Vector Search Tool

The Azure CosmosDB Vector Search Tool enables CrewAI agents to perform sophisticated vector similarity searches on Azure CosmosDB NoSQL containers. This tool leverages CosmosDB's integrated vector search capabilities to find semantically similar documents based on vector embeddings.

## Features

- **Vector Similarity Search**: Perform cosine similarity searches on vector embeddings
- **Multiple Search Types**: Support for vector-only and hybrid (vector + full-text) searches
- **Configurable Results**: Control result count and similarity thresholds
- **Flexible Vector Support**: Work with embeddings from any ML model
- **Advanced Filtering**: Combine vector search with traditional query filters
- **Multiple Auth Methods**: Support for API keys and Azure token credentials
- **Efficient Indexing**: Leverage CosmosDB's optimized vector indexing

## Installation

```bash
pip install crewai-tools[azure]
```

## Prerequisites

- Azure CosmosDB account with NoSQL API
- Container configured with vector indexing policy
- Either an API key or Azure credentials for authentication
- Python 3.8+ environment

## Configuration

### Basic Configuration with API Key

```python
from crewai_tools.azure.cosmosdb_nosql.vector_search import CosmosDBVectorSearchTool
from crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool import AzureCosmosDBNoSqlSearchConfig

config = AzureCosmosDBNoSqlSearchConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    key="your-cosmos-db-key",
    database_name="vector_database",
    container_name="embeddings_container"
)

vector_search_tool = CosmosDBVectorSearchTool(config=config)
```

### Configuration with Azure Token Credential

```python
from azure.identity import DefaultAzureCredential
from crewai_tools.azure.cosmosdb_nosql.vector_search import CosmosDBVectorSearchTool
from crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool import AzureCosmosDBNoSqlSearchConfig

credential = DefaultAzureCredential()
config = AzureCosmosDBNoSqlSearchConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    token_credential=credential,
    database_name="vector_database", 
    container_name="embeddings_container"
)

vector_search_tool = CosmosDBVectorSearchTool(config=config)
```

### Container Setup with Vector Indexing

```python
# Example container properties for vector search
container_properties = {
    "id": "embeddings_container",
    "partitionKey": {"paths": ["/category"], "kind": "Hash"},
    "vectorEmbeddingPolicy": {
        "vectorEmbeddings": [
            {
                "path": "/embedding",
                "dataType": "float32",
                "distanceFunction": "cosine",
                "dimensions": 1536  # Adjust based on your embedding model
            }
        ]
    },
    "indexingPolicy": {
        "vectorIndexes": [
            {
                "path": "/embedding",
                "type": "quantizedFlat"
            }
        ]
    }
}
```

## Usage Examples

### Complete CrewAI Integration Example

```python
from crewai import Agent, Task, Crew
from crewai_tools.azure.cosmosdb_nosql.vector_search import CosmosDBVectorSearchTool
from crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool import AzureCosmosDBNoSqlSearchConfig
import openai

# Configure the vector search tool
search_config = AzureCosmosDBNoSqlSearchConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    key="your-cosmos-db-key",
    database_name="knowledge_base",
    container_name="documents"
)

vector_search_tool = CosmosDBVectorSearchTool(config=search_config)

# Create an agent with vector search capabilities
research_agent = Agent(
    role="Research Assistant",
    goal="Find relevant information using semantic search capabilities",
    backstory="You are an expert at finding relevant information using advanced vector search techniques.",
    tools=[vector_search_tool],
    verbose=True
)

# Task to find similar documents
search_task = Task(
    description="""
    Find documents similar to the query: "machine learning applications in healthcare"
    
    Use the vector search tool to find the top 5 most semantically similar documents.
    The search should focus on documents about AI/ML applications in medical domains.
    """,
    agent=research_agent,
    expected_output="List of top 5 relevant documents with similarity scores and content"
)

# Create and execute crew
crew = Crew(
    agents=[research_agent],
    tasks=[search_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

### Vector Search Operations

#### 1. Basic Vector Search

```python
# Example query vector (from OpenAI or other embedding model)
query_embedding = [0.1, 0.2, -0.1, 0.5, ...]  # 1536-dimensional vector

result = vector_search_tool._run(
    query="machine learning in healthcare",
    top_k=5,
    query_vector=query_embedding
)
```

#### 2. Vector Search with Text Query (Auto-embedding)

```python
# Tool automatically generates embeddings for text queries
result = vector_search_tool._run(
    query="artificial intelligence medical diagnosis",
    top_k=10,
    embedding_model="text-embedding-ada-002"
)
```

#### 3. Hybrid Search (Vector + Full-text)

```python
# Combine vector similarity with traditional text search
result = vector_search_tool._run(
    query="deep learning neural networks",
    top_k=5,
    query_vector=query_embedding,
    hybrid_search=True,
    text_query="neural networks AND deep learning"
)
```

#### 4. Search with Filters

```python
# Add additional filtering criteria
result = vector_search_tool._run(
    query="machine learning algorithms",
    top_k=5,
    query_vector=query_embedding,
    filter_criteria={
        "category": "research_papers",
        "publication_year": {"$gte": 2020}
    }
)
```

#### 5. Search with Similarity Threshold

```python
# Only return results above similarity threshold
result = vector_search_tool._run(
    query="computer vision applications",
    top_k=10,
    query_vector=query_embedding,
    similarity_threshold=0.8
)
```

### Working with OpenAI Embeddings

```python
import openai
from crewai_tools.azure.cosmosdb_nosql.vector_search import CosmosDBVectorSearchTool

# Generate embedding for search query
client = openai.OpenAI(api_key="your-openai-key")

def get_embedding(text, model="text-embedding-ada-002"):
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

# Perform vector search
query_text = "machine learning in medical imaging"
query_vector = get_embedding(query_text)

result = vector_search_tool._run(
    query=query_text,
    top_k=5,
    query_vector=query_vector
)
```

### Document Storage Example

Before searching, you need documents with embeddings in your container:

```python
# Example document structure for vector search
document = {
    "id": "doc_001",
    "title": "AI Applications in Healthcare",
    "content": "Machine learning and artificial intelligence are revolutionizing healthcare...",
    "category": "healthcare",
    "publication_year": 2024,
    "embedding": [0.1, 0.2, -0.1, 0.5, ...],  # 1536-dimensional vector
    "metadata": {
        "author": "Dr. Smith",
        "journal": "AI in Medicine",
        "doi": "10.1000/example"
    }
}
```

## Configuration Options

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `cosmos_host` | CosmosDB account endpoint URL | - | Yes |
| `key` | CosmosDB account key | - | Yes* |
| `token_credential` | Azure token credential | - | Yes* |
| `database_name` | Database name | "vector_database" | No |
| `container_name` | Container name | "vector_container" | No |
| `embedding_field` | Field containing embeddings | "embedding" | No |
| `content_fields` | Fields to return in results | ["id", "content"] | No |

*Either `key` or `token_credential` must be provided

## Search Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `query` | Search query text | - | Yes |
| `top_k` | Number of results to return | 5 | No |
| `query_vector` | Pre-computed query embedding | - | No |
| `embedding_model` | Model for auto-embedding | - | No |
| `hybrid_search` | Enable hybrid search | False | No |
| `text_query` | Full-text search query | - | No |
| `filter_criteria` | Additional filters | - | No |
| `similarity_threshold` | Minimum similarity score | 0.0 | No |

## Vector Search Best Practices

### 1. Embedding Model Consistency
```python
# Use the same embedding model for indexing and searching
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSIONS = 1536

# Always use consistent model for both storage and search
```

### 2. Optimal Partition Key Design
```python
# Choose partition keys that align with search patterns
container_properties = {
    "partitionKey": {"paths": ["/domain"], "kind": "Hash"}  # e.g., "healthcare", "finance"
}
```

### 3. Efficient Similarity Thresholds
```python
# Set appropriate similarity thresholds to filter noise
result = vector_search_tool._run(
    query="specific medical condition",
    similarity_threshold=0.75,  # Adjust based on your use case
    top_k=10
)
```

### 4. Hybrid Search for Better Relevance
```python
# Combine vector and text search for best results
result = vector_search_tool._run(
    query="machine learning diagnosis",
    hybrid_search=True,
    text_query="machine learning AND (diagnosis OR diagnostic)",
    top_k=5
)
```

## Error Handling

```python
import json

result = vector_search_tool._run(
    query="search query",
    top_k=5
)

try:
    parsed_result = json.loads(result)
    if "error" in parsed_result:
        print(f"Search error: {parsed_result['error']}")
    else:
        documents = parsed_result.get("documents", [])
        print(f"Found {len(documents)} similar documents")
        for doc in documents:
            print(f"Score: {doc.get('similarity_score', 'N/A')}")
            print(f"Content: {doc.get('content', 'N/A')}")
except json.JSONDecodeError:
    print("Failed to parse search results")
```

## Performance Optimization

### 1. Index Configuration
```python
# Optimize vector index for your use case
indexing_policy = {
    "vectorIndexes": [
        {
            "path": "/embedding",
            "type": "quantizedFlat"  # or "diskANN" for large datasets
        }
    ]
}
```

### 2. Query Optimization
```python
# Limit results and use filters to improve performance
result = vector_search_tool._run(
    query="specific query",
    top_k=10,  # Reasonable limit
    filter_criteria={"category": "specific_domain"},  # Pre-filter data
    similarity_threshold=0.7  # Filter low-relevance results
)
```

### 3. Batch Processing
```python
# For multiple searches, consider batching
queries = ["query1", "query2", "query3"]
results = []

for query in queries:
    result = vector_search_tool._run(query=query, top_k=5)
    results.append(result)
```

## Integration with Popular ML Libraries

### Hugging Face Transformers
```python
from transformers import AutoTokenizer, AutoModel
import torch

def get_huggingface_embedding(text, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
    
    return embeddings[0].tolist()

# Use with vector search
query_embedding = get_huggingface_embedding("machine learning healthcare")
result = vector_search_tool._run(
    query="machine learning healthcare",
    query_vector=query_embedding,
    top_k=5
)
```

### Azure OpenAI Integration
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-openai-key",
    api_version="2024-02-01"
)

def get_azure_openai_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"  # Your deployed model
    )
    return response.data[0].embedding

query_embedding = get_azure_openai_embedding("AI in medical diagnosis")
result = vector_search_tool._run(
    query="AI in medical diagnosis",
    query_vector=query_embedding,
    top_k=5
)
```

## Azure CosmosDB Documentation

- [Azure CosmosDB Vector Search](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search)
- [Vector Indexing in CosmosDB](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-indexing-policy)
- [NoSQL API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/)
- [Vector Embeddings Best Practices](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search-best-practices)
- [Similarity Search Concepts](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search-concepts)
- [Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-cosmos/)

## Troubleshooting

### Common Issues

1. **Vector Dimension Mismatch**: Ensure query vector dimensions match indexed embeddings
2. **Index Configuration**: Verify container has proper vector indexing policy
3. **Similarity Scores**: Adjust thresholds based on your embedding model characteristics
4. **Performance Issues**: Consider using diskANN indexing for large datasets
5. **Query Limits**: Be aware of CosmosDB query timeout and RU consumption

### Debug Tips

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with simple queries first
result = vector_search_tool._run(
    query="test",
    top_k=1,
    query_vector=[0.1] * 1536  # Simple test vector
)
```

## License

This tool is part of the CrewAI Tools package and follows the same licensing terms.
