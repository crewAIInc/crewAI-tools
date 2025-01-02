from typing import Any, Type
from urllib.parse import urlencode

import requests
from pydantic import BaseModel, Field

from crewai_tools.tools.serply_api_tool.serply_base_tool import SerplyBaseTool


class SerplyJobSearchToolSchema(BaseModel):
    """Input for Job Search."""

    search_query: str = Field(
        ...,
        description="Mandatory search query you want to use to fetch jobs postings.",
    )


class SerplyJobSearchTool(SerplyBaseTool):
    name: str = "Job Search"
    description: str = (
        "A tool to perform to perform a job search in the US with a search_query."
    )
    args_schema: Type[BaseModel] = SerplyJobSearchToolSchema
    request_url: str = "https://api.serply.io/v1/job/search/"
    """
        proxy_location: (str): Where to get jobs, specifically for a specific country results.
            - Currently only supports US
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        query_payload = {}

        if "query" in kwargs:
            query_payload["q"] = kwargs["query"]
        elif "search_query" in kwargs:
            query_payload["q"] = kwargs["search_query"]

        # build the url
        url = f"{self.request_url}{urlencode(query_payload)}"

        response = requests.request("GET", url, headers=self.headers)

        jobs = response.json().get("jobs", "")

        if not jobs:
            return ""

        string = []
        for job in jobs:
            try:
                string.append(
                    "\n".join(
                        [
                            f"Position: {job['position']}",
                            f"Employer: {job['employer']}",
                            f"Location: {job['location']}",
                            f"Link: {job['link']}",
                            f"""Highest: {', '.join([h for h in job['highlights']])}""",
                            f"Is Remote: {job['is_remote']}",
                            f"Is Hybrid: {job['is_remote']}",
                            "---",
                        ]
                    )
                )
            except KeyError:
                continue

        content = "\n".join(string)
        return f"\nSearch results: {content}\n"
