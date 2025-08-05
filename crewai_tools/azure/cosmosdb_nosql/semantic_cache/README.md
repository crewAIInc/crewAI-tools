# Azure CosmosDB Semantic Cache Tool

The Azure CosmosDB Semantic Cache Tool provides intelligent LLM response caching for CrewAI agents using semantic similarity search. This tool helps reduce API costs, improve response times, and ensure consistent outputs by caching and retrieving LLM responses based on semantic similarity rather than exact string matching.

## Features

- **Semantic Similarity Caching**: Cache LLM responses with vector-based similarity matching
- **Intelligent Cache Retrieval**: Find semantically similar queries even with different wording
- **Configurable Similarity Thresholds**: Control cache hit sensitivity with adjustable thresholds
- **TTL Support**: Automatic cache expiration with time-to-live settings
- **Hybrid Search**: Combine vector similarity with text-based filtering
- **Cache Management**: Update, clear, and manage cached responses
- **Multiple LLM Support**: Work with OpenAI, Azure OpenAI, and other embedding providers
- **Cost Optimization**: Reduce LLM API calls and associated costs

## Installation

```bash
pip install crewai-tools[azure]
```

## Prerequisites

- Azure CosmosDB account with NoSQL API and vector search capabilities
- OpenAI or Azure OpenAI API access for embeddings
- Either CosmosDB API key or Azure credentials for authentication
- Python 3.8+ environment

## Configuration

### Basic Configuration with OpenAI

```python
from crewai_tools.azure.cosmosdb_nosql.semantic_cache import CosmosDBSemanticCacheTool
from crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool import CosmosDBSemanticCacheConfig

config = CosmosDBSemanticCacheConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    cosmos_key="your-cosmos-db-key",
    database_name="llm_cache",
    container_name="semantic_cache",
    openai_api_key="your-openai-key",
    embedding_model="text-embedding-ada-002"
)

cache_tool = CosmosDBSemanticCacheTool(config=config)
```

### Configuration with Azure OpenAI

```python
config = CosmosDBSemanticCacheConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    cosmos_key="your-cosmos-db-key",
    database_name="llm_cache",
    container_name="semantic_cache",
    azure_openai_endpoint="https://your-resource.openai.azure.com/",
    azure_openai_api_key="your-azure-openai-key",
    azure_openai_api_version="2024-02-01",
    embedding_deployment="text-embedding-ada-002"
)

cache_tool = CosmosDBSemanticCacheTool(config=config)
```

### Configuration with Azure Token Credential

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
config = CosmosDBSemanticCacheConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    token_credential=credential,
    database_name="llm_cache",
    container_name="semantic_cache",
    openai_api_key="your-openai-key"
)

cache_tool = CosmosDBSemanticCacheTool(config=config)
```

## Usage Examples

### Complete CrewAI Integration Example

```python
from crewai import Agent, Task, Crew
from crewai_tools.azure.cosmosdb_nosql.semantic_cache import CosmosDBSemanticCacheTool
from crewai_tools.azure.cosmosdb_nosql.semantic_cache.semantic_cache_tool import CosmosDBSemanticCacheConfig
import openai

# Configure the semantic cache tool
cache_config = CosmosDBSemanticCacheConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    cosmos_key="your-cosmos-db-key",
    database_name="crew_cache",
    container_name="llm_responses",
    openai_api_key="your-openai-key",
    similarity_threshold=0.85
)

cache_tool = CosmosDBSemanticCacheTool(config=cache_config)

# Create an agent with caching capabilities
cached_agent = Agent(
    role="Efficient Assistant",
    goal="Provide fast responses by utilizing intelligent caching",
    backstory="You are an expert at providing quick, consistent responses by leveraging semantic caching.",
    tools=[cache_tool],
    verbose=True
)

# Task that benefits from caching
analysis_task = Task(
    description="""
    Before generating a new analysis, check the semantic cache for similar queries about:
    "What are the benefits of machine learning in healthcare?"
    
    If a similar response exists with high similarity (>0.8), return the cached response.
    Otherwise, generate a new response and cache it for future use.
    """,
    agent=cached_agent,
    expected_output="Analysis of ML benefits in healthcare (cached or newly generated)"
)

