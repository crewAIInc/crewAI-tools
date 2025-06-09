"""
AWS Bedrock Inline Agents module for CrewAI.

This module provides tools for interacting with AWS Bedrock Inline Agents.
"""

from .bedrock_inline_agent_tool import BedrockInlineAgentTool
from .utils.config_loader import ConfigLoader


__all__ = ["BedrockInlineAgentTool", "ConfigLoader"]
