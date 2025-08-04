# Klavis MCP Server Tools

## Description

This tool enables CrewAI agents to interact with Klavis MCP (Model Context Protocol) servers, allowing them to automate workflows and integrate with hundreds of applications through Klavis MCP Server. The tool dynamically creates BaseTool instances for each available MCP server tool, making it easy to incorporate external services into your AI workflows.

## Installation

Install the crewai_tools package and the klavis dependency by executing the following command in your terminal:

```shell
uv pip install 'crewai[tools]' klavis
```

## Example

To utilize the KlavisMcpServerTools, you first need to create a Klavis MCP server instance, then use it with CrewAI:

```python
from crewai_tools import KlavisMcpServerTools
from crewai import Agent
from klavis import Klavis
from klavis.types import McpServerName

# Step 1: Create MCP server instance via Klavis
klavis_client = Klavis(api_key="your-klavis-api-key")

mcp_server = klavis_client.mcp_server.create_server_instance(
    server_name=McpServerName.YOUTUBE,  # or other server types
    user_id="123",  # your unique user id
    platform_name="Klavis"  # your platform name
)

# Step 2: Create tools from the MCP server
tools = KlavisMcpServerTools(
    klavis_api_key=api_key,
    mcp_server_url=mcp_server.server_url
)

# Step 3: Use with CrewAI agent
my_agent = Agent(
    role="YouTube Content Analyst",
    tools=tools,
    goal="analyze YouTube videos to extract summaries with timestamps",
    backstory="You are an expert at analyzing video content, extracting transcripts with precise timestamps",
    verbose=True,
)

# Step 4: kick off
result = my_agent.kickoff(
    "Get information about this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)
```

### Optional: Filtering Specific Tools

If you only want to use specific tools from the MCP server:

```python
# Only include specific tools by name
tools = KlavisMcpServerTools(
    klavis_api_key=api_key,
    mcp_server_url=mcp_server.server_url,
    tool_list=["get_video_info", "get_transcript"]  # example tool names
)
```

## Arguments

- `klavis_api_key` : Your Klavis API key for authentication. Can also be set via `KLAVIS_API_KEY` environment variable. (Required)
- `mcp_server_url` : The URL of the Klavis MCP server instance you want to connect to. Can also be set via `KLAVIS_MCP_SERVER_URL` environment variable. (Required)
- `tool_list` : A list of specific tool names to include. If not provided, all available tools from the MCP server will be returned. (Optional)

## Getting Your Klavis API Key

1. Visit [klavis.ai](https://klavis.ai/)
2. Sign up or log in to your account
3. Navigate to API Key
4. Generate or copy your API key

## Available MCP Servers

Klavis supports various enterprise MCP servers that provide different business capabilities:

- **CRM**: Salesforce, Close, Attio, etc. for deal tracking, contact management, sales pipeline analysis
- **GSuite**: Google Workspace integration (Gmail, Drive, Calendar, Sheets, Docs) - requires OAuth
- **Database**: SQL operations, data queries, business intelligence, reporting
- **ERP Systems**: Enterprise resource planning, inventory management, financial reporting
- **And many more**: Check the Klavis documentation for the full list of enterprise integrations
