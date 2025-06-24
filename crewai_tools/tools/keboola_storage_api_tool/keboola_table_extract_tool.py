import pandas as pd
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from .azure_slice_download import download_azure_slices
from .exceptions import KeboolaAPIError
from .gcp_slice_download import download_gcp_slices
from .s3_slice_download import download_s3_slices
from .utils import (
    prepare_keboola_headers,
    fetch_table_columns,
    start_and_poll_export_job
)


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

    Example:
        .. code-block:: python
            from crewai_tools import KeboolaTableExtractTool

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
            raise KeboolaAPIError(f"Failed to download table: {str(e)}") from e

    def download_keboola_table(self, table_id: str, token: str, api_url: str) -> pd.DataFrame:
        api_url = api_url.rstrip("/")
        headers = prepare_keboola_headers(token)

        columns = fetch_table_columns(table_id, token, api_url)
        file_id = start_and_poll_export_job(table_id, token, api_url)

        metadata_url = f"{api_url}/v2/storage/files/{file_id}?federationToken=1"
        metadata = requests.get(metadata_url, headers=headers).json()
        manifest_url = metadata["url"]

        manifest = requests.get(manifest_url).json()
        entries = manifest.get("entries", [])

        if not entries:
            return pd.DataFrame(columns=columns)

        first_url = entries[0]["url"]
        if first_url.startswith("gs://"):
            return download_gcp_slices(entries, columns, metadata)
        elif first_url.startswith("s3://"):
            return download_s3_slices(entries, columns, metadata.get("credentials", {}))
        elif first_url.startswith("azure://"):
            return download_azure_slices(entries, columns, manifest_url)
        else:
            raise ValueError(f"Unknown storage type in URL: {first_url}")
