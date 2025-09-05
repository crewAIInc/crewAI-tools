import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from crewai_tools.tools.steel_scrape_website_tool.steel_scrape_website_tool import (
    SteelScrapeWebsiteTool,
)


@pytest.fixture(autouse=True)
def mock_env_api_key():
    with patch.dict(os.environ, {"STEEL_API_KEY": "test_key"}):
        yield

@pytest.fixture(autouse=True)
def mock_steel_module():
    original = sys.modules.get("steel")
    mock_module = MagicMock()
    mock_module.Steel = MagicMock()
    sys.modules["steel"] = mock_module
    try:
        yield mock_module.Steel
    finally:
        if original is not None:
            sys.modules["steel"] = original
        else:
            del sys.modules["steel"]

def test_init_prefers_arg_over_env():
    tool = SteelScrapeWebsiteTool(api_key="arg_key")
    assert tool.api_key == "arg_key"


def test_init_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("STEEL_API_KEY", raising=False)
    with pytest.raises(EnvironmentError):
        SteelScrapeWebsiteTool()


def test_run_success(mock_steel_module):
    mock_client = mock_steel_module.return_value
    mock_client.scrape.return_value = {"markdown": "Hello"}

    tool = SteelScrapeWebsiteTool(api_key="k", formats=["markdown"], proxy=True)
    result = tool._run("https://example.com")

    assert result == {"markdown": "Hello"}
    mock_client.scrape.assert_called_once_with(
        url="https://example.com", use_proxy=True, format=["markdown"]
    )


def test_run_raises_when_not_initialized(monkeypatch):
    tool = SteelScrapeWebsiteTool(api_key="k")
    tool._steel = None
    with pytest.raises(RuntimeError):
        tool._run("https://example.com")


def test_defaults_and_env():
    tool = SteelScrapeWebsiteTool()
    assert tool.api_key == "test_key"
    assert tool.formats == ["markdown"]
    assert tool.proxy is None
