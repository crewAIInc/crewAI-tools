from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Type

from crewai.tools import BaseTool
from crewai_tools.adapters.tool_collection import ToolCollection

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from mcp import StdioServerParameters
    from mcpadapt.core import MCPAdapt
    from mcpadapt.crewai_adapter import CrewAIAdapter


try:
    from mcp import StdioServerParameters
    from mcpadapt.core import MCPAdapt
    from mcpadapt.crewai_adapter import CrewAIAdapter

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class MCPServerAdapter:
    """Manages the lifecycle of an MCP server and makes its tools available to CrewAI.

    This adapter handles starting and stopping the MCP server, converting its
    capabilities into CrewAI tools. It is best used as a context manager (`with`
    statement) to ensure resources are properly cleaned up.

    Attributes:
        tools: A ToolCollection of the available CrewAI tools. Accessing this
            before the server is ready will raise a ValueError.
    """

    def __init__(
        self,
        serverparams: StdioServerParameters | dict[str, Any],
        *tool_names: str,
        connect_timeout: int = 30,
    ) -> None:
        """Initialize and start the MCP Server.

        Example:
            .. code-block:: python

                # For a server communicating over standard I/O
                from mcp import StdioServerParameters
                stdio_params = StdioServerParameters(command="python", args=["-c", "..."])
                with MCPServerAdapter(stdio_params) as tools:
                    # use tools

                # For a server communicating over SSE (Server-Sent Events)
                sse_params = {"url": "http://localhost:8000/sse"}
                with MCPServerAdapter(sse_params, connect_timeout=60) as tools:
                    # use tools

        Args:
            serverparams: The parameters for the MCP server. This supports either a
                `StdioServerParameters` object for STDIO or a `dict` for SSE connections.
            *tool_names: Optional names of tools to filter. If provided, only tools with
                matching names will be available.
            connect_timeout: Connection timeout in seconds to the MCP server.
                Defaults to 30.
        """
        self._adapter = None
        self._tools = None
        self._tool_names = list(tool_names) if tool_names else None

        if not MCP_AVAILABLE:
            msg = (
                "MCP is not available. The 'mcp' package, a required dependency, "
                "must be installed for MCPServerAdapter to work."
            )
            logger.critical(msg)
            raise ImportError(
                "`mcp` package not found. Please install it with:\n"
                "  pip install mcp crewai-tools[mcp]"
            )

        try:
            self._serverparams = serverparams
            self._adapter = MCPAdapt(self._serverparams, CrewAIAdapter(), connect_timeout)
            self.start()
        except Exception as e:
            logger.exception("Failed to initialize MCP Adapter during __init__.")
            if self._adapter is not None:
                try:
                    self.stop()
                except Exception as stop_e:
                    logger.error(f"Error during post-failure cleanup: {stop_e}")
            raise RuntimeError(f"Failed to initialize MCP Adapter: {e}") from e

    def start(self) -> None:
        """Start the MCP server and initialize the tools."""
        if not self._adapter:
            raise RuntimeError("Cannot start MCP server: Adapter is not initialized.")
        if self._tools:
            logger.debug("MCP server already started.")
            return
        self._tools = self._adapter.__enter__()

    def stop(self) -> None:
        """Stop the MCP server and release all associated resources.

        This method is idempotent; calling it multiple times has no effect.
        """
        if not self._adapter:
            logger.debug("stop() called but adapter is already stopped.")
            return

        try:
            self._adapter.__exit__(None, None, None)
        finally:
            self._tools = None
            self._adapter = None

    @property
    def tools(self) -> ToolCollection[BaseTool]:
        """The CrewAI tools available from the MCP server.

        Raises:
            ValueError: If the MCP server is not started.

        Returns:
            A ToolCollection of the available CrewAI tools.
        """
        if self._tools is None:
            raise ValueError(
                "MCP tools are not available. The server may be stopped or initialization failed."
            )

        tools_collection = ToolCollection(self._tools)
        if self._tool_names:
            return tools_collection.filter_by_names(self._tool_names)
        return tools_collection

    def __enter__(self) -> ToolCollection[BaseTool]:
        """Enter the context manager, returning the initialized tools."""
        return self.tools

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> bool:
        """Exit the context manager, stop the server, and do not suppress exceptions."""
        self.stop()
        return False  # Ensures any exceptions that occurred are re-raised.

    def __del__(self) -> None:
        """
        Finalizer to attempt cleanup if the user forgets to call stop() or use a
        context manager.

        Note: This is a fallback and should not be relied upon, as Python does
        not guarantee __del__ will always be called on object destruction.
        """
        if self._adapter:
            logger.warning(
                "MCPServerAdapter was not cleanly shut down. Please use a "
                "context manager (`with` statement) or call .stop() explicitly."
            )
            self.stop()
