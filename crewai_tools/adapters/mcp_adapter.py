import os
from contextlib import AsyncExitStack
from typing import Optional, List, Type, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, ConfigDict, create_model
import logging
import asyncio
from mcp.types import (
    Tool as MCPTool,
)
from anthropic import Anthropic
from crewai import Agent, Task, Crew, Process

try:
    from mcp import (
        ClientSession,
        StdioServerParameters,
    )

    from mcp.client.stdio import stdio_client

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

DEFAULT_ENCODING = "utf-8"
DEFAULT_ENCODING_ERROR_HANDLER = "strict"
DEFAULT_MAX_TOKENS = 1000

logger = logging.getLogger(__name__)


class McpServerAdapterSchema(BaseModel):
    """Input schema for McpServerAdapterTool."""

    query_passed: str = Field(..., description="The query to send to the MCP server")


class McpServerAdapter:
    available_tools: List[MCPTool] = []

    def __init__(self, command: str, args: list, env: Optional[dict] = None):
        self._session = None
        self._exit_stack = None
        self._command = command
        self._args = args
        self._env = env or {}
        self.anthropic = Anthropic()

        # Ensure PATH is passed through
        if "PATH" not in self._env:
            self._env["PATH"] = os.environ["PATH"]

    async def initialize(self):
        """Initialize the session if not already initialized"""
        if self._session is None:
            try:
                self._exit_stack = AsyncExitStack()

                # Create server parameters
                server_params = StdioServerParameters(
                    command=self._command, args=self._args, env=self._env
                )

                # Initialize connection using stdio_client
                stdio_transport = await self._exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                stdio, write = stdio_transport

                # Create and initialize session
                self._session = await self._exit_stack.enter_async_context(
                    ClientSession(stdio, write)
                )
                await self._session.initialize()

                # Test connection with list_tools
                response = await self._session.list_tools()
                print(
                    f"Connected to server with tools: {[tool.name for tool in response.tools]}"
                )
                self.available_tools = response.tools
                return response.tools

            except Exception as e:
                logger.error(f"Failed to initialize MCP session: {e}")
                if self._exit_stack:
                    await self._cleanup()
                raise

    async def _cleanup(self):
        """Cleanup resources"""
        if self._exit_stack:
            try:
                await self._exit_stack.aclose()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self._exit_stack = None
                self._session = None

    def _create_tool_schema(self, mcp_tool: MCPTool) -> Type[BaseModel]:
        """Dynamically create a Pydantic model from MCP tool's input schema"""
        print(f"\nOriginal MCP tool schema for {mcp_tool.name}:", mcp_tool.inputSchema)

        # Create field definitions for the model
        field_definitions = {}
        properties = mcp_tool.inputSchema.get("properties", {})
        required = mcp_tool.inputSchema.get("required", [])

        # Map JSON schema types to Python types
        type_mapping = {
            "string": str,
            "object": dict,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
        }
        print("properties", properties.items())
        # Create fields from the properties
        for prop_name, prop_details in properties.items():
            print("prop_details", prop_details)
            print("prop_name", prop_name)
            field_type = prop_details.get("type", "string")
            python_type = type_mapping.get(field_type, str)

            # Create a field with the appropriate type and required status
            field_definitions[prop_name] = (
                python_type,
                Field(
                    ... if prop_name in required else None,
                    title=prop_details.get("title", prop_name),
                    description=prop_details.get("description"),
                ),
            )
        print("field_definitions", field_definitions)
        # Create the model using create_model
        schema = create_model(
            f"{mcp_tool.name}Schema",
            **field_definitions,
            __config__=ConfigDict(extra="allow"),
        )

        print(f"Created schema for {mcp_tool.name}:", schema)
        print(f"Created schema for {mcp_tool.name}:", schema.__annotations__)
        return schema

    def _create_tool_from_mcp(self, mcp_tool: MCPTool) -> BaseTool:
        """Convert a single MCP tool to a CrewAI BaseTool"""
        # Create schemas and descriptions
        # tool_args_desc = {}
        # for prop_name, prop_details in mcp_tool.inputSchema.get(
        #     "properties", {}
        # ).items():
        #     tool_args_desc[prop_name] = {
        #         "type": "str" if prop_details.get("type") == "string" else "dict",
        #         "description": prop_details.get("description"),
        #     }

        tool_description = f"""{mcp_tool.description or ""}

        Tool Arguments: {mcp_tool.inputSchema}"""  # Use the entire inputSchema

        def _run(**kwargs):
            # print(f"Running {mcp_tool.name} with args:", tool_args_desc)
            # tool_input = {key: kwargs[key] for key in kwargs if key in tool_args_desc}
            print(f"Running {mcp_tool.name} with args:", kwargs)

            result = asyncio.run(self._session.call_tool(mcp_tool.name, kwargs))
            print("called result:", result)
            return result
            # return f"Tool {mcp_tool.name} executed with args: {kwargs}"

        # Create simple schema with common fields
        class SimpleSchema(BaseModel):
            query: Optional[str] = Field(None, description="Search query")
            information: Optional[str] = Field(None, description="Information to store")
            metadata: Optional[dict] = Field(None, description="Additional metadata")

            model_config = ConfigDict(extra="allow")  # Allow extra fields

        # Create the tool class
        class DynamicTool(BaseTool):
            name: str = mcp_tool.name
            description: str = tool_description
            args_schema: Type[BaseModel] = SimpleSchema

            def _run(self, **kwargs) -> Any:
                return _run(**kwargs)

            async def _arun(self, **kwargs) -> Any:
                return _run(**kwargs)  # Call the sync version for simplicity

        # Return the tool instance
        tool = DynamicTool()
        print(f"Created tool {tool.name}", tool._run)
        return tool


