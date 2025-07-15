from textwrap import dedent

import pytest

from crewai_tools import MCPServerAdapter
from crewai_tools.adapters.tool_collection import ToolCollection

try:
    from mcp import StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    class StdioServerParameters:
        def __init__(self, **kwargs):
            pass

@pytest.fixture
def echo_server_script():
    return dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server")

        @mcp.tool()
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"

        @mcp.tool()
        def calc_tool(a: int, b: int) -> int:
            """Calculate a + b"""
            return a + b

        mcp.run()
        '''
    )


@pytest.fixture
def echo_server_sse_script():
    return dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server", host="127.0.0.1", port=8000)

        @mcp.tool()
        def echo_tool(text: str) -> str:
            """Echo the input text"""
            return f"Echo: {text}"

        @mcp.tool()
        def calc_tool(a: int, b: int) -> int:
            """Calculate a + b"""
            return a + b

        mcp.run("sse")
        '''
    )


@pytest.fixture
def echo_sse_server(echo_server_sse_script):
    import subprocess
    import time

    # Start the SSE server process with its own process group
    process = subprocess.Popen(
        ["python", "-c", echo_server_sse_script],
    )

    # Give the server a moment to start up
    time.sleep(1)

    try:
        yield {"url": "http://127.0.0.1:8000/sse"}
    finally:
        # Clean up the process when test is done
        process.kill()
        process.wait()


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_context_manager_syntax(echo_server_script):
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams) as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == '8'

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_context_manager_syntax_sse(echo_sse_server):
    sse_serverparams = echo_sse_server
    with MCPServerAdapter(sse_serverparams) as tools:
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == '8'

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_try_finally_syntax(echo_server_script):
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == '8'
    finally:
        mcp_server_adapter.stop()

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_try_finally_syntax_sse(echo_sse_server):
    sse_serverparams = echo_sse_server
    mcp_server_adapter = MCPServerAdapter(sse_serverparams)
    try:
        tools = mcp_server_adapter.tools
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == '8'
    finally:
        mcp_server_adapter.stop()

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_context_manager_with_filtered_tools(echo_server_script):
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    # Only select the echo_tool
    with MCPServerAdapter(serverparams, "echo_tool") as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        # Check that calc_tool is not present
        with pytest.raises(IndexError):
            _ = tools[1]
        with pytest.raises(KeyError):
            _ = tools["calc_tool"]

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_context_manager_sse_with_filtered_tools(echo_sse_server):
    sse_serverparams = echo_sse_server
    # Only select the calc_tool
    with MCPServerAdapter(sse_serverparams, "calc_tool") as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 1
        assert tools[0].name == "calc_tool"
        assert tools[0].run(a=10, b=5) == '15'
        # Check that echo_tool is not present
        with pytest.raises(IndexError):
            _ = tools[1]
        with pytest.raises(KeyError):
            _ = tools["echo_tool"]

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_try_finally_with_filtered_tools(echo_server_script):
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    try:
        # Select both tools but in reverse order
        mcp_server_adapter = MCPServerAdapter(serverparams, "calc_tool", "echo_tool")
        tools = mcp_server_adapter.tools
        assert len(tools) == 2
        # The order of tools is based on filter_by_names which preserves
        # the original order from the collection
        assert tools[0].name == "calc_tool"
        assert tools[1].name == "echo_tool"
    finally:
        mcp_server_adapter.stop()

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_filter_with_nonexistent_tool(echo_server_script):
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    # Include a tool that doesn't exist
    with MCPServerAdapter(serverparams, "echo_tool", "nonexistent_tool") as tools:
        # Only echo_tool should be in the result
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"

@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not available")
def test_filter_with_only_nonexistent_tools(echo_server_script):
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    # All requested tools don't exist
    with MCPServerAdapter(serverparams, "nonexistent1", "nonexistent2") as tools:
        # Should return an empty tool collection
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 0


def test_mcp_adapter_missing_dependency():
    """Test that MCPServerAdapter raises ImportError when mcp package is missing."""
    from unittest.mock import patch
    
    with patch('crewai_tools.adapters.mcp_adapter.MCP_AVAILABLE', False):
        with pytest.raises(ImportError, match="`mcp` package not found, please run `uv add crewai-tools\\[mcp\\]`"):
            MCPServerAdapter({"url": "http://localhost:8000/sse"})


def test_mcp_adapter_missing_dependency_stdio():
    """Test that MCPServerAdapter raises ImportError for stdio params when mcp package is missing."""
    from unittest.mock import patch, MagicMock
    
    with patch('crewai_tools.adapters.mcp_adapter.MCP_AVAILABLE', False):
        mock_params = MagicMock()
        with pytest.raises(ImportError, match="`mcp` package not found, please run `uv add crewai-tools\\[mcp\\]`"):
            MCPServerAdapter(mock_params)
