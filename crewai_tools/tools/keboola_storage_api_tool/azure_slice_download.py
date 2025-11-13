import pandas as pd
import requests
from io import StringIO
from urllib.parse import urlparse
from .exceptions import KeboolaAPIError


def download_azure_slices(entries: list[dict], columns: list[str], manifest_url: str) -> pd.DataFrame:
    parsed = urlparse(manifest_url)
    storage_host = parsed.netloc
    sas_token = parsed.query

    merged_df = pd.DataFrame()
    for entry in entries:
        try:
            azure_url = entry["url"]
            if not azure_url.startswith("azure://"):
                raise KeboolaAPIError(f"Invalid Azure URL format: {azure_url}")
            path = azure_url.replace("azure://", "").split("/", 1)[1]
            https_url = f"https://{storage_host}/{path}?{sas_token}"

            response = requests.get(https_url)
            response.raise_for_status()

            df = pd.read_csv(StringIO(response.text), header=None)
            df.columns = columns
            merged_df = pd.concat([merged_df, df], ignore_index=True)
        except Exception as e:
            raise KeboolaAPIError(f"Failed to download Azure slice from {entry['url']}: {str(e)}")
    return merged_df
