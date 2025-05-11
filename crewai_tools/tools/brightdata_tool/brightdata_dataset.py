import asyncio
import os
from typing import Any, Dict, Optional, Type

import aiohttp
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class BrightDataDatasetToolSchema(BaseModel):
    """
    Schema for validating input parameters for the BrightDataDatasetTool.

    Attributes:
        dataset_id (str): Required Bright Data Dataset ID used to specify which dataset to access.
        url (str): The URL from which structured data needs to be extracted.
        zipcode (Optional[str]): An optional ZIP code to narrow down the data geographically.
        additional_params (Optional[Dict]): Extra parameters for the Bright Data API call.
        async_mode (Optional[bool]): If True, enables asynchronous execution for data scraping.
    """

    dataset_id: str = Field(..., description="The Bright Data Dataset ID")
    url: str = Field(..., description="The URL to extract data from")
    zipcode: Optional[str] = Field(default=None, description="Optional zipcode")
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional params if any"
    )
    async_mode: Optional[bool] = Field(
        default=False, description="Use async Bright Data API if True"
    )


# Base API URL for Bright Data
BRIGHTDATA_API_URL = "https://api.brightdata.com"
timeout = 1800


# Reused and modified code from https://github.com/luminati-io/langchain-brightdata/blob/main/langchain-brightdata/brightdata_scraper.py
class BrightDataWebScraperAPIWrapper:
    """
    Wrapper class for interacting with Bright Data's Dataset API.

    This class provides methods to synchronously or asynchronously
    scrape structured data from a given URL using Bright Data.

    Methods:
        get_dataset_data: Synchronous method to retrieve structured data.
        get_dataset_data_async: Asynchronous method to retrieve structured data.
    """

    def get_dataset_data(
        self,
        dataset_id: str,
        url: str,
        zipcode: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """
        Perform a synchronous API call to Bright Data to scrape structured data.

        Args:
            dataset_id (str): Bright Data Dataset ID.
            url (str): Target URL to scrape.
            zipcode (Optional[str]): Optional ZIP code for region-specific data.
            additional_params (Optional[Dict]): Additional parameters for API call.

        Returns:
            Dict: Parsed JSON response with structured data.

        Raises:
            ValueError: If the API response status is not 200.
        """
        # Build request data
        request_data = {"url": url}

        if zipcode:
            request_data["zipcode"] = zipcode

        if additional_params:
            request_data.update(additional_params)

        api_key = os.getenv("BRIGHT_DATA_API_KEY")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{BRIGHTDATA_API_URL}/datasets/v3/scrape",
            params={"dataset_id": dataset_id, "include_errors": "true"},
            json=[request_data],
            headers=headers,
            timeout=timeout,
        )

        if response.status_code != 200:
            error_message = f"Error {response.status_code}: {response.text}"
            raise ValueError(error_message)

        return response.json()

    async def get_dataset_data_async(
        self,
        dataset_id: str,
        url: str,
        zipcode: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        polling_interval: int = 5,
    ) -> Dict:
        """
        Asynchronously trigger and poll Bright Data dataset scraping.

        Args:
            dataset_id (str): Bright Data Dataset ID.
            url (str): Target URL to scrape.
            zipcode (Optional[str]): Optional ZIP code for geo-specific data.
            additional_params (Optional[Dict]): Extra API parameters.
            polling_interval (int): Time interval in seconds between polling attempts.

        Returns:
            Dict: Structured dataset result from Bright Data.

        Raises:
            Exception: If any API step fails or the job fails.
            TimeoutError: If polling times out before job completion.
        """
        request_data = {"url": url}
        if zipcode:
            request_data["zipcode"] = zipcode
        if additional_params:
            request_data.update(additional_params)

        api_key = os.getenv("BRIGHT_DATA_API_KEY")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            # Step 1: Trigger job
            async with session.post(
                f"{BRIGHTDATA_API_URL}/datasets/v3/trigger",
                params={"dataset_id": dataset_id, "include_errors": "true"},
                json=[request_data],
                headers=headers,
            ) as trigger_response:
                if trigger_response.status != 200:
                    raise Exception(f"Trigger failed: {await trigger_response.text()}")
                trigger_data = await trigger_response.json()
                print(trigger_data)
                snapshot_id = trigger_data.get("snapshot_id")

            # Step 2: Poll for completion
            elapsed = 0
            while elapsed < timeout:
                await asyncio.sleep(polling_interval)
                elapsed += polling_interval

                async with session.get(
                    f"{BRIGHTDATA_API_URL}/datasets/v3/progress/{snapshot_id}",
                    headers=headers,
                ) as status_response:
                    if status_response.status != 200:
                        raise Exception(
                            f"Status check failed: {await status_response.text()}"
                        )
                    status_data = await status_response.json()
                    if status_data.get("status") == "ready":
                        break
                    elif status_data.get("status") == "error":
                        raise Exception(f"Job failed: {status_data}")
            else:
                raise TimeoutError("Polling timed out before job completed.")

            # Step 3: Retrieve result
            async with session.get(
                f"{BRIGHTDATA_API_URL}/datasets/v3/snapshot/{snapshot_id}",
                headers=headers,
            ) as snapshot_response:
                if snapshot_response.status != 200:
                    raise Exception(
                        f"Result fetch failed: {await snapshot_response.text()}"
                    )

                content_type = snapshot_response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await snapshot_response.json()
                elif "application/octet-stream" in content_type:
                    data = await snapshot_response.read()
                    return {
                        "raw_data": data.decode("utf-8", errors="ignore")
                    }  # or base64 encode


class BrightDataDatasetTool(BaseTool):
    """
    CrewAI-compatible tool for scraping structured data using Bright Data Datasets.

    This class integrates BrightDataWebScraperAPIWrapper with CrewAI's BaseTool interface
    to support synchronous and asynchronous scraping workflows.

    Attributes:
        name (str): Tool name displayed in the CrewAI environment.
        description (str): Tool description shown to agents or users.
        args_schema (Type[BaseModel]): Pydantic schema for validating input arguments.
    """

    name: str = "Bright Data Dataset Tool"
    description: str = (
        "Scrapes structured data using Bright Data Dataset API from a URL"
    )
    args_schema: Type[BaseModel] = BrightDataDatasetToolSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _run(self, **kwargs: Any) -> Any:
        api_wrapper = BrightDataWebScraperAPIWrapper()
        dataset_id = kwargs["dataset_id"]
        url = kwargs["url"]
        zipcode = kwargs.get("zipcode")
        additional_params = kwargs.get("additional_params")
        async_mode = kwargs.get("async_mode", False)

        api_key = os.getenv("BRIGHT_DATA_API_KEY")
        if not api_key:
            raise ValueError("BRIGHT_DATA_API_KEY environment variable is required.")

        try:
            if async_mode:
                return asyncio.run(
                    api_wrapper.get_dataset_data_async(
                        dataset_id=dataset_id,
                        url=url,
                        zipcode=zipcode,
                        additional_params=additional_params,
                    )
                )
            else:
                return api_wrapper.get_dataset_data(
                    dataset_id=dataset_id,
                    url=url,
                    zipcode=zipcode,
                    additional_params=additional_params,
                )
        except Exception as e:
            return f"Bright Data API error: {str(e)}"
