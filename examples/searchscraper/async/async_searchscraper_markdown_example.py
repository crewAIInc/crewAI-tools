#!/usr/bin/env python3
"""
Async SearchScraper Markdown Example

This example demonstrates using the async SearchScraper API in markdown mode
to search and scrape web pages, returning raw markdown content instead of
AI-extracted data.

Features demonstrated:
- Async search and scrape with markdown output
- Polling for async results
- Error handling with async operations
- Cost-effective: Only 2 credits per page (vs 10 credits for AI extraction)

Requirements:
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")


async def wait_for_completion(
    client: AsyncClient, request_id: str, max_wait_time: int = 60
) -> Optional[dict]:
    """
    Poll for completion of an async SearchScraper request.
    
    Args:
        client: The AsyncClient instance
        request_id: The request ID to poll for
        max_wait_time: Maximum time to wait in seconds
        
    Returns:
        The completed response or None if timeout
    """
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            result = await client.get_searchscraper(request_id)
            
            if result.get("status") == "completed":
                return result
            elif result.get("status") == "failed":
                print(f"❌ Request failed: {result.get('error', 'Unknown error')}")
                return None
            else:
                print(f"⏳ Status: {result.get('status', 'processing')}... waiting 5 seconds")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"⚠️ Error polling for results: {str(e)}")
            await asyncio.sleep(5)
    
    print("⏰ Timeout waiting for completion")
    return None


async def basic_searchscraper_markdown_example() -> bool:
    """
    Run a basic SearchScraper example with markdown output.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("🔍 Async SearchScraper Markdown Example")
    print("=" * 50)

    # Initialize the async client with API key from environment
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ SGAI_API_KEY not found in environment variables.")
        print("Please create a .env file with: SGAI_API_KEY=your_api_key_here")
        return False

    async with AsyncClient(api_key=api_key) as client:
        try:
            # Configuration
            user_prompt = "Latest developments in artificial intelligence"
            num_results = 3

            print(f"📝 Query: {user_prompt}")
            print(f"📊 Results: {num_results} websites")
            print("🔧 Mode: Markdown conversion")
            print("💰 Cost: 2 credits per page (vs 10 for AI extraction)")

            # Send a searchscraper request in markdown mode
            response = await client.searchscraper(
                user_prompt=user_prompt,
                num_results=num_results,
                extraction_mode=False,  # False = markdown mode, True = AI extraction mode
            )

            print(f"\n✅ SearchScraper request submitted successfully!")
            print(f"📄 Request ID: {response.get('request_id', 'N/A')}")

            # Check if this is an async request that needs polling
            if 'request_id' in response and 'status' not in response:
                print("⏳ Waiting for async processing to complete...")
                
                # Poll for completion
                final_result = await wait_for_completion(client, response['request_id'])
                
                if final_result:
                    response = final_result
                else:
                    print("❌ Failed to get completed results")
                    return False

            # Display results
            if response.get("status") == "completed":
                print("\n🎉 SearchScraper markdown completed successfully!")
                
                # Display markdown content (first 500 chars)
                markdown_content = response.get("markdown_content", "")
                if markdown_content:
                    print("\n📝 Markdown Content Preview:")
                    print(f"{markdown_content[:500]}{'...' if len(markdown_content) > 500 else ''}")
                else:
                    print("⚠️  No markdown content returned")

                # Display reference URLs
                reference_urls = response.get("reference_urls", [])
                if reference_urls:
                    print(f"\n🔗 References: {len(reference_urls)}")
                    print("\n🔗 Reference URLs:")
                    for i, url in enumerate(reference_urls, 1):
                        print(f"  {i}. {url}")
                else:
                    print("⚠️  No reference URLs returned")

                return True
            else:
                print(f"❌ Request not completed. Status: {response.get('status', 'unknown')}")
                return False

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False


async def main():
    """Main function to run the example."""
    success = await basic_searchscraper_markdown_example()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

