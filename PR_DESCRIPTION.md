# Add Neo4jSearchTool for Semantic Search in Neo4j Graph Databases

## Summary

This PR introduces `Neo4jSearchTool`, a new RAG-based tool that enables semantic search capabilities over Neo4j graph databases. The tool extends the existing `RagTool` infrastructure and follows the same pattern as `MySQLSearchTool` and `PGSearchTool`, providing CrewAI agents with the ability to intelligently query and search graph data using natural language queries.

## What This PR Adds

- **Neo4jSearchTool**: A semantic search tool for Neo4j databases that executes Cypher queries and enables RAG-based search over graph data
- **Neo4jLoader**: A dedicated loader for Neo4j databases that handles Cypher query execution and result formatting
- **DataType.NEO4J**: New data type enum value for Neo4j integration with proper chunker and loader mappings
- **Comprehensive test suite**: Full test coverage with 6 test cases validating initialization, data addition, query execution, and edge cases
- **Documentation**: Complete README.md with usage examples, configuration options, and connection URI formats

## Key Features

✅ **Semantic Search Over Graph Data**: Leverages RAG technology to enable natural language queries over Neo4j graph databases  
✅ **Cypher Query Support**: Executes Cypher queries to extract nodes, relationships, and properties from Neo4j  
✅ **Flexible Connection Options**: Supports Bolt, Neo4j URI, and secure TLS/SSL connection schemes  
✅ **Customizable LLM/Embeddings**: Full support for custom model providers and embedding configurations  
✅ **RAG Integration**: Seamlessly integrates with existing CrewAI RAG infrastructure for vector search and retrieval

## Implementation Details

### Core Components

1. **Neo4jSearchTool** (`crewai_tools/tools/neo4j_search_tool/neo4j_search_tool.py`)
   - Extends `RagTool` class
   - Handles Neo4j connection credentials (URI, user, password)
   - Manages Cypher query execution and semantic search

2. **Neo4jLoader** (`crewai_tools/rag/loaders/neo4j_loader.py`)
   - Implements `BaseLoader` interface
   - Executes Cypher queries using Neo4j Python driver
   - Formats query results into structured text for RAG processing
   - Supports secure connections with optional TLS/SSL

3. **DataType Integration**
   - Added `NEO4J` enum value to `DataType`
   - Configured chunker mapping (uses TextChunker)
   - Configured loader mapping (uses Neo4jLoader)

### Dependencies

- Added `neo4j>=5.0.0` as an optional dependency in `pyproject.toml`
- Import handling with graceful fallback if neo4j package is not installed

## Testing

The PR includes comprehensive test coverage in `tests/tools/test_neo4j_search_tool.py`:

- ✅ Tool initialization with connection parameters
- ✅ Adding data via Cypher queries
- ✅ Running semantic search queries
- ✅ Custom similarity threshold and limit parameters
- ✅ Handling empty/no results scenarios
- ✅ Description generation

All tests pass successfully with mocked Neo4j connections to avoid requiring actual database instances.

## Usage Example

```python
from crewai_tools import Neo4jSearchTool

# Initialize the tool
tool = Neo4jSearchTool(
    neo4j_uri='bolt://localhost:7687',
    neo4j_user='neo4j',
    neo4j_password='your_password'
)

# Add data from a Cypher query
tool.add("MATCH (n:Person)-[:KNOWS]->(f:Person) RETURN n.name as person, f.name as friend")

# Perform semantic search
result = tool._run(
    search_query="Find people who know others",
    similarity_threshold=0.7,
    limit=10
)
```

## Files Changed

### New Files
- `crewai_tools/tools/neo4j_search_tool/neo4j_search_tool.py` - Main tool implementation
- `crewai_tools/tools/neo4j_search_tool/README.md` - Comprehensive documentation
- `crewai_tools/rag/loaders/neo4j_loader.py` - Neo4j database loader
- `tests/tools/test_neo4j_search_tool.py` - Test suite

### Modified Files
- `crewai_tools/rag/data_types.py` - Added NEO4J data type enum
- `crewai_tools/__init__.py` - Added Neo4jSearchTool export
- `crewai_tools/tools/__init__.py` - Added Neo4jSearchTool import
- `pyproject.toml` - Added neo4j optional dependency

## Benefits

1. **Extends Database Tool Support**: Adds graph database support alongside existing relational database tools (MySQL, PostgreSQL)
2. **Semantic Search for Graphs**: Enables intelligent querying of graph data using natural language, not just structured Cypher queries
3. **Consistent API**: Follows the same patterns as existing database search tools for easy adoption
4. **Production Ready**: Includes error handling, secure connection support, and comprehensive testing

## Compatibility

- ✅ Backward compatible - No breaking changes to existing functionality
- ✅ Follows existing patterns - Consistent with MySQLSearchTool and PGSearchTool
- ✅ Optional dependency - Neo4j support requires explicit installation (`pip install neo4j` or `pip install 'crewai-tools[neo4j]'`)

## Testing Instructions

```bash
# Install test dependencies
pip install neo4j pytest

# Run tests
pytest tests/tools/test_neo4j_search_tool.py -v
```

All 6 tests should pass.

