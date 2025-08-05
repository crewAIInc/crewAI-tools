# Azure CosmosDB Memory Store Tool

The Azure CosmosDB Memory Store Tool enables CrewAI agents to store, retrieve, update, and manage persistent memory using Azure CosmosDB NoSQL. This tool provides comprehensive CRUD operations for agent memory management with support for both single and hierarchical partition keys.

## Features

- **Complete CRUD Operations**: Store, retrieve, update, and delete memory items
- **Hierarchical Partition Keys**: Support for complex partition key structures
- **TTL Support**: Automatic memory expiration with time-to-live settings
- **Batch Operations**: Efficient bulk operations for memory management
- **Query Filtering**: Advanced filtering capabilities for memory retrieval
- **Error Handling**: Robust error handling with detailed error messages
- **Multiple Auth Methods**: Support for API keys and Azure token credentials

## Installation

```bash
pip install crewai-tools[azure]
```

## Prerequisites

- Azure CosmosDB account with NoSQL API
- Either an API key or Azure credentials for authentication
- Python 3.8+ environment

## Configuration

### Basic Configuration with API Key

```python
from crewai_tools.azure.cosmosdb_nosql.memory_store import CosmosDBMemoryStoreTool
from crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool import AzureCosmosDBMemoryConfig

config = AzureCosmosDBMemoryConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    key="your-cosmos-db-key",
    database_name="memory_database",
    container_name="memory_container"
)

memory_tool = CosmosDBMemoryStoreTool(config=config)
```

### Configuration with Azure Token Credential

```python
from azure.identity import DefaultAzureCredential
from crewai_tools.azure.cosmosdb_nosql.memory_store import CosmosDBMemoryStoreTool
from crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool import AzureCosmosDBMemoryConfig

credential = DefaultAzureCredential()
config = AzureCosmosDBMemoryConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    token_credential=credential,
    database_name="memory_database",
    container_name="memory_container"
)

memory_tool = CosmosDBMemoryStoreTool(config=config)
```

### Hierarchical Partition Key Configuration

```python
config = AzureCosmosDBMemoryConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    key="your-cosmos-db-key",
    database_name="memory_database",
    container_name="memory_container",
    cosmos_container_properties={
        "partition_key": {
            "paths": ["/agent_id", "/session_id"], 
            "kind": "MultiHash"
        }
    }
)
```

## Usage Examples

### Complete CrewAI Integration Example

```python
from crewai import Agent, Task, Crew
from crewai_tools.azure.cosmosdb_nosql.memory_store import CosmosDBMemoryStoreTool
from crewai_tools.azure.cosmosdb_nosql.memory_store.memory_store_tool import AzureCosmosDBMemoryConfig

# Configure the memory tool
memory_config = AzureCosmosDBMemoryConfig(
    cosmos_host="https://your-account.documents.azure.com:443/",
    key="your-cosmos-db-key",
    database_name="crew_memory",
    container_name="agent_memories"
)

memory_tool = CosmosDBMemoryStoreTool(config=memory_config)

# Create an agent with memory capabilities
memory_agent = Agent(
    role="Memory Manager",
    goal="Manage and utilize persistent memory for better task continuity",
    backstory="You are an expert at managing information and learning from past interactions.",
    tools=[memory_tool],
    verbose=True
)

# Task to store important information
store_memory_task = Task(
    description="""
    Store important conversation context about user preferences:
    - User prefers technical explanations
    - User works in healthcare domain
    - User's timezone is EST
    
    Use the memory tool to store this information with agent_id 'user_001'.
    """,
    agent=memory_agent,
    expected_output="Confirmation that user preferences have been stored in memory"
)

# Task to retrieve and use stored memory
retrieve_memory_task = Task(
    description="""
    Retrieve the stored user preferences from memory for agent_id 'user_001' 
    and provide a personalized response based on that information.
    """,
    agent=memory_agent,
    expected_output="Personalized response based on retrieved user preferences"
)

# Create and execute crew
crew = Crew(
    agents=[memory_agent],
    tasks=[store_memory_task, retrieve_memory_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

### Individual Operations

#### 1. Store Memory

```python
# Store a new memory
memory_item = {
    "id": "conversation_001",
    "agent_id": "agent_1", 
    "content": {
        "user_preferences": {
            "communication_style": "technical",
            "domain": "healthcare"
        },
        "conversation_summary": "User asked about AI applications in medical diagnosis"
    },
    "metadata": {
        "importance": "high",
        "category": "user_profile"
    }
}

result = memory_tool._run(
    operation="store",
    memory_item=memory_item,
    ttl=86400  # 24 hours TTL
)
```

#### 2. Retrieve Memories

```python
# Retrieve all memories for an agent
result = memory_tool._run(
    operation="retrieve",
    memory_item={},
    partition_key_value="agent_1",
    max_results=10
)

