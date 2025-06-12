import os
import boto3
import time
import tempfile
import requests
import pandas as pd
from io import StringIO
from urllib.parse import urlparse, quote
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession

class ExtractInput(BaseModel):
    table_id: str = Field(..., description="Full table ID like 'in.c-usage.usage_data'")
    api_token: str = Field(..., description="Keboola Storage API token")
    base_url: str = Field(..., description="Keboola base API URL (e.g. https://connection.keboola.com)")

class KeboolaTableExtractTool(BaseTool):
    """Tool that extracts table data from Keboola Storage API.

       This tool uses asynchronous export via the Keboola Storage API and supports
       multiple cloud backends automatically (AWS S3, GCP, Azure). It polls the export job,
       downloads and combines CSV slices, and returns the data as a CSV string.

       To use, you must provide the following arguments:
       - `table_id`: The full ID of the table (e.g., 'in.c-bucket.table').
       - `api_token`: A valid Keboola Storage API token.
       - `base_url`: The base URL of the Keboola stack to connect to (e.g., https://connection.keboola.com).

       This tool auto-detects the storage backend based on the export manifest entries.

       Supported Keboola stacks include:
         - https://connection.keboola.com (AWS US East 1)
         - https://connection.eu-central-1.keboola.com (AWS EU Central 1)
         - https://connection.north-europe.azure.keboola.com (Azure North Europe)
         - https://connection.europe-west3.gcp.keboola.com (GCP Europe West 3)
         - https://connection.us-east4.gcp.keboola.com (GCP US East 4)

       Args:
           table_id (str): Full Keboola table ID (e.g., 'in.c-bucket.table').
           api_token (str): Keboola Storage API token.
           base_url (str): Keboola Connection stack base URL.

       Returns:
           str: CSV content of the table as a string.

       Raises:
           ValueError: If table export fails or invalid credentials are used.
           TimeoutError: If the export job does not complete in time.
           Exception: For general API or download errors.

       Example:
           .. code-block:: python

               from keboola_storage_api_tool.keboola_table_extract_tool import KeboolaTableExtractTool

               tool = KeboolaTableExtractTool()
               csv_string = tool.run({
                   "table_id": "in.c-usage.usage_data",
                   "api_token": "your_keboola_token",
                   "base_url": "https://connection.eu-central-1.keboola.com"
               })

               print(csv_string[:500])  # Print first 500 characters of the CSV
        """

    name: str = "Keboola Table Extract"
    description: str = "Downloads a Keboola table (async export) and returns its content as a CSV string"
    args_schema: Type[BaseModel] = ExtractInput

    def _run(self, table_id: str, api_token: str, base_url: str) -> str:
        try:
            df = self.download_keboola_table(table_id, api_token, base_url)
            return df.to_csv(index=False)
        except Exception as e:
            return f"\u274c Failed to download table: {str(e)}"

    def fetch_table_columns(self, table_id: str, token: str, api_url: str) -> list[str]:
        headers = {"X-StorageApi-Token": token}
        url = f"{api_url}/v2/storage/tables/{table_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("columns", [])

    def download_keboola_table(self, table_id: str, token: str, api_url: str) -> pd.DataFrame:
        headers = {"X-StorageApi-Token": token}
        api_url = api_url.rstrip("/")
        max_attempts = 30

        columns = self.fetch_table_columns(table_id, token, api_url)
        export_url = f"{api_url}/v2/storage/tables/{table_id}/export-async"
        export_response = requests.post(export_url, headers=headers, json={"format": "rfc"})
        export_response.raise_for_status()
        job_id = export_response.json()["id"]

        job_url = f"{api_url}/v2/storage/jobs/{job_id}"
        for attempt in range(1, max_attempts + 1):
            job_response = requests.get(job_url, headers=headers)
            job_response.raise_for_status()
            status = job_response.json()["status"]
            if status == "success":
                break
            elif status in {"error", "cancelled"}:
                raise Exception(f"Job failed: {job_response.json()}")
            time.sleep(2)
        else:
            raise TimeoutError("Export job did not complete in time.")

        file_id = job_response.json()["results"]["file"]["id"]
        metadata_url = f"{api_url}/v2/storage/files/{file_id}?federationToken=1"
        metadata = requests.get(metadata_url, headers=headers).json()
        manifest_url = metadata["url"]

        manifest = requests.get(manifest_url).json()
        entries = manifest.get("entries", [])

        if not entries:
            return pd.DataFrame(columns=columns)

        first_url = entries[0]["url"]

        if first_url.startswith("gs://"):
            return self.download_gcp_slices(entries, columns, metadata)
        elif first_url.startswith("s3://"):
            return self.download_s3_slices(entries, columns, metadata.get("credentials", {}))
        elif first_url.startswith("azure://"):
            return self.download_azure_slices(entries, columns, manifest_url)
        else:
            raise ValueError(f"Unknown storage type in URL: {first_url}")

    def download_gcp_slices(self, entries: list, columns: list, credentials: dict) -> pd.DataFrame:
        access_token = credentials.get("gcsCredentials", {}).get("access_token")
        if not access_token and "credentials" in credentials:
            access_token = credentials["credentials"].get("access_token")
        if not access_token:
            raise ValueError("No access token found for GCP authentication")

        creds = Credentials(token=access_token)
        authed_session = AuthorizedSession(creds)

        merged_df = pd.DataFrame()
        for entry in entries:
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
        return merged_df

    def download_s3_slices(self, entries: list, columns: list, credentials: dict) -> pd.DataFrame:
        access_key = credentials.get("AccessKeyId") or credentials.get("accessKeyId")
        secret_key = credentials.get("SecretAccessKey") or credentials.get("secretAccessKey")
        session_token = credentials.get("SessionToken") or credentials.get("sessionToken")
        if not (access_key and secret_key):
            raise ValueError("Missing AWS credentials")

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            region_name="eu-central-1"
        )
        s3_client = session.client('s3')

        merged_df = pd.DataFrame()
        for entry in entries:
            s3_url = entry["url"]
            s3_parts = s3_url[5:].split('/', 1)
            bucket = s3_parts[0]
            key = s3_parts[1]
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name
            try:
                s3_client.download_file(bucket, key, tmp_path)
                with open(tmp_path, 'r') as f:
                    content = f.read()
                df = pd.read_csv(StringIO(content), header=None)
                df.columns = columns
                merged_df = pd.concat([merged_df, df], ignore_index=True)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        return merged_df

    def download_azure_slices(self, entries: list, columns: list, manifest_url: str) -> pd.DataFrame:
        parsed = urlparse(manifest_url)
        storage_host = parsed.netloc
        sas_token = parsed.query

        merged_df = pd.DataFrame()
        for entry in entries:
            azure_url = entry["url"]
            if azure_url.startswith("azure://"):
                parts = azure_url.replace("azure://", "").split("/", 1)
                if len(parts) != 2:
                    raise ValueError(f"Invalid Azure URL format: {azure_url}")
                path = parts[1]
                https_url = f"https://{storage_host}/{path}?{sas_token}"
            else:
                raise ValueError(f"Expected Azure URL starting with 'azure://', got: {azure_url}")

            response = requests.get(https_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), header=None)
            df.columns = columns
            merged_df = pd.concat([merged_df, df], ignore_index=True)
        return merged_df