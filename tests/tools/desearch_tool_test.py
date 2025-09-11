import os
from unittest.mock import patch
from crewai_tools import DesearchTool

import pytest


@pytest.fixture
def desearch_tool():
    return DesearchTool(api_key="test_api_key")


@pytest.fixture(autouse=True)
def mock_desearch_api_key():
    with patch.dict(os.environ, {"DESEARCH_API_KEY": "test_key_from_env"}):
        yield


def test_desearch_tool_initialization():
    with patch(
        "crewai_tools.tools.desearch_tools.desearch_tool.Desearch"
    ) as mock_desearch_class:
        api_key = "test_api_key"
        tool = DesearchTool(api_key=api_key)

        assert tool.api_key == api_key
        mock_desearch_class.assert_called_once_with(api_key=api_key)


def test_desearch_tool_initialization_with_env(mock_desearch_api_key):
    with patch(
        "crewai_tools.tools.desearch_tools.desearch_tool.Desearch"
    ) as mock_desearch_class:
        DesearchTool()
        mock_desearch_class.assert_called_once_with(api_key="test_key_from_env")
