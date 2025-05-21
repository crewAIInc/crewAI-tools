# MongoDBVectorSearchTool

## Description
This tool is specifically crafted for conducting vector searches within docs within a MongoDB database. Use this tool to find semantically similar docs to a given query.

MongoDB can act as a vector database that is used to store and query vector embeddings. You can follow the docs here: 
https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/

## Installation
Install the crewai_tools package with MongoDB support by executing the following command in your terminal:

```shell
pip install crewai-tools[mongodb]
```

# or

```
uv add crewai-tools --extra mongodb
```

## Example
To utilize the MongoDBVectorSearchTool for different use cases, follow these examples:

```python
from crewai_tools import MongoDBVectorSearchTool

# To enable the tool to search any website the agent comes across or learns about during its operation
tool = MongoDBVectorSearchTool(
    database_name="example_database',
    collection_name='example_collections',
    limit=3,
    connection_string="<your_mongodb_connection_string>",
)

# or 

# Setup custom embedding model and customize the vector search parameters.
tool = MongoDBVectorSearchTool(
    database_name="example_database',
    collection_name='example_collections',
    limit=3,
    index_name="my_vector_index",
    relevance_score_fn="euclidean",
    generative_model="gpt-4o-mini",
    connection_string="<your_mongodb_connection_string>",
)

# Adding the tool to an agent
rag_agent = Agent(
    name="rag_agent",
    role="You are a helpful assistant that can answer questions with the help of the MongoDBVectorSearchTool.",
    llm="gpt-4o-mini",
    tools=[tool],
)
```

## Arguments
- `database_name`: The name of the database to search within. (Required)
- `collection_name` : The name of the collection to search within. (Required)
- `connection_string` : The connection string for the MongoDB clsuter (Required)
- `limit` : The number of results to return. (Optional)
- `generative_model` : The name of the generative model to use. (Optional)

Preloading the Weaviate database with documents:

```python
from crewai_tools import MongoDBVectorSearchTool

# Use before hooks to generate the documents and add them to the MongoDB database
test_docs = client.collections.get("example_collections")

docs_to_load = os.listdir("knowledge")
with test_docs.batch.dynamic() as batch:
    for d in docs_to_load:
        with open(os.path.join("knowledge", d), "r") as f:
            content = f.read()
        batch.add_object(
            {
                "content": content,
                "year": d.split("_")[0],
            }
        )
tool = MongoDBVectorSearchTool(collection_name='example_collections', limit=3)

```
