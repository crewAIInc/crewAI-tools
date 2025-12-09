from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest
from mcp import StdioServerParameters

from crewai_tools import MCPServerAdapter
from crewai_tools.adapters.tool_collection import ToolCollection


@pytest.fixture
def echo_server_script() -> str:
    return dedent(
        """
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server")

        @mcp.tool()
        def echo_tool(text: str) -> str:
            \"\"\"Echo the input text\"\"\"
            return f"Echo: {text}"

        @mcp.tool()
        def calc_tool(a: int, b: int) -> int:
            \"\"\"Calculate a + b\"\"\"
            return a + b

        mcp.run()
        """
    )


@pytest.fixture
def echo_server_sse_script() -> str:
    return dedent(
        """
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Echo Server", host="127.0.0.1", port=8000)

        @mcp.tool()
        def echo_tool(text: str) -> str:
            \"\"\"Echo the input text\"\"\"
            return f"Echo: {text}"

        @mcp.tool()
        def calc_tool(a: int, b: int) -> int:
            \"\"\"Calculate a + b\"\"\"
            return a + b

        mcp.run("sse")
        """
    )


@pytest.fixture
def echo_sse_server(echo_server_sse_script: str):
    import subprocess
    import time

    process = subprocess.Popen(
        ["python", "-c", echo_server_sse_script],
    )

    time.sleep(1)

    try:
        yield {"url": "http://127.0.0.1:8000/sse"}
    finally:
        process.kill()
        process.wait()


def test_context_manager_syntax(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="python", args=["-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams) as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == "8"


def test_context_manager_syntax_sse(echo_sse_server) -> None:
    sse_serverparams = echo_sse_server
    with MCPServerAdapter(sse_serverparams) as tools:
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == "8"


def test_try_finally_syntax(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="python", args=["-c", echo_server_script]
    )
    mcp_server_adapter = None
    try:
        mcp_server_adapter = MCPServerAdapter(serverparams)
        tools = mcp_server_adapter.tools
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == "8"
    finally:
        if mcp_server_adapter:
            mcp_server_adapter.stop()


def test_try_finally_syntax_sse(echo_sse_server) -> None:
    sse_serverparams = echo_sse_server
    mcp_server_adapter = MCPServerAdapter(sse_serverparams)
    try:
        tools = mcp_server_adapter.tools
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        assert tools[1].run(a=5, b=3) == "8"
    finally:
        mcp_server_adapter.stop()


def test_context_manager_with_filtered_tools(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="python", args=["-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams, "echo_tool") as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"
        assert tools[0].run(text="hello") == "Echo: hello"
        with pytest.raises(IndexError):
            _ = tools[1]
        with pytest.raises(KeyError):
            _ = tools["calc_tool"]


def test_context_manager_sse_with_filtered_tools(echo_sse_server) -> None:
    sse_serverparams = echo_sse_server
    with MCPServerAdapter(sse_serverparams, "calc_tool") as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 1
        assert tools[0].name == "calc_tool"
        assert tools[0].run(a=10, b=5) == "15"
        with pytest.raises(IndexError):
            _ = tools[1]
        with pytest.raises(KeyError):
            _ = tools["echo_tool"]


def test_try_finally_with_filtered_tools(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="python", args=["-c", echo_server_script]
    )
    mcp_server_adapter = None
    try:
        mcp_server_adapter = MCPServerAdapter(serverparams, "calc_tool", "echo_tool")
        tools = mcp_server_adapter.tools
        assert len(tools) == 2
        assert tools[0].name == "calc_tool"
        assert tools[1].name == "echo_tool"
    finally:
        if mcp_server_adapter:
            mcp_server_adapter.stop()


def test_filter_with_nonexistent_tool(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="python", args=["-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams, "echo_tool", "nonexistent_tool") as tools:
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"


def test_filter_with_only_nonexistent_tools(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="python", args=["-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams, "nonexistent1", "nonexistent2") as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 0


def test_adapter_raises_import_error_if_mcp_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests that MCPServerAdapter raises ImportError if the mcp package is not available.
    """
    monkeypatch.setattr("crewai_tools.adapters.mcp_adapter.MCP_AVAILABLE", False)
    with pytest.raises(ImportError, match="`mcp` package not found"):
        MCPServerAdapter(serverparams={})


def test_connect_timeout_parameter(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams, connect_timeout=60) as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 2
        assert tools[0].name == "echo_tool"
        assert tools[1].name == "calc_tool"
        assert tools[0].run(text="hello") == "Echo: hello"

def test_connect_timeout_with_filtered_tools(echo_server_script: str) -> None:
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", echo_server_script]
    )
    with MCPServerAdapter(serverparams, "echo_tool", connect_timeout=45) as tools:
        assert isinstance(tools, ToolCollection)
        assert len(tools) == 1
        assert tools[0].name == "echo_tool"
        assert tools[0].run(text="timeout test") == "Echo: timeout test"

@patch("crewai_tools.adapters.mcp_adapter.MCPAdapt")
def test_connect_timeout_passed_to_mcpadapt(mock_mcpadapt: MagicMock) -> None:
    mock_adapter_instance = MagicMock()
    mock_mcpadapt.return_value = mock_adapter_instance

    serverparams = StdioServerParameters(
        command="uv", args=["run", "echo", "test"]
    )

    MCPServerAdapter(serverparams)
    mock_mcpadapt.assert_called_once()
    assert mock_mcpadapt.call_args[0][2] == 30

    mock_mcpadapt.reset_mock()

    MCPServerAdapter(serverparams, connect_timeout=5)
    mock_mcpadapt.assert_called_once()
    assert mock_mcpadapt.call_args[0][2] == 5
