"""Tests for the APIBasedTool base class."""
import os
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from crewai_tools.tools.base.api_tool import APIBasedTool, APIKeyConfig


class TestAPITool(APIBasedTool):
    """Test implementation of APIBasedTool."""

    api_key_config = APIKeyConfig(
        env_var="TEST_API_KEY", key_prefix="test_", min_length=10
    )


def test_api_tool_initialization():
    """Test successful initialization with valid API key."""
    with patch.dict(os.environ, {"TEST_API_KEY": "test_valid_key_12345"}):
        tool = TestAPITool()
        assert isinstance(tool.get_api_key(), SecretStr)
        assert tool.get_api_key().get_secret_value() == "test_valid_key_12345"


def test_api_tool_missing_key():
    """Test initialization with missing API key."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing API key"):
            TestAPITool()


def test_api_tool_invalid_prefix():
    """Test initialization with invalid API key prefix."""
    with patch.dict(os.environ, {"TEST_API_KEY": "invalid_prefix_key"}):
        with pytest.raises(ValueError, match="Invalid API key format"):
            TestAPITool()


def test_api_tool_short_key():
    """Test initialization with too short API key."""
    with patch.dict(os.environ, {"TEST_API_KEY": "test_short"}):
        with pytest.raises(ValueError, match="API key length below minimum"):
            TestAPITool()


def test_api_key_not_exposed_in_str():
    """Test that API key is not exposed in string representation."""
    with patch.dict(os.environ, {"TEST_API_KEY": "test_valid_key_12345"}):
        tool = TestAPITool()
        assert "test_valid_key_12345" not in str(tool)
        assert "test_valid_key_12345" not in repr(tool)
