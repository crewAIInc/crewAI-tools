"""
Example of using the async searchscraper functionality with output schemas for extraction.

This example demonstrates both schema-based output and configurable website limits:
- Using different website limits for different complexity levels
- Enhanced searches provide better data for complex schema population
- Concurrent processing of multiple schema-based searches
"""

import asyncio
from typing import List

from pydantic import BaseModel

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_logging(level="INFO")


# Define schemas for extracting structured data
class PythonVersionInfo(BaseModel):
    version: str
    release_date: str
    major_features: List[str]


class PythonComparison(BaseModel):
    key_differences: List[str]
    backward_compatible: bool
    migration_difficulty: str


class GILInfo(BaseModel):
    definition: str
    purpose: str
    limitations: List[str]
    workarounds: List[str]


async def main():
    # Initialize async client
    sgai_client = AsyncClient(api_key="your-api-key-here")

    # Define search queries with their corresponding schemas and website limits
    searches = [
        {
            "prompt": "What is the latest version of Python? Include the release date and main features.",
            "schema": PythonVersionInfo,
            "num_results": 4,  # Moderate search for version info (40 credits)
        },
        {
            "prompt": "Compare Python 2 and Python 3, including backward compatibility and migration difficulty.",
            "schema": PythonComparison,
            "num_results": 6,  # Enhanced search for comparison (60 credits)
        },
        {
            "prompt": "Explain Python's GIL, its purpose, limitations, and possible workarounds.",
            "schema": GILInfo,
            "num_results": 8,  # Deep search for technical details (80 credits)
        },
    ]

    print("🚀 Starting concurrent schema-based searches with configurable limits:")
    for i, search in enumerate(searches, 1):
        credits = (
            30 if search["num_results"] <= 3 else 30 + (search["num_results"] - 3) * 10
        )
        print(
            f"   {i}. {search['num_results']} websites ({credits} credits): {search['prompt'][:50]}..."
        )
    print()

    # Create tasks for concurrent execution with configurable website limits
    tasks = [
        sgai_client.searchscraper(
            user_prompt=search["prompt"],
            num_results=search["num_results"],
            output_schema=search["schema"],
        )
        for search in searches
    ]

    # Execute requests concurrently
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"\nError for search {i+1}: {response}")
        else:
            print(f"\nSearch {i+1}:")
            print(f"Query: {searches[i]['prompt']}")
            # print(f"Raw Result: {response['result']}")

            try:
                # Try to extract structured data using the schema
                result = searches[i]["schema"].model_validate(response["result"])

                # Print extracted structured data
                if isinstance(result, PythonVersionInfo):
                    print("\nExtracted Data:")
                    print(f"Python Version: {result.version}")
                    print(f"Release Date: {result.release_date}")
                    print("Major Features:")
                    for feature in result.major_features:
                        print(f"- {feature}")

                elif isinstance(result, PythonComparison):
                    print("\nExtracted Data:")
                    print("Key Differences:")
                    for diff in result.key_differences:
                        print(f"- {diff}")
                    print(f"Backward Compatible: {result.backward_compatible}")
                    print(f"Migration Difficulty: {result.migration_difficulty}")

                elif isinstance(result, GILInfo):
                    print("\nExtracted Data:")
                    print(f"Definition: {result.definition}")
                    print(f"Purpose: {result.purpose}")
                    print("Limitations:")
                    for limit in result.limitations:
                        print(f"- {limit}")
                    print("Workarounds:")
                    for workaround in result.workarounds:
                        print(f"- {workaround}")
            except Exception as e:
                print(f"\nCould not extract structured data: {e}")

            print("\nReference URLs:")
            for url in response["reference_urls"]:
                print(f"- {url}")

    await sgai_client.close()


if __name__ == "__main__":
    asyncio.run(main())
