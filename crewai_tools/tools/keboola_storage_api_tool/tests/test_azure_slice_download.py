import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from crewai_tools.tools.keboola_storage_api_tool.azure_slice_download import download_azure_slices, KeboolaAPIError


def test_download_azure_slices_success():
    entries = [
        {"url": "azure://container/file1.csv"},
        {"url": "azure://container/file2.csv"},
    ]
    columns = ["id", "name"]
    manifest_url = "https://fakestorageaccount.blob.core.windows.net/container/manifest?sig=FAKE_SAS"

    csv_map = {
        "file1.csv": "1,Alice\n2,Bob\n",
        "file2.csv": "3,Charlie\n4,Diana\n"
    }

    def mock_requests_get(url, *args, **kwargs):
        if "file1.csv" in url:
            return MagicMock(status_code=200, text=csv_map["file1.csv"], raise_for_status=lambda: None)
        elif "file2.csv" in url:
            return MagicMock(status_code=200, text=csv_map["file2.csv"], raise_for_status=lambda: None)
        raise Exception("Unexpected URL")

    with patch("requests.get", side_effect=mock_requests_get):
        df = download_azure_slices(entries, columns, manifest_url)

    expected_df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Charlie", "Diana"]
    })
    df["id"] = df["id"].astype(int)
    pd.testing.assert_frame_equal(df, expected_df)


def test_download_azure_slices_invalid_url():
    entries = [{"url": "http://bad-url.com/file.csv"}]
    columns = ["id"]
    manifest_url = "https://storage/fake/manifest?sig=FAKE"

    with pytest.raises(KeboolaAPIError, match="Invalid Azure URL format"):
        download_azure_slices(entries, columns, manifest_url)


def test_download_azure_slices_http_failure():
    entries = [{"url": "azure://container/broken.csv"}]
    columns = ["id"]
    manifest_url = "https://storage/fake/manifest?sig=FAKE"

    with patch("requests.get", side_effect=Exception("Timeout")):
        with pytest.raises(KeboolaAPIError, match="Failed to download Azure slice"):
            download_azure_slices(entries, columns, manifest_url)
