import asyncio
import os

from dotenv import load_dotenv

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")


async def main():
    # Initialize async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return

    sgai_client = AsyncClient(api_key=api_key)

    # Concurrent scraping requests
    urls = [
        "https://scrapegraphai.com/",
        "https://github.com/ScrapeGraphAI/Scrapegraph-ai",
    ]

    tasks = [
        sgai_client.smartscraper(
            website_url=url, user_prompt="Summarize the main content"
        )
        for url in urls
    ]

    # Execute requests concurrently
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"\nError for {urls[i]}: {response}")
        else:
            print(f"\nPage {i+1} Summary:")
            print(f"URL: {urls[i]}")
            print(f"Result: {response['result']}")

    await sgai_client.close()


if __name__ == "__main__":
    asyncio.run(main())