# Retrieve with filtering
result = memory_tool._run(
    operation="retrieve", 
    memory_item={},
    partition_key_value="agent_1",
    query_filter={"category": "user_profile"},
    max_results=5
)
```

#### 3. Update Memory

```python
# Update existing memory
update_data = {
    "content": {
        "user_preferences": {
            "communication_style": "technical",
            "domain": "healthcare", 
            "preferred_format": "bullet_points"
        }
    },
    "metadata": {
        "last_updated": "2025-01-15T10:30:00Z"
    }
}

result = memory_tool._run(
    operation="update",
    memory_item=update_data,
    partition_key_value="agent_1",
    memory_id="conversation_001"
)
```

#### 4. Delete Memory

```python
# Delete specific memory
result = memory_tool._run(
    operation="delete",
    memory_item={},
    partition_key_value="agent_1", 
    memory_id="conversation_001"
)
```

#### 5. Clear All Memories

```python
# Clear all memories for an agent
result = memory_tool._run(
    operation="clear",
    memory_item={},
    partition_key_value="agent_1"
)
```

### Hierarchical Partition Key Usage

```python
# For hierarchical partition keys (agent_id + session_id)
result = memory_tool._run(
    operation="store",
    memory_item={
        "id": "session_memory_001",
        "agent_id": "agent_1",
        "session_id": "session_123",
        "content": {"session_data": "Important session context"}
    },
    partition_key_value=["agent_1", "session_123"]
)

# Retrieve memories for specific agent and session
result = memory_tool._run(
    operation="retrieve",
    memory_item={},
    partition_key_value=["agent_1", "session_123"]
)
```

## Configuration Options

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `cosmos_host` | CosmosDB account endpoint URL | - | Yes |
| `key` | CosmosDB account key | - | Yes* |
| `token_credential` | Azure token credential | - | Yes* |
| `database_name` | Database name | "memory_database" | No |
| `container_name` | Container name | "memory_container" | No |
| `create_container` | Auto-create container | True | No |
| `cosmos_container_properties` | Container configuration | Single partition key | No |

*Either `key` or `token_credential` must be provided

## Operation Parameters

### Store Operation
- `memory_item` (dict): The memory object to store
- `ttl` (int, optional): Time-to-live in seconds
- `partition_key_value` (str/list, optional): Partition key value(s)

### Retrieve Operation  
- `partition_key_value` (str/list): Partition key value(s)
- `query_filter` (dict, optional): Additional filtering criteria
- `max_results` (int, optional): Maximum number of results (default: 100)

### Update Operation
- `memory_item` (dict): Updated memory data
- `partition_key_value` (str/list): Partition key value(s)
- `memory_id` (str): ID of memory to update
- `ttl` (int, optional): New TTL value

### Delete Operation
- `partition_key_value` (str/list): Partition key value(s) 
- `memory_id` (str): ID of memory to delete

### Clear Operation
- `partition_key_value` (str/list): Partition key value(s)

## Error Handling

The tool provides comprehensive error handling with detailed error messages:

```python
import json

result = memory_tool._run(operation="retrieve", memory_item={})
parsed_result = json.loads(result)

if "error" in parsed_result:
    print(f"Error: {parsed_result['error']}")
    if "details" in parsed_result:
        print(f"Details: {parsed_result['details']}")
else:
    print("Operation successful")
```

## Best Practices

1. **Partition Key Design**: Choose partition keys that distribute data evenly
2. **Memory Structure**: Use consistent JSON structure for better querying
3. **TTL Management**: Set appropriate TTL values to manage storage costs
4. **Error Handling**: Always check for errors in operation results
5. **Batch Operations**: Use clear operation for bulk deletions
6. **Query Optimization**: Use specific filters to limit query scope

## Azure CosmosDB Documentation

- [Azure CosmosDB Overview](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction)
- [NoSQL API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/nosql/)
- [Partition Keys Best Practices](https://docs.microsoft.com/en-us/azure/cosmos-db/partitioning-overview)
- [Time-to-Live (TTL)](https://docs.microsoft.com/en-us/azure/cosmos-db/time-to-live)
- [Hierarchical Partition Keys](https://docs.microsoft.com/en-us/azure/cosmos-db/hierarchical-partition-keys)
- [Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-cosmos/)

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify cosmos_host URL and credentials
2. **Partition Key Errors**: Ensure partition key values match container configuration
3. **Query Timeouts**: Use more specific filters to reduce query scope
4. **Storage Costs**: Implement TTL for automatic cleanup
5. **Authentication Errors**: Verify API key or token credential permissions

### Debug Mode

Enable verbose logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This tool is part of the CrewAI Tools package and follows the same licensing terms.
