# Elasticsearch Tool

A tool for executing queries on Elastic database with built-in connection pooling, retry logic, and async execution support.

## Installation

```bash
uv sync --extra elasticsearch

OR 
uv pip install elasticsearch>=8.17.0 aiohttp~=3.11

OR 
pip install elasticsearch>=8.17.0 aiohttp~=3.11
```

## Quick Start

```python
import asyncio
from pydantic import SecretStr
from crewai_tools import ElasticsearchSearchTool, ElasticsearchConfig

# Create configuration
config = ElasticsearchConfig(
    hosts=["http://<your_host>:9200"],
    username="<your_username>",
    password=SecretStr("<your_password>"),
    
    # In case you're using elastic cloud
    api_key=SecretStr("<your_api_key>"),
    cloud_id="<your_cloud_id>"
)

# Initialize tool
tool = ElasticsearchSearchTool(
    config=config,
    pool_size=5,
    max_retries=3,
    enable_caching=True
)


# Execute query
async def main():
    search_result = await tool._run("""
    {
      "query": {
        "range": {
          "timestamp": {
            "gte": "now-30d/d",
            "lte": "now/d"
          }
        }
      }
    }
    """,
    index="iam-logs")
    
    print(search_result)


if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- ✨ Asynchronous query execution
- 🚀 Connection pooling for better performance
- 🔄 Automatic retries for transient failures
- 💾 Query result caching (optional)
- 🔒 Support for both password and key-pair authentication

## Configuration Options
# Elasticsearch Search Tool

A powerful tool for executing searches on Elasticsearch with support for both self-hosted and Elastic Cloud deployments.

## Configuration

### ElasticsearchConfig Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| hosts | Yes* | List of Elasticsearch hosts |
| username | No | Elasticsearch username |
| password | No | Elasticsearch password |
| api_key | No | Elasticsearch API key |
| cloud_id | Yes* | Elasticsearch Cloud ID |
| verify_certs | No | Verify SSL certificates (default: True) |
| default_index | No | Default index to search |

\* Either hosts or cloud_id must be provided

### Tool Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| pool_size | 5       | Size of connection pool |
| max_retries | 3       | Maximum retry attempts for failed searches |
| retry_delay | 1.0     | Delay between retries in seconds |
| enable_caching | False   | Enable/disable search result caching |

## Advanced Usage

### Self-hosted Elasticsearch

```python
config = ElasticsearchConfig(
    hosts=["http://es1:9200", "http://es2:9200"],
    username="your_username",
    password="your_password",
    default_index="your_index"
)
```

### Elastic Cloud Deployment

```python
config = ElasticsearchConfig(
    cloud_id="deployment:xxxx",
    api_key="your_api_key",
    default_index="your_index"
)
```

## Search Examples

### Query String Search

```python
result = await tool._run(
    query="status:active AND user.name:john*",
    index="users",
    size=10
)
```

### Query DSL Search

```python
result = await tool._run(
    query="""
    {
      "query": {
        "range": {
          "@timestamp": {
            "gte": "now-30d/d",
            "lte": "now/d"
          }
        }
      },
      "sort": [
        {
          "@timestamp": {
            "order": "desc"
          }
        }
      ]
    }
    """,
    index="logs"
)
```