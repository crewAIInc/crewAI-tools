"""
AWS Bedrock module for CrewAI.

This module provides tools for interacting with AWS Bedrock services.
"""

from .knowledge_base.retriever_tool import BedrockKBRetrieverTool
from .agents.invoke_agent_tool import BedrockInvokeAgentTool
from .inline_agents import BedrockInlineAgentTool, ConfigLoader

__all__ = [
    "BedrockKBRetrieverTool",
    "BedrockInvokeAgentTool",
    "BedrockInlineAgentTool",
    "ConfigLoader"
]
