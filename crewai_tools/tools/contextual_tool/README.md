# ContextualTool Documentation

## Description
This tool is designed to integrate Contextual AI's enterprise-grade RAG agents with CrewAI, enabling you to leverage Contextual AI's powerful document parsing, vector storage, and grounded language models as tools for your CrewAI agents. With this integration, you can create specialized RAG agents that have exceptional accuracy and scalability for answering questions and completing tasks based on your documents and data.

## Installation
To incorporate this tool into your project, follow the installation instructions below:

```shell
pip install 'crewai[tools]' contextual-client
```

**Note**: You'll also need a Contextual AI API key. Sign up at [app.contextual.ai](https://app.contextual.ai) to get your free API key with $25 in credits.

## Example

The following examples demonstrate how to initialize the tool in different scenarios:

### Example 1: Using an Existing Agent
If you already have a Contextual AI agent set up:

```python
from crewai_tools import ContextualTool

# Initialize the tool from an existing agent
tool = ContextualTool.from_existing_agent(
    api_key="your_api_key_here",
    agent_id="your_agent_id_here"
)

# Try a simple query
result = tool._run("your_query_here?")
print("Result:", result)
```

### Example 2: Creating a New Agent with Existing Datastore
If you have documents already uploaded to a Contextual AI datastore:

```python
from crewai_tools import ContextualTool

# Create a new agent using an existing datastore
tool = ContextualTool.from_existing_datastore(
    api_key="your_api_key_here",
    datastore_id="your_datastore_id_here",
    agent_name="Financial Analysis Agent",
    agent_description="Specialized agent for financial document analysis",
    name="Financial RAG Tool",
    description="Query financial documents and reports"
)
```

### Example 3: Complete Setup with Document Upload
Create everything from scratch - datastore, upload documents, and create agent:

```python
from crewai_tools import ContextualTool

# Create a complete RAG pipeline
tool = ContextualTool.create_with_documents(
    api_key="your_api_key_here",
    agent_name="Company Knowledge Agent",
    agent_description="Agent with access to company policies and procedures",
    datastore_name="Company Documents",
    document_paths=[
        "/path/to/employee_handbook.pdf",
        "/path/to/company_policies.pdf",
        "/path/to/procedures_manual.pdf"
    ],
    name="Company Knowledge Tool",
    description="Query company policies and procedures"
)

# After processing is completed, try a query
# To check processing status, see Example 5
result = tool._run("What is the company computer policy?")
print("Agent ID:", tool.agent_id)
print("Datastore ID:", tool.datastore_id)
print("Result:", result)
```

### Example 4: Using with CrewAI Agents
Integrate the Contextual RAG tool with your CrewAI agents:

```python
import os
os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'

from crewai import Agent, Task, Crew
from crewai_tools import ContextualTool

# Create the Contextual AI tool
rag_tool = ContextualTool.from_existing_agent(
    api_key="your_api_key_here",
    agent_id="your_agent_id_here"
)

# Create a CrewAI agent with the tool
analyst = Agent(
    role="Research Analyst",
    goal="Analyze documents and provide insights",
    backstory="You are a skilled analyst with access to a comprehensive knowledge base.",
    tools=[rag_tool],
    verbose=True
)

# Create a task
research_task = Task(
    description="Research the company's revenue trends over the past 3 years",
    expected_output="A detailed analysis of revenue trends with key insights",
    agent=analyst
)

# Create and run the crew
crew = Crew(
    agents=[analyst],
    tasks=[research_task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

### Example 5: Managing Documents
Upload additional documents and check status:

```python
# Upload additional documents to existing tool
document_ids = tool.upload_additional_documents([
    "/path/to/new_report.pdf",
    "/path/to/latest_data.xlsx"
])

# Check document processing status
status = tool.get_document_status("your_document_id_here")
print("Document processing status:", status)
```

## Steps to Get Started

To effectively use the `ContextualTool`, follow these steps:

1. **Get API Access**: 
   - Sign up at [app.contextual.ai](https://app.contextual.ai)
   - Create an API key from the dashboard
   - New workspaces get $25 in free credits

2. **Install Dependencies**: 
   ```shell
   pip install 'crewai[tools]' contextual
   ```

3. **Prepare Your Documents**: 
   - Gather the documents you want to use (PDFs work best)
   - Ensure they are readable/copyable text (not scanned images)

4. **Choose Your Integration Method**:
   - Use `from_existing_agent()` if you already have a Contextual AI agent
   - Use `from_existing_datastore()` if you have documents uploaded but need a new agent
   - Use `create_with_documents()` for a complete setup from scratch

5. **Test Your Tool**:
   ```python
   # Test the tool directly
   result = tool._run("What is the main topic of the uploaded documents?")
   print(result)
   ```

6. **Integrate with CrewAI**: Add the tool to your CrewAI agents and tasks

## Key Features

- **Powerful Parsing**: Contextual AI's advanced document parsing handles complex PDFs, tables, and layouts
- **Grounded Responses**: Built-in grounding to ensure factual, source-attributed answers
- **Scalable**: Handle large document collections with optimized chunking and storage
- **Multiple Input Formats**: Support for PDFs, Word documents, text files, and more
- **Flexible Integration**: Multiple initialization patterns to fit your workflow

## Best Practices

- **Document Quality**: Use text-based PDFs rather than scanned images for best results
- **Descriptive Names**: Give your agents and datastores descriptive names for easier management
- **Test Queries**: Start with simple queries to verify your setup before complex tasks
- **Iterative Improvement**: Add relevant documents based on query patterns and gaps

For more detailed information about Contextual AI's capabilities, visit the [official documentation](https://docs.contextual.ai).
