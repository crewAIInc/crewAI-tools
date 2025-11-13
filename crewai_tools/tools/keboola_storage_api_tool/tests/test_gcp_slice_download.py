import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from crewai_tools.tools.keboola_storage_api_tool.gcp_slice_download import download_gcp_slices, KeboolaAPIError


@pytest.fixture
def mock_credentials():
    return {
        "gcsCredentials": {
            "access_token": "fake-access-token"
        }
    }


def test_download_gcp_slices_success(mock_credentials):
    entries = [
        {"url": "gs://test-bucket/path/to/file1.csv"},
        {"url": "gs://test-bucket/path/to/file2.csv"}
    ]
    columns = ["id", "name"]

    csv_map = {
        "file1.csv": "1,Alice\n2,Bob\n",
        "file2.csv": "3,Charlie\n4,Diana\n"
    }

    def mock_get(url, *args, **kwargs):
        if "file1.csv" in url:
            return MagicMock(status_code=200, text=csv_map["file1.csv"], raise_for_status=lambda: None)
        elif "file2.csv" in url:
            return MagicMock(status_code=200, text=csv_map["file2.csv"], raise_for_status=lambda: None)
        raise Exception("Unexpected URL")

    with patch("google.auth.transport.requests.AuthorizedSession.get", side_effect=mock_get):
        df = download_gcp_slices(entries, columns, mock_credentials)

    expected_df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Charlie", "Diana"]
    })

    df["id"] = df["id"].astype(int)
    pd.testing.assert_frame_equal(df, expected_df)


def test_download_gcp_slices_missing_token():
    entries = [{"url": "gs://bucket/path"}]
    bad_credentials = {}
    with pytest.raises(KeboolaAPIError, match="Missing access token"):
        download_gcp_slices(entries, ["id"], bad_credentials)
