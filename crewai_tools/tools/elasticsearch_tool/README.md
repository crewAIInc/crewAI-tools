# Elasticsearch Tool

A tool for searching and retrieving information from Elasticsearch using vector search and RAG capabilities.

## Installation

```bash
pip install 'crewai[tools]'
```

## Index Configuration

Before using the tool, ensure your index has the correct mapping:

```yaml
PUT /documents
{
  "mappings": {
    "properties": {
      "text": { "type": "text" },
      "embedding": { 
        "type": "dense_vector",
        "dims": 1536,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

## Usage

```python
from crewai_tools import ElasticsearchTool
from crewai_tools.adapters.elasticsearch_adapter import ElasticsearchAdapter

# Initialize the tool
tool = ElasticsearchTool(
    adapter=ElasticsearchAdapter(
        es_url="http://localhost:9200",
        index_name="documents",
        api_key="your_api_key"  # or use username/password
    )
)

# Add documents
tool.add(
    texts=["Document 1 content", "Document 2 content"],
    metadata={"source": "example"}
)

# Use in a crew
crew = Crew(
    agents=[
        Agent(
            role="Researcher",
            goal="Research documents",
            tools=[tool]
        )
    ]
)
```

## Authentication Options

- API Key (recommended):
```python
adapter = ElasticsearchAdapter(
    es_url="http://localhost:9200",
    index_name="documents",
    api_key="your_api_key"
)
```

- Basic Authentication:
```python
adapter = ElasticsearchAdapter(
    es_url="http://localhost:9200",
    index_name="documents",
    username="user",
    password="pass"
)
```

- Elastic Cloud:
```python
adapter = ElasticsearchAdapter(
    es_url="https://your-deployment.es.cloud",
    index_name="documents",
    cloud_id="your-cloud-id",
    api_key="your_api_key"
)
```

## Features

- Vector search for semantic understanding
- Document indexing with metadata
- Configurable top-k results
- Support for both Elasticsearch and OpenSearch
- Secure authentication methods
- Bulk document operations

## Error Handling

The tool handles common errors:
- Connection failures: When the Elasticsearch server is unreachable
- Authentication issues: Invalid API keys or credentials
- Index not found: When the specified index doesn't exist
- Bulk indexing errors: Detailed error messages for failed document operations

See error messages in logs for detailed troubleshooting information.
