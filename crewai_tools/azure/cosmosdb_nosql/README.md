# Azure CosmosDB NoSQL Tools for CrewAI

This package provides a comprehensive suite of Azure CosmosDB NoSQL tools specifically designed for CrewAI agents. These tools leverage Azure CosmosDB's powerful NoSQL capabilities, including vector search, to enable sophisticated data storage, retrieval, and semantic operations.

## Available Tools

### 🧠 [Memory Store Tool](./memory_store/README.md)
**Complete CRUD operations for agent memory management**
- Store, retrieve, update, and delete agent memories
- Support for both single and hierarchical partition keys
- TTL (Time-To-Live) support for automatic memory expiration
- Batch operations for efficient memory management
- Advanced query filtering capabilities

### 🔍 [Vector Search Tool](./vector_search/README.md)
**Semantic similarity search using vector embeddings**
- Cosine similarity search on vector embeddings
- Hybrid search combining vector and full-text capabilities
- Integration with popular embedding models (OpenAI, Hugging Face)
- Configurable similarity thresholds
- Advanced filtering and result ranking

### ⚡ [Semantic Cache Tool](./semantic_cache/README.md)
**Intelligent LLM response caching with semantic matching**
- Cache LLM responses with semantic similarity detection
- Reduce API costs and improve response times
- Support for OpenAI and Azure OpenAI embeddings
- TTL-based cache expiration
- Cache analytics and management capabilities

## Quick Start

### Installation

```bash
pip install crewai-tools[azure]
```

### Basic Setup

```python
from crewai_tools.azure.cosmosdb_nosql import (
    CosmosDBMemoryStoreTool,
    CosmosDBVectorSearchTool, 
    CosmosDBSemanticCacheTool
)

# Basic configuration
cosmos_host = "https://your-account.documents.azure.com:443/"
cosmos_key = "your-cosmos-db-key"
database_name = "your_database"
```

## Complete CrewAI Integration Example

Here's a comprehensive example showing how to use all three tools together in a CrewAI workflow:

```python
from crewai import Agent, Task, Crew
from crewai_tools.azure.cosmosdb_nosql import (
    CosmosDBMemoryStoreTool,
    CosmosDBVectorSearchTool,
    CosmosDBSemanticCacheTool
)
from crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool import AzureCosmosDBMemoryConfig
from crewai_tools.azure.cosmosdb_nosql.vector_search.vector_search_tool import AzureCosmosDBNoSqlSearchConfig
from crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool import CosmosDBSemanticCacheConfig

# Configuration
cosmos_host = "https://your-account.documents.azure.com:443/"
cosmos_key = "your-cosmos-db-key"
openai_key = "your-openai-key"

# Memory Store Configuration
memory_config = AzureCosmosDBMemoryConfig(
    cosmos_host=cosmos_host,
    key=cosmos_key,
    database_name="crew_memory",
    container_name="agent_memories"
)

# Vector Search Configuration
search_config = AzureCosmosDBNoSqlSearchConfig(
    cosmos_host=cosmos_host,
    key=cosmos_key,
    database_name="knowledge_base",
    container_name="documents"
)

# Semantic Cache Configuration
cache_config = CosmosDBSemanticCacheConfig(
    cosmos_host=cosmos_host,
    cosmos_key=cosmos_key,
    database_name="llm_cache",
    container_name="response_cache",
    openai_api_key=openai_key
)

# Initialize tools
memory_tool = CosmosDBMemoryStoreTool(config=memory_config)
search_tool = CosmosDBVectorSearchTool(config=search_config)
cache_tool = CosmosDBSemanticCacheTool(config=cache_config)

# Create intelligent agent with all CosmosDB capabilities
intelligent_agent = Agent(
    role="Intelligent Research Assistant",
    goal="Provide comprehensive research assistance with memory, search, and caching capabilities",
    backstory="""
    You are an advanced AI assistant equipped with persistent memory, semantic search, 
    and intelligent caching capabilities. You can remember past interactions, search 
    through knowledge bases, and cache responses for efficiency.
    """,
    tools=[memory_tool, search_tool, cache_tool],
    verbose=True
)

# Research task that utilizes all tools
research_task = Task(
    description="""
    Research the topic: "Machine Learning Applications in Healthcare"
    
    1. First, check your memory for any previous research on this topic
    2. Check the semantic cache for similar queries to avoid redundant work
    3. If no cached response exists, use vector search to find relevant documents
    4. Generate a comprehensive analysis and store key insights in memory
    5. Cache the response for future similar queries
    6. Provide a well-structured research summary
    """,
    agent=intelligent_agent,
    expected_output="""
    A comprehensive research summary including:
    - Key applications of ML in healthcare
    - Current trends and technologies
    - Benefits and challenges
    - Future outlook
    - References to relevant documents found
    """
)

# Follow-up task that benefits from stored memory
followup_task = Task(
    description="""
    Based on your previous research stored in memory, provide specific recommendations 
    for implementing ML in a hospital setting. Focus on practical steps and considerations.
    """,
    agent=intelligent_agent,
    expected_output="Practical implementation guide for ML in hospital settings"
)

# Execute the crew
crew = Crew(
    agents=[intelligent_agent],
    tasks=[research_task, followup_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

## Tool Comparison and Use Cases

| Tool | Primary Use Case | Key Features | Best For |
|------|------------------|--------------|----------|
| **Memory Store** | Agent state persistence | CRUD operations, TTL, hierarchical keys | Long-term agent memory, user preferences, conversation history |
| **Vector Search** | Semantic document retrieval | Vector similarity, hybrid search, filtering | Knowledge base search, document retrieval, content discovery |
| **Semantic Cache** | LLM response optimization | Similarity matching, TTL, cost reduction | Reducing API costs, improving response times, consistency |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CrewAI Agent                             │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Memory Store   │  Vector Search  │   Semantic Cache        │
│                 │                 │                         │
│ • Agent State   │ • Knowledge     │ • LLM Responses         │
│ • Preferences   │   Retrieval     │ • Query Optimization    │
│ • History       │ • Document      │ • Cost Reduction        │
│                 │   Discovery     │                         │
├─────────────────┼─────────────────┼─────────────────────────┤
│          Azure CosmosDB NoSQL with Vector Search           │
└─────────────────────────────────────────────────────────────┘
```

## Common Patterns

### 1. Memory-Enhanced Search

```python
# Store search preferences in memory
memory_tool._run(
    operation="store",
    memory_item={
        "id": "search_prefs_001",
        "agent_id": "research_agent",
        "content": {
            "preferred_domains": ["healthcare", "AI"],
            "search_history": ["ML applications", "neural networks"]
        }
    }
)

# Use preferences to enhance search
search_result = search_tool._run(
    query="latest AI research",
    top_k=5,
    filter_criteria={"domain": "healthcare"}
)
```

### 2. Cached Knowledge Retrieval

```python
# Check cache before expensive search
cache_result = cache_tool._run(
    operation="search",
    query="AI in medical diagnosis",
    similarity_threshold=0.85
)

if not json.loads(cache_result):
    # Cache miss - perform search and cache result
    search_result = search_tool._run(
        query="AI in medical diagnosis",
        top_k=5
    )
    
    # Cache the search result
    cache_tool._run(
        operation="store", 
        query="AI in medical diagnosis",
        response=search_result,
        ttl=3600
    )
```

### 3. Memory-Guided Conversations

```python
# Retrieve conversation context from memory
context = memory_tool._run(
    operation="retrieve",
    memory_item={},
    partition_key_value="user_123",
    query_filter={"type": "conversation_context"}
)

# Use context to inform responses
# ... generate contextual response ...

# Update memory with new context
memory_tool._run(
    operation="update",
    memory_item={"content": {"latest_topic": "healthcare AI"}},
    partition_key_value="user_123",
    memory_id="context_001"
)
```

