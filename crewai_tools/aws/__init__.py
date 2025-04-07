"""
AWS module for CrewAI.

This module provides tools for interacting with AWS services.
"""

from .s3 import S3ReaderTool, S3WriterTool
from .bedrock import (
    BedrockKBRetrieverTool,
    BedrockInvokeAgentTool,
    BedrockInlineAgentTool,
    ConfigLoader
)

__all__ = [
    'S3ReaderTool',
    'S3WriterTool',
    'BedrockKBRetrieverTool',
    'BedrockInvokeAgentTool',
    'BedrockInlineAgentTool',
    'ConfigLoader'
]
