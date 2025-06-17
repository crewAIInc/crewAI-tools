import pandas as pd
import pytest
from unittest.mock import patch
from crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool import KeboolaTableExtractTool


@pytest.fixture
def tool():
    return KeboolaTableExtractTool()


@patch.object(KeboolaTableExtractTool, "download_keboola_table")
def test_success_csv_output(mock_download, tool):
    df = pd.DataFrame({"name": ["Radek"], "age": [34]})
    mock_download.return_value = df

    result = tool._run(
        table_id="in.c-main.test",
        api_token="dummy_token",
        base_url="https://connection.eu-central-1.keboola.com"
    )

    assert "Radek" in result
    assert "age" in result


@patch.object(KeboolaTableExtractTool, "download_keboola_table")
def test_empty_result(mock_download, tool):
    df = pd.DataFrame(columns=["id", "value"])
    mock_download.return_value = df

    result = tool._run(
        table_id="in.c-main.empty",
        api_token="dummy_token",
        base_url="https://connection.eu-central-1.keboola.com"
    )

    assert "id" in result
    assert result.strip() != ""


@patch.object(KeboolaTableExtractTool, "download_keboola_table")
def test_exception_handling(mock_download, tool):
    mock_download.side_effect = Exception("Simulated error")

    result = tool._run(
        table_id="in.c-main.fail",
        api_token="dummy_token",
        base_url="https://connection.eu-central-1.keboola.com"
    )

    assert "Failed to download table" in result
    assert "Simulated error" in result