# Create and execute crew
crew = Crew(
    agents=[cached_agent],
    tasks=[analysis_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

### Cache Operations

#### 1. Search for Cached Response

```python
# Search for semantically similar cached responses
result = cache_tool._run(
    operation="search",
    query="What are the advantages of AI in medical diagnosis?",
    similarity_threshold=0.8,
    top_k=3
)

import json
search_results = json.loads(result)

if search_results and len(search_results) > 0:
    best_match = search_results[0]
    print(f"Cache hit! Similarity: {best_match['similarity_score']}")
    print(f"Cached response: {best_match['response']}")
else:
    print("No similar cached responses found")
```

#### 2. Store LLM Response in Cache

```python
# Store a new LLM response with semantic indexing
llm_response = """
Machine learning offers several key benefits in healthcare:
1. Improved diagnostic accuracy through pattern recognition
2. Personalized treatment recommendations based on patient data
3. Drug discovery acceleration through predictive modeling
4. Early disease detection via medical imaging analysis
5. Population health insights from large-scale data analysis
"""

result = cache_tool._run(
    operation="store",
    query="Benefits of machine learning in healthcare",
    response=llm_response,
    model="gpt-4",
    ttl=86400,  # Cache for 24 hours
    metadata={
        "topic": "healthcare_ai",
        "complexity": "intermediate",
        "timestamp": "2025-01-15T10:30:00Z"
    }
)
```

#### 3. Update Cached Response

```python
# Update an existing cached response
updated_response = """
Machine learning provides transformative benefits in healthcare:
1. Enhanced diagnostic precision with AI-powered analysis
2. Personalized medicine through genomic data integration
3. Accelerated drug discovery and clinical trial optimization
4. Predictive analytics for patient risk assessment
5. Operational efficiency improvements in healthcare delivery
6. Real-time monitoring and alert systems
"""

result = cache_tool._run(
    operation="update",
    cache_id="existing_cache_id",
    response=updated_response,
    metadata={
        "updated_at": "2025-01-15T12:00:00Z",
        "version": "2.0"
    }
)
```

#### 4. Clear Cache

```python
# Clear all cached responses
result = cache_tool._run(operation="clear")

# Clear cache with specific filters
result = cache_tool._run(
    operation="clear",
    filter_criteria={
        "topic": "outdated_content",
        "created_at": {"$lt": "2025-01-01T00:00:00Z"}
    }
)
```

### Advanced Usage Patterns

#### Smart Cache-First Response Generation

```python
def get_cached_or_generate_response(query, cache_tool, llm_client):
    """
    Smart function to get cached response or generate new one
    """
    import json
    
    # Try to find cached response
    cache_result = cache_tool._run(
        operation="search",
        query=query,
        similarity_threshold=0.85,
        top_k=1
    )
    
    cached_responses = json.loads(cache_result)
    
    if cached_responses and len(cached_responses) > 0:
        print(f"Cache hit! Similarity: {cached_responses[0]['similarity_score']}")
        return cached_responses[0]['response']
    
    # Generate new response
    print("Cache miss. Generating new response...")
    new_response = llm_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    ).choices[0].message.content
    
    # Cache the new response
    cache_tool._run(
        operation="store",
        query=query,
        response=new_response,
        model="gpt-4",
        ttl=86400
    )
    
    return new_response

# Usage
query = "Explain quantum computing applications in cryptography"
response = get_cached_or_generate_response(query, cache_tool, openai_client)
print(response)
```

#### Batch Cache Operations

```python
# Store multiple responses in batch
responses_to_cache = [
    {
        "query": "What is machine learning?",
        "response": "Machine learning is a subset of AI...",
        "model": "gpt-4"
    },
    {
        "query": "How does deep learning work?", 
        "response": "Deep learning uses neural networks...",
        "model": "gpt-4"
    },
    {
        "query": "What are neural networks?",
        "response": "Neural networks are computing systems...",
        "model": "gpt-4"
    }
]

for item in responses_to_cache:
    result = cache_tool._run(
        operation="store",
        query=item["query"],
        response=item["response"],
        model=item["model"],
        ttl=3600
    )
    print(f"Cached: {item['query'][:50]}...")
```

#### Cache Analytics and Management

```python
# Get cache statistics
def get_cache_stats(cache_tool):
    """Get cache usage statistics"""
    import json
    
    # Search all cached items
    all_items = cache_tool._run(
        operation="search",
        query="",  # Empty query to get all items
        similarity_threshold=0.0,
        top_k=1000
    )
    
    items = json.loads(all_items)
    
    if not items:
        return {"total_items": 0}
    
    # Analyze cache contents
    models = {}
    topics = {}
    
    for item in items:
        model = item.get('model', 'unknown')
        models[model] = models.get(model, 0) + 1
        
        topic = item.get('metadata', {}).get('topic', 'general')
        topics[topic] = topics.get(topic, 0) + 1
    
    return {
        "total_items": len(items),
        "models": models,
        "topics": topics,
        "avg_similarity": sum(item.get('similarity_score', 0) for item in items) / len(items)
    }

stats = get_cache_stats(cache_tool)
print("Cache Statistics:", stats)
```

### Integration with Different LLM Providers

#### OpenAI Integration

```python
import openai

class CachedOpenAIClient:
    def __init__(self, cache_tool, openai_client):
        self.cache_tool = cache_tool
        self.openai_client = openai_client
        self.similarity_threshold = 0.85
    
    def cached_completion(self, query, model="gpt-4", **kwargs):
        # Check cache first
        cache_result = self.cache_tool._run(
            operation="search",
            query=query,
            similarity_threshold=self.similarity_threshold,
            top_k=1
        )
        
        import json
        cached_responses = json.loads(cache_result)
        
        if cached_responses:
            print("Using cached response")
            return cached_responses[0]['response']
        
        # Generate new response
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query}],
            **kwargs
        ).choices[0].message.content
        
        # Cache the response
        self.cache_tool._run(
            operation="store",
            query=query,
            response=response,
            model=model,
            ttl=86400
        )
        
        return response

# Usage
openai_client = openai.OpenAI(api_key="your-key")
cached_client = CachedOpenAIClient(cache_tool, openai_client)

response = cached_client.cached_completion(
    "Explain the benefits of renewable energy",
    model="gpt-4"
)
```

#### Azure OpenAI Integration

```python
from openai import AzureOpenAI

azure_client = AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-azure-openai-key",
    api_version="2024-02-01"
)

cached_azure_client = CachedOpenAIClient(cache_tool, azure_client)
response = cached_azure_client.cached_completion(
    "What are the advantages of cloud computing?",
    model="gpt-4"  # Your deployment name
)
```

## Configuration Options

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `cosmos_host` | CosmosDB account endpoint URL | - | Yes |
| `cosmos_key` | CosmosDB account key | - | Yes* |
| `token_credential` | Azure token credential | - | Yes* |
| `database_name` | Database name | "semantic_cache" | No |
| `container_name` | Container name | "cache_container" | No |
| `openai_api_key` | OpenAI API key | - | Yes** |
| `azure_openai_endpoint` | Azure OpenAI endpoint | - | Yes** |
| `azure_openai_api_key` | Azure OpenAI API key | - | Yes** |
| `embedding_model` | Embedding model name | "text-embedding-ada-002" | No |
| `similarity_threshold` | Default similarity threshold | 0.8 | No |
| `max_cache_size` | Maximum cached items | 10000 | No |

*Either `cosmos_key` or `token_credential` must be provided
**Either OpenAI or Azure OpenAI credentials must be provided

## Operation Parameters

### Search Operation
- `query` (str): Search query text
- `similarity_threshold` (float): Minimum similarity score (0.0-1.0)
- `top_k` (int): Maximum number of results
- `filter_criteria` (dict): Additional filtering

### Store Operation
- `query` (str): Original query text
- `response` (str): LLM response to cache
- `model` (str): LLM model used
- `ttl` (int, optional): Time-to-live in seconds
- `metadata` (dict, optional): Additional metadata

### Update Operation
- `cache_id` (str): ID of cache item to update
- `response` (str, optional): New response text
- `metadata` (dict, optional): Updated metadata
- `ttl` (int, optional): New TTL value

### Clear Operation
- `filter_criteria` (dict, optional): Criteria for selective clearing

## Performance Optimization

### 1. Similarity Threshold Tuning

```python
# Test different thresholds to find optimal balance
thresholds = [0.7, 0.75, 0.8, 0.85, 0.9]

for threshold in thresholds:
    result = cache_tool._run(
        operation="search",
        query="test query",
        similarity_threshold=threshold,
        top_k=5
    )
    
    import json
    hits = json.loads(result)
    print(f"Threshold {threshold}: {len(hits)} hits")
```

### 2. Cache Size Management

```python
# Implement cache size limits
def manage_cache_size(cache_tool, max_size=10000):
    # Get current cache size
    all_items = cache_tool._run(
        operation="search",
        query="",
        similarity_threshold=0.0,
        top_k=max_size + 1000
    )
    
    import json
    items = json.loads(all_items)
    
    if len(items) > max_size:
        # Clear oldest items
        items.sort(key=lambda x: x.get('created_at', ''))
        items_to_remove = items[:-max_size]
        
        for item in items_to_remove:
            cache_tool._run(
                operation="clear",
                filter_criteria={"id": item['id']}
            )
```

### 3. TTL Strategy

```python
# Different TTL strategies based on content type
def get_ttl_for_content(query, response):
    """Determine appropriate TTL based on content characteristics"""
    
    # Factual information - longer TTL
    if any(word in query.lower() for word in ['what is', 'define', 'fact']):
        return 86400 * 7  # 7 days
    
    # Current events - shorter TTL
    if any(word in query.lower() for word in ['news', 'current', 'latest']):
        return 3600  # 1 hour
    
    # Technical explanations - medium TTL
    if any(word in query.lower() for word in ['how to', 'explain', 'tutorial']):
        return 86400  # 1 day
    
    # Default TTL
    return 86400  # 1 day

# Usage
ttl = get_ttl_for_content(query, response)
cache_tool._run(
    operation="store",
    query=query,
    response=response,
    ttl=ttl
)
```

## Best Practices

### 1. Cache Key Design
```python
# Use consistent query normalization
def normalize_query(query):
    """Normalize queries for better cache hits"""
    return query.lower().strip().replace('?', '').replace('.', '')

normalized_query = normalize_query("What are the benefits of AI?")
```

### 2. Metadata Strategy
```python
# Rich metadata for better cache management
metadata = {
    "topic": "artificial_intelligence",
    "complexity": "beginner",
    "language": "en",
    "content_type": "explanation",
    "model_version": "gpt-4-1106-preview",
    "user_type": "developer"
}
```

### 3. Error Handling
```python
def safe_cache_operation(cache_tool, operation, **kwargs):
    """Safe wrapper for cache operations"""
    try:
        result = cache_tool._run(operation=operation, **kwargs)
        return json.loads(result)
    except Exception as e:
        print(f"Cache operation failed: {e}")
        return None

# Usage
cached_response = safe_cache_operation(
    cache_tool, 
    "search", 
    query="test query",
    similarity_threshold=0.8
)
```

## Azure CosmosDB Documentation

- [Azure CosmosDB Vector Search](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-search)
- [Azure CosmosDB Hybrid Search](https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/hybrid-search?context=%2Fazure%2Fcosmos-db%2Fnosql%2Fcontext%2Fcontext)
- [Vector Indexing in CosmosDB](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/vector-indexing-policy)
- [NoSQL API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/)
- [Time-to-Live (TTL)](https://docs.microsoft.com/en-us/azure/cosmos-db/time-to-live)
- [Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-cosmos/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [Azure OpenAI Service](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

## Troubleshooting

### Common Issues

1. **Low Cache Hit Rates**: Adjust similarity threshold or improve query normalization
2. **Vector Dimension Mismatches**: Ensure consistent embedding models
3. **High Storage Costs**: Implement TTL and cache size management
4. **Authentication Errors**: Verify API keys and credentials
5. **Performance Issues**: Optimize similarity thresholds and implement proper indexing

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test cache operations
result = cache_tool._run(
    operation="search",
    query="test query",
    similarity_threshold=0.5,
    top_k=1
)
print("Debug result:", result)
```

## License

This tool is part of the CrewAI Tools package and follows the same licensing terms.
