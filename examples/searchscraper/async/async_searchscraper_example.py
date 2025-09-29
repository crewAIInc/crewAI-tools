"""
Example of using the async searchscraper functionality to search for information concurrently.

This example demonstrates the configurable website limits feature:
- Default: 3 websites (30 credits)
- Enhanced: 5 websites (50 credits) - for better research depth
- Maximum: 20 websites (200 credits) - for comprehensive research
"""

import asyncio

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_logging(level="INFO")


async def main():
    # Initialize async client
    sgai_client = AsyncClient(api_key="your-api-key-here")

    # List of search queries with different website limits for demonstration
    queries = [
        ("What is the latest version of Python and what are its main features?", 3),
        ("What are the key differences between Python 2 and Python 3?", 5),
        ("What is Python's GIL and how does it work?", 3),
    ]

    # Create tasks for concurrent execution with configurable website limits
    tasks = [
        sgai_client.searchscraper(user_prompt=query, num_results=num_results)
        for query, num_results in queries
    ]

    # Execute requests concurrently
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"\nError for query {i+1}: {response}")
        else:
            query, num_results = queries[i]
            print(f"\nSearch {i+1}:")
            print(f"Query: {query}")
            print(
                f"Websites searched: {num_results} (Credits: {30 if num_results <= 3 else 30 + (num_results - 3) * 10})"
            )
            print(f"Result: {response['result']}")
            print("Reference URLs:")
            for url in response["reference_urls"]:
                print(f"- {url}")

    await sgai_client.close()


if __name__ == "__main__":
    asyncio.run(main())
