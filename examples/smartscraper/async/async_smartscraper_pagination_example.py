#!/usr/bin/env python3
"""
SmartScraper Pagination Example (Async)

This example demonstrates how to use pagination functionality with SmartScraper API using the asynchronous client.
"""

import asyncio
import json
import logging
import os
import time
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel

from scrapegraph_py import AsyncClient
from scrapegraph_py.exceptions import APIError

# Load environment variables from .env file
load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ProductInfo(BaseModel):
    """Schema for product information"""

    name: str
    price: Optional[str] = None
    rating: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class ProductList(BaseModel):
    """Schema for list of products"""

    products: List[ProductInfo]


async def smartscraper_pagination_example():
    """Example of using pagination with SmartScraper (async)"""

    print("SmartScraper Pagination Example (Async)")
    print("=" * 50)

    # Initialize client from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return

    try:
        client = AsyncClient(api_key=api_key)
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return

    # Configuration
    website_url = "https://www.amazon.in/s?k=tv&crid=1TEF1ZFVLU8R8&sprefix=t%2Caps%2C390&ref=nb_sb_noss_2"
    user_prompt = "Extract all product info including name, price, rating, image_url, and description"
    total_pages = 3  # Number of pages to scrape

    print(f"🌐 Website URL: {website_url}")
    print(f"📝 User Prompt: {user_prompt}")
    print(f"📄 Total Pages: {total_pages}")
    print("-" * 50)

    try:
        # Start timing
        start_time = time.time()

        # Make the request with pagination
        result = await client.smartscraper(
            user_prompt=user_prompt,
            website_url=website_url,
            output_schema=ProductList,
            total_pages=total_pages,
        )

        # Calculate duration
        duration = time.time() - start_time

        print(f"✅ Request completed in {duration:.2f} seconds")
        print(f"📊 Response type: {type(result)}")

        # Display results
        if isinstance(result, dict):
            print("\n🔍 Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # Check for pagination success indicators
            if "data" in result:
                print(
                    f"\n✨ Pagination successful! Data extracted from {total_pages} pages"
                )

        elif isinstance(result, list):
            print(f"\n✅ Pagination successful! Extracted {len(result)} items")
            for i, item in enumerate(result[:5]):  # Show first 5 items
                print(f"  {i+1}. {item}")
            if len(result) > 5:
                print(f"  ... and {len(result) - 5} more items")
        else:
            print(f"\n📋 Result: {result}")

    except APIError as e:
        print(f"❌ API Error: {e}")
        print("This could be due to:")
        print("  - Invalid API key")
        print("  - Rate limiting")
        print("  - Server issues")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("This could be due to:")
        print("  - Network connectivity issues")
        print("  - Invalid website URL")
        print("  - Pagination limitations")


async def test_concurrent_pagination():
    """Test multiple pagination requests concurrently"""

    print("\n" + "=" * 50)
    print("Testing concurrent pagination requests")
    print("=" * 50)

    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return

    try:
        client = AsyncClient(api_key=api_key)
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return

    # Test concurrent requests
    urls = [
        "https://example.com/products?page=1",
        "https://example.com/products?page=2",
        "https://example.com/products?page=3",
    ]

    tasks = []
    for i, url in enumerate(urls):
        print(f"🚀 Creating task {i+1} for URL: {url}")
        # Note: In a real scenario, you would use actual URLs
        # This is just to demonstrate the async functionality
        tasks.append(
            asyncio.create_task(simulate_pagination_request(client, url, i + 1))
        )

    print(f"⏱️ Starting {len(tasks)} concurrent tasks...")
    start_time = time.time()

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time

        print(f"✅ All tasks completed in {duration:.2f} seconds")

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Task {i+1} failed: {result}")
            else:
                print(f"✅ Task {i+1} succeeded: {result}")

    except Exception as e:
        print(f"❌ Concurrent execution failed: {e}")


async def simulate_pagination_request(client: AsyncClient, url: str, task_id: int):
    """Simulate a pagination request (for demonstration)"""

    print(f"📋 Task {task_id}: Processing {url}")

    # Simulate some work
    await asyncio.sleep(0.5)

    # Return a simulated result
    return f"Task {task_id} completed successfully"


async def test_pagination_with_different_parameters():
    """Test pagination with different parameters"""

    print("\n" + "=" * 50)
    print("Testing pagination with different parameters")
    print("=" * 50)

    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return

    try:
        AsyncClient(api_key=api_key)
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return

    # Test cases
    test_cases = [
        {
            "name": "Single page (default)",
            "url": "https://example.com",
            "total_pages": None,
            "user_prompt": "Extract basic info",
        },
        {
            "name": "Two pages with schema",
            "url": "https://example.com/products",
            "total_pages": 2,
            "user_prompt": "Extract product information",
            "output_schema": ProductList,
        },
        {
            "name": "Maximum pages with scrolling",
            "url": "https://example.com/search",
            "total_pages": 5,
            "user_prompt": "Extract all available data",
            "number_of_scrolls": 3,
        },
    ]

    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        print(f"   Pages: {test_case['total_pages']}")
        print(f"   Prompt: {test_case['user_prompt']}")

        try:
            # This is just to demonstrate the API call structure
            # In a real scenario, you'd make actual API calls
            print("   ✅ Configuration valid")

        except Exception as e:
            print(f"   ❌ Configuration error: {e}")


async def main():
    """Main function to run the pagination examples"""

    print("ScrapeGraph SDK - SmartScraper Pagination Examples (Async)")
    print("=" * 60)

    # Run the main example
    await smartscraper_pagination_example()

    # Test concurrent pagination
    await test_concurrent_pagination()

    # Test different parameters
    await test_pagination_with_different_parameters()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("\nNext steps:")
    print("1. Set SGAI_API_KEY environment variable")
    print("2. Replace example URLs with real websites")
    print("3. Adjust total_pages parameter (1-10)")
    print("4. Customize user_prompt for your use case")
    print("5. Define output_schema for structured data")
    print("\nAsync-specific tips:")
    print("- Use asyncio.gather() for concurrent requests")
    print("- Consider rate limiting with asyncio.Semaphore")
    print("- Handle exceptions properly in async context")
    print("- Use proper context managers for cleanup")


if __name__ == "__main__":
    asyncio.run(main())
