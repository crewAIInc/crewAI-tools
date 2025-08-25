import time
import requests
from .exceptions import KeboolaAPIError
from .config import KeboolaConfig

config = KeboolaConfig()


def prepare_keboola_headers(token: str) -> dict[str, str]:
    return {"X-StorageApi-Token": token}

def fetch_table_columns(table_id: str, token: str, api_url: str) -> list[str]:
    headers = prepare_keboola_headers(token)
    url = f"{api_url.rstrip('/')}/v2/storage/tables/{table_id}"
    response = requests.get(url, headers=headers)
    if not response.ok:
        raise KeboolaAPIError(f"Failed to fetch table columns: {response.text}")
    return response.json().get("columns", [])

def start_and_poll_export_job(table_id: str, token: str, api_url: str) -> str:
    api_url = api_url.rstrip("/")
    headers = prepare_keboola_headers(token)
    export_url = f"{api_url}/v2/storage/tables/{table_id}/export-async"
    export_response = requests.post(export_url, headers=headers, json={"format": "rfc"})
    if not export_response.ok:
        raise KeboolaAPIError(f"Failed to start export job: {export_response.text}")

    job_id = export_response.json()["id"]
    job_url = f"{api_url}/v2/storage/jobs/{job_id}"

    for attempt in range(1, config.max_poll_attempts + 1):
        job_response = requests.get(job_url, headers=headers)
        job_response.raise_for_status()
        job_data = job_response.json()
        status = job_data.get("status")

        if status == "success":
            return job_data["results"]["file"]["id"]
        elif status in {"error", "cancelled"}:
            raise KeboolaAPIError(f"Export job failed: {job_data}")

        time.sleep(config.poll_interval_seconds)

    raise TimeoutError("Export job did not complete in time.")
