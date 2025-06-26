import os
import logging
from typing import List, Optional, Any, Dict

from crewai.tools import BaseTool
from pydantic import Field, create_model

logger = logging.getLogger(__name__)


class KlavisMcpServerTool(BaseTool):
    """
    A tool that wraps a Klavis MCP server tool
    """

    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    klavis_client: Any = Field(description="Klavis client instance")
    server_url: str = Field(description="MCP server URL")

    class Config:
        arbitrary_types_allowed = True

    def _run(self, **kwargs) -> str:
        """Execute the Klavis MCP server tool"""
        try:
            result = self.klavis_client.mcp_server.call_tools(
                server_url=self.server_url,
                tool_name=self.name,
                tool_args=kwargs
            )
            return str(result)
        except Exception as e:
            logger.error(f"Error executing Klavis tool {self.name}: {str(e)}")
            raise e


class KlavisMcpServerAdapter:
    """
    Adapter for Klavis MCP Server Tools
    """

    def __init__(self, klavis_api_key: str, mcp_server_url: str):
        try:
            from klavis import Klavis
        except ImportError:
            raise ImportError("klavis package is required. Install it with: pip install klavis")
        
        self.klavis_api_key = klavis_api_key
        self.mcp_server_url = mcp_server_url
        
        if not self.klavis_api_key:
            logger.error("Klavis API key is required")
            raise ValueError("Klavis API key is required")
        
        if not self.mcp_server_url:
            logger.error("MCP server URL is required")
            raise ValueError("MCP server URL is required")
            
        self.klavis_client = Klavis(api_key=self.klavis_api_key)

    def get_tools_from_mcp_server(self):
        """Get available tools from the MCP server"""
        try:          
            response = self.klavis_client.mcp_server.list_tools(
                server_url=self.mcp_server_url
            )
            return response.tools
        except Exception as e:
            logger.error(f"Error fetching Klavis tools: {str(e)}")
            raise e

    def tools(self) -> List[BaseTool]:
        """Convert to CrewAI BaseTool instances"""
        tools_response = self.get_tools_from_mcp_server()
        tools = []

        print(tools_response)
        for tool_spec in tools_response:
            tool = KlavisMcpServerTool(
                name=tool_spec["name"],
                description=tool_spec["description"],
                klavis_client=self.klavis_client,
                server_url=self.mcp_server_url
            )
            tools.append(tool)

        return tools


def KlavisMcpServerTools(
    klavis_api_key: Optional[str] = None, 
    mcp_server_url: Optional[str] = None,
    tool_list: Optional[List[str]] = None
) -> List[BaseTool]:
    """Factory function that returns tools from Klavis MCP server.

    Args:
        klavis_api_key: The API key for Klavis.
        mcp_server_url: The URL of the MCP server to connect to.
        tool_list: Optional list of specific tool names to include.

    Returns:
        A list of crewai format tools from Klavis MCP server.
    """
    if klavis_api_key is None:
        klavis_api_key = os.getenv("KLAVIS_API_KEY")
        if klavis_api_key is None:
            logger.error("KLAVIS_API_KEY is not set")
            raise ValueError("KLAVIS_API_KEY is not set")
    
    if mcp_server_url is None:
        mcp_server_url = os.getenv("KLAVIS_MCP_SERVER_URL")
        if mcp_server_url is None:
            logger.error("mcp_server_url parameter or KLAVIS_MCP_SERVER_URL environment variable is required")
            raise ValueError("mcp_server_url parameter or KLAVIS_MCP_SERVER_URL environment variable is required")
    
    adapter = KlavisMcpServerAdapter(klavis_api_key, mcp_server_url)
    all_tools = adapter.tools()

    if tool_list is None:
        return all_tools

    return [tool for tool in all_tools if tool.name in tool_list]
