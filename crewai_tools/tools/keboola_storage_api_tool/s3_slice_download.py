import os
import boto3
import pandas as pd
from io import StringIO
import tempfile
from contextlib import contextmanager
from .exceptions import KeboolaAPIError


@contextmanager
def temporary_file():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        yield tmp.name
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)


def download_s3_slices(entries: list[dict], columns: list[str], credentials: dict[str, str]) -> pd.DataFrame:
    access_key = credentials.get("AccessKeyId") or credentials.get("accessKeyId")
    secret_key = credentials.get("SecretAccessKey") or credentials.get("secretAccessKey")
    session_token = credentials.get("SessionToken") or credentials.get("sessionToken")

    if not (access_key and secret_key):
        raise KeboolaAPIError("Missing AWS credentials for S3 slice download.")

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
        region_name="eu-central-1"
    )
    s3_client = session.client('s3')

    merged_df = pd.DataFrame()
    for entry in entries:
        try:
            s3_url = entry["url"]
            bucket, key = s3_url[5:].split("/", 1)
            with temporary_file() as tmp_path:
                s3_client.download_file(bucket, key, tmp_path)
                with open(tmp_path, "r") as f:
                    content = f.read()
                df = pd.read_csv(StringIO(content), header=None)
                df.columns = columns
                merged_df = pd.concat([merged_df, df], ignore_index=True)
        except Exception as e:
            raise KeboolaAPIError(f"Failed to download S3 slice from {entry['url']}: {str(e)}")
    return merged_df
