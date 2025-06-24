import pandas as pd
from io import StringIO
from urllib.parse import quote
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials
from .exceptions import KeboolaAPIError


def download_gcp_slices(entries: list[dict], columns: list[str], credentials: dict[str, str]) -> pd.DataFrame:
    access_token = (
        credentials.get("gcsCredentials", {}).get("access_token") or
        credentials.get("credentials", {}).get("access_token")
    )
    if not access_token:
        raise KeboolaAPIError("Missing access token for GCP slice download.")

    creds = Credentials(token=access_token)
    authed_session = AuthorizedSession(creds)

    merged_df = pd.DataFrame()
    for entry in entries:
        try:
            gs_url = entry["url"]
            _, path = gs_url.split("gs://", 1)
            bucket_name, *blob_parts = path.split("/")
            blob_path = "/".join(blob_parts)
            quoted_path = quote(blob_path, safe="")
            download_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}/o/{quoted_path}?alt=media"

            response = authed_session.get(download_url)
            response.raise_for_status()

            df = pd.read_csv(StringIO(response.text), header=None)
            df.columns = columns
            merged_df = pd.concat([merged_df, df], ignore_index=True)
        except Exception as e:
            raise KeboolaAPIError(f"Failed to download GCP slice from {entry['url']}: {str(e)}")
    return merged_df