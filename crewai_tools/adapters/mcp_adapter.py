"""
MCPServer for CrewAI.


"""
from typing import Any

from crewai.tools import BaseTool

try:
    from mcp import (
        StdioServerParameters,
    )
    from mcpadapt.core import MCPAdapt
    from mcpadapt.crewai_adapter import CrewAIAdapter
except ImportError:
    raise ImportError(
        "MCP needs optional dependencies to be installed, run `pip install crewai-tools[mcp]`"
    )


class MCPServer:
    """Manages the lifecycle of an MCP server and make its tools available to CrewAI.
    
    Note: tools can only be accessed after the server has been started with the 
        `start()` method.

    Attributes:
        tools: The CrewAI tools available from the MCP server.

    Usage:
        # context manager + stdio
        with MCPServer(StdioServerParameters(...)) as tools:
            # tools is now available

        # context manager + sse
        with MCPServer({"url": "http://localhost:8000/sse"}) as tools:
            # tools is now available
        
        # manually start / stop mcp server
        mcp_server = MCPServer(StdioServerParameters(...))
        mcp_server.start()
        tools = mcp_server.tools
        mcp_server.stop()
    """
    def __init__(
        self,
        serverparams: StdioServerParameters | dict[str, Any],
    ):
        """Initialize the MCP Server
        
        Args:
            serverparams: The parameters for the MCP server it supports either a 
                `StdioServerParameters` or a `dict` respectively for STDIO and SSE.

        """
        super().__init__()
        self._serverparams = serverparams
        self._adapter = MCPAdapt(self._serverparams, CrewAIAdapter())
        self._tools = None

    def start(self):
        """Start the MCP server and initialize the tools."""
        self._tools = self._adapter.__enter__()

    def stop(self):
        """Stop the MCP server"""
        self._adapter.__exit__(None, None, None)

    @property
    def tools(self) -> list[BaseTool]:
        """The CrewAI tools available from the MCP server.
        
        Raises:
            ValueError: If the MCP server is not started.

        Returns:
            The CrewAI tools available from the MCP server.
        """
        if self._tools is None:
            raise ValueError(
                "MCP server not started, run `mcp_server.start()` first before accessing `tools`"
            )
        return self._tools

    def __enter__(self):
        """Enter the context manager."""
        return self._adapter.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager."""
        return self._adapter.__exit__(exc_type, exc_value, traceback)


if __name__ == "__main__":
    from textwrap import dedent

    # Example for Echo server
    echo_server_script = dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server")

        @mcp.tool()
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"
        
        mcp.run()
        '''
    )

    mcp_server = MCPServer(
        StdioServerParameters(
            command="uv",
            args=[
                "run",
                "python",
                "-c",
                echo_server_script,
            ],
        )
    )

    # option 1: start the server and get the available tools
    mcp_server.start()

    print(mcp_server.tools)

    echo_tool = mcp_server.tools[0]

    print(echo_tool)
    print(echo_tool.name)
    print(echo_tool.run(text="Hello"))

    mcp_server.stop()

    # option 2: with context manager
    with MCPServer(
        StdioServerParameters(
            command="uv",
            args=[
                "run",
                "python",
                "-c",
                echo_server_script,
            ],
        )
    ) as tools:
        echo_tool = tools[0]
        print(echo_tool.name)
        print(echo_tool.run(text="Hello"))