class McpServerTool(BaseTool):
    """Tool for interacting with MCP servers"""

    name: str = "MCP Server Tool"
    description: str = "Connects to and interacts with MCP servers to execute queries"
    args_schema: Type[BaseModel] = McpServerAdapterSchema

    def __init__(
        self,
        command: str,
        args: List[str],
        env: Optional[dict[str, str]] = None,
    ):
        """Initialize the MCP Server Tool with configuration"""
        super().__init__()
        self._command = command
        self._args = args
        self._env = env or {}
        self._adapter = McpServerAdapter(
            command=self._command, args=self._args, env=self._env
        )

    async def get_available_tools(self) -> List[BaseTool]:
        """Get all available tools from the MCP server as CrewAI tools"""
        await self._adapter.initialize()
        print("available tools", self._adapter.available_tools)
        return [
            self._adapter._create_tool_from_mcp(tool)
            for tool in self._adapter.available_tools
        ]

    def _run(self, query: str) -> str:
        """Execute a query against an MCP server"""
        self._adapter.initialize()

        async def _execute():
            try:
                return await self.get_available_tools()
            finally:
                await self._adapter._cleanup()

        return asyncio.run(_execute())

    async def _arun(self, query: str) -> str:
        """Async version of _run"""
        try:
            return await self.get_available_tools()
        finally:
            await self._adapter._cleanup()

    def __del__(self):
        """No need for cleanup in __del__ as it's handled after each query"""
        pass


if __name__ == "__main__":
    # Example for Qdrant server
    mcp_tool = McpServerTool(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/Users/lorenzejay/workspace/crewAI-tools",
        ],
    )

    # Get the actual tools from the MCP server
    available_tools = asyncio.run(mcp_tool.get_available_tools())

    agent = Agent(
        role="You are a helpful assistant that can use the available tools to answer query with description of: {description}",
        goal="Answer the question using the appropriate tool",
        backstory="You are a helpful assistant with access to various tools",
        tools=available_tools,  # Use the actual MCP tools
        verbose=True,
        llm="gpt-4o",
    )

    task = Task(
        description="answer the question using the appropriate tool: {description}.",
        expected_output="An answer to the question: {description}",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    res = crew.kickoff(
        inputs={"description": "tell me about the files inside the directory?"}
    )
    print("res", res)