## Prerequisites

### Azure CosmosDB Setup

1. **Create CosmosDB Account**: Choose NoSQL API
2. **Enable Vector Search**: Configure vector indexing policies
3. **Set Up Authentication**: Use either API keys or Azure AD

### Container Configuration Examples

#### Memory Store Container
```json
{
    "id": "memory_container",
    "partitionKey": {"paths": ["/agent_id"], "kind": "Hash"}
}
```

#### Vector Search Container
```json
{
    "id": "vector_container", 
    "partitionKey": {"paths": ["/category"], "kind": "Hash"},
    "vectorEmbeddingPolicy": {
        "vectorEmbeddings": [
            {
                "path": "/embedding",
                "dataType": "float32", 
                "distanceFunction": "cosine",
                "dimensions": 1536
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

#### Semantic Cache Container
```json
{
    "id": "cache_container",
    "partitionKey": {"paths": ["/query_hash"], "kind": "Hash"},
    "defaultTtl": 86400,
    "vectorEmbeddingPolicy": {
        "vectorEmbeddings": [
            {
                "path": "/query_embedding",
                "dataType": "float32",
                "distanceFunction": "cosine", 
                "dimensions": 1536
            }
        ]
    }
}
```

## Performance Optimization

### 1. Partition Key Strategy
- **Memory Store**: Use agent_id or user_id for even distribution
- **Vector Search**: Use domain/category for logical grouping
- **Semantic Cache**: Use query_hash for uniform distribution

### 2. Indexing Best Practices
- Configure vector indexes based on your embedding dimensions
- Use composite indexes for complex queries
- Monitor RU consumption and adjust accordingly

### 3. Cost Optimization
- Implement TTL for automatic cleanup
- Use similarity thresholds to reduce unnecessary operations
- Monitor and adjust container throughput based on usage

## Monitoring and Analytics

```python
def get_system_stats(memory_tool, search_tool, cache_tool):
    """Get comprehensive system statistics"""
    
    # Memory usage
    memory_stats = memory_tool._run(
        operation="retrieve",
        memory_item={},
        partition_key_value="system_stats",
        max_results=1000
    )
    
    # Cache hit rates
    cache_stats = cache_tool._run(
        operation="search",
        query="",
        similarity_threshold=0.0,
        top_k=1000
    )
    
    return {
        "memory_items": len(json.loads(memory_stats)),
        "cached_responses": len(json.loads(cache_stats)),
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Error Handling and Resilience

```python
def robust_cosmosdb_operation(tool, operation, **kwargs):
    """Robust wrapper for CosmosDB operations with retry logic"""
    import time
    import json
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = tool._run(operation=operation, **kwargs)
            parsed_result = json.loads(result)
            
            if "error" not in parsed_result:
                return parsed_result
            else:
                print(f"Operation error: {parsed_result['error']}")
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
        if attempt < max_retries - 1:
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
    
    return {"error": "All retry attempts failed"}
```

## Azure CosmosDB Documentation

- [Azure CosmosDB Overview](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction)
- [NoSQL API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/)
- [Vector Search in CosmosDB](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search)
- [Hierarchical Partition Keys](https://docs.microsoft.com/en-us/azure/cosmos-db/hierarchical-partition-keys)
- [Time-to-Live (TTL)](https://docs.microsoft.com/en-us/azure/cosmos-db/time-to-live)
- [Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-cosmos/)
- [Best Practices Guide](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/best-practices)

## Support and Contributing

For issues, questions, or contributions related to these CosmosDB tools:

1. Check the individual tool README files for specific documentation
2. Review the Azure CosmosDB documentation for underlying service details
3. Follow CrewAI Tools contribution guidelines
4. Report issues through the appropriate channels

## License

These tools are part of the CrewAI Tools package and follow the same licensing terms.
