from __future__ import annotations

"""
MCPServer for CrewAI.


"""

from typing import Any, TYPE_CHECKING

from crewai.tools import BaseTool

if TYPE_CHECKING:
    from mcp import StdioServerParameters
    from mcpadapt.core import MCPAdapt
    from mcpadapt.crewai_adapter import CrewAIAdapter


try:
    import mcp
    import mcpadapt.core
    import mcpadapt.crewai_adapter
except ImportError:
    raise ImportError(
        "MCP needs optional dependencies to be installed, run `uv add crewai-tools[mcp]`"
    )


class MCPServerAdapter:
    """Manages the lifecycle of an MCP server and make its tools available to CrewAI.

    Note: tools can only be accessed after the server has been started with the
        `start()` method.

    Attributes:
        tools: The CrewAI tools available from the MCP server.

    Usage:
        # context manager + stdio
        with MCPServerAdapter(...) as tools:
            # tools is now available

        # context manager + sse
        with MCPServerAdapter({"url": "http://localhost:8000/sse"}) as tools:
            # tools is now available

        # manually stop mcp server
        try:
            mcp_server = MCPServerAdapter(...)
            tools = mcp_server.tools
            mcp_server.stop()
        except Exception as e:
            print(e)
            mcp_server.stop()
            raise e

        # Best practice is ensure cleanup is done after use.
        mcp_server.stop() # run after crew().kickoff()
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
        self._adapter = mcpadapt.core.MCPAdapt(
            self._serverparams, mcpadapt.crewai_adapter.CrewAIAdapter()
        )
        self._tools = None
        self.start()

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
