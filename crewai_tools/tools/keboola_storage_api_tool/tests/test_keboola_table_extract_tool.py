import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
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

    with pytest.raises(Exception) as exc:
        tool._run(
            table_id="in.c-main.fail",
            api_token="dummy_token",
            base_url="https://connection.eu-central-1.keboola.com"
        )

    assert "Failed to download table" in str(exc.value)


@pytest.mark.parametrize(
    "url, expected_func",
    [
        ("s3://bucket/file.csv", "download_s3_slices"),
        ("gs://bucket/file.csv", "download_gcp_slices"),
        ("azure://container/blob.csv", "download_azure_slices"),
    ]
)
@patch("crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.requests.get")
@patch("crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.fetch_table_columns", return_value=["id", "name"])
@patch("crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.start_and_poll_export_job", return_value="file-id")
def test_backend_detection(mock_start, mock_columns, mock_requests, url, expected_func, tool):
    manifest = {"entries": [{"url": url}]}
    metadata = {
        "url": "https://storage.fake/manifest",
        "credentials": {"AccessKeyId": "X", "SecretAccessKey": "Y", "SessionToken": "Z"}
    }

    def side_effect(*args, **kwargs):
        if args[0].endswith("/files/file-id?federationToken=1"):
            m = MagicMock()
            m.json.return_value = metadata
            return m
        elif args[0] == metadata["url"]:
            m = MagicMock()
            m.json.return_value = manifest
            return m
        raise Exception(f"Unexpected request to {args[0]}")

    mock_requests.side_effect = side_effect

    with patch(f"crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.{expected_func}", return_value=pd.DataFrame(columns=["id", "name"])) as backend_mock:
        df = tool.download_keboola_table("in.c-dummy.table", "dummy_token", "https://connection.eu-central-1.keboola.com")
        assert isinstance(df, pd.DataFrame)
        backend_mock.assert_called_once()


def test_export_timeout(tool):
    with patch("crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.start_and_poll_export_job", side_effect=TimeoutError("Export job did not complete in time")), \
         patch("crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.fetch_table_columns", return_value=["id", "value"]), \
         patch("crewai_tools.tools.keboola_storage_api_tool.keboola_table_extract_tool.requests.get"):
        with pytest.raises(Exception) as exc:
            tool.download_keboola_table("in.c-timeout.table", "dummy_token", "https://connection.eu-central-1.keboola.com")
        assert "Export job did not complete in time" in str(exc.value)
