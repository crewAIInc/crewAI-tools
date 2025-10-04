import pytest
import pandas as pd
from io import StringIO
from unittest.mock import patch, MagicMock
from crewai_tools.tools.keboola_storage_api_tool.s3_slice_download import download_s3_slices, KeboolaAPIError


@pytest.fixture
def mock_credentials():
    return {
        "AccessKeyId": "test-access",
        "SecretAccessKey": "test-secret",
        "SessionToken": "test-token"
    }


def test_download_s3_slices_success(mock_credentials):
    entries = [
        {"url": "s3://my-bucket/file1.csv"},
        {"url": "s3://my-bucket/file2.csv"}
    ]
    columns = ["id", "name"]

    csv_map = {
        "file1.csv": "1,Alice\n2,Bob\n",
        "file2.csv": "3,Charlie\n4,Diana\n"
    }

    written_files = {}

    with patch("boto3.Session.client") as mock_client_factory, \
         patch("os.path.exists", return_value=True), \
         patch("os.remove"):

        import builtins
        real_open = builtins.open

        mock_client = MagicMock()
        mock_client_factory.return_value = mock_client

        def mock_download_file(Bucket, Key, Filename):
            content = csv_map.get(Key.split("/")[-1], "")
            written_files[Filename] = content
            with real_open(Filename, "w") as f:
                f.write(content)

        mock_client.download_file.side_effect = mock_download_file

        def open_mock(filename, mode='r', *args, **kwargs):
            if "r" in mode and filename in written_files:
                return StringIO(written_files[filename])
            return real_open(filename, mode, *args, **kwargs)

        with patch("builtins.open", side_effect=open_mock):
            df = download_s3_slices(entries, columns, mock_credentials)

    expected_df = pd.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Charlie", "Diana"]
    })

    df["id"] = df["id"].astype(int)
    pd.testing.assert_frame_equal(df, expected_df)


def test_download_s3_slices_missing_credentials():
    entries = [{"url": "s3://bucket/path"}]
    columns = ["id"]
    bad_credentials = {}

    with pytest.raises(KeboolaAPIError, match="Missing AWS credentials"):
        download_s3_slices(entries, columns, bad_credentials)
