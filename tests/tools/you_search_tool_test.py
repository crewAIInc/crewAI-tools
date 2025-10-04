from unittest.mock import patch

import pytest

from crewai_tools.tools.you_search_tool.you_search_tool import YouSearchTool


def test_requires_env_var(monkeypatch):
    monkeypatch.delenv("YOU_API_KEY", raising=False)
    tool = YouSearchTool()
    result = tool.run(query="test")
    assert "YOU_API_KEY" in result


@patch("crewai_tools.tools.you_search_tool.you_search_tool.requests.get")
def test_happy_path(mock_get, monkeypatch):
    monkeypatch.setenv("YOU_API_KEY", "test")

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "results": {
            "web": [
                {
                    "url": "https://www.europarl.europa.eu/topics/en/topic/state-of-the-eu-debates",
                    "title": "State of the EU debates",
                    "snippets": [
                        "MEPs will scrutinise the work of the European Commission..."
                    ],
                }
            ]
        },
        "metadata": {"query": "result of the political debate in EU"},
    }

    tool = YouSearchTool()
    result = tool.run(query="result of the political debate in EU")
    assert "results" in result
    assert "europarl.europa.eu" in result


