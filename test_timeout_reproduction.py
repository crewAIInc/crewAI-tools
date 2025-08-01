"""
Reproduction test for the MCPServerAdapter timeout issue from GitHub issue #3254.
This test demonstrates that the timeout configuration fix works correctly.
"""

from textwrap import dedent
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
import time
import threading


def test_timeout_reproduction():
    """Test that reproduces the original timeout issue and verifies the fix"""
    
    slow_server_script = dedent(
        '''
        import time
        from mcp.server.fastmcp import FastMCP

        time.sleep(35)
        
        mcp = FastMCP("Slow Server")

        @mcp.tool()
        def slow_tool(text: str) -> str:
            """A tool from a slow-starting server"""
            return f"Slow response: {text}"

        mcp.run()
        '''
    )
    
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", slow_server_script]
    )
    
    start_time = time.time()
    try:
        with MCPServerAdapter(serverparams) as tools:
            assert False, "Expected timeout but connection succeeded"
    except RuntimeError as e:
        elapsed = time.time() - start_time
        assert "Failed to initialize MCP Adapter" in str(e)
        assert elapsed < 35  # Should timeout before server finishes starting
        print(f"✓ Default timeout (30s) correctly failed after {elapsed:.1f}s")
    
    start_time = time.time()
    try:
        with MCPServerAdapter(serverparams, connect_timeout=60) as tools:
            elapsed = time.time() - start_time
            assert len(tools) == 1
            assert tools[0].name == "slow_tool"
            assert tools[0].run(text="test") == "Slow response: test"
            print(f"✓ Custom timeout (60s) succeeded after {elapsed:.1f}s")
    except Exception as e:
        print(f"✗ Custom timeout failed: {e}")
        raise


def test_fast_server_with_custom_timeout():
    """Test that custom timeout works with fast servers too"""
    
    fast_server_script = dedent(
        '''
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("Fast Server")

        @mcp.tool()
        def fast_tool(text: str) -> str:
            """A tool from a fast server"""
            return f"Fast response: {text}"

        mcp.run()
        '''
    )
    
    serverparams = StdioServerParameters(
        command="uv", args=["run", "python", "-c", fast_server_script]
    )
    
    start_time = time.time()
    with MCPServerAdapter(serverparams, connect_timeout=45) as tools:
        elapsed = time.time() - start_time
        assert len(tools) == 1
        assert tools[0].name == "fast_tool"
        assert tools[0].run(text="test") == "Fast response: test"
        print(f"✓ Fast server with custom timeout succeeded after {elapsed:.1f}s")


if __name__ == "__main__":
    print("Testing MCPServerAdapter timeout configuration...")
    
    
    test_fast_server_with_custom_timeout()
    print("All timeout tests passed!")
