#!/usr/bin/env python3
"""
Basic SearchScraper Markdown Example

This example demonstrates the simplest way to use the SearchScraper API
in markdown mode to search and scrape web pages, returning raw markdown content
instead of AI-extracted data.

Features demonstrated:
- Basic search and scrape with markdown output
- Simple error handling
- Minimal code approach
- Cost-effective: Only 2 credits per page (vs 10 credits for AI extraction)

Requirements:
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import os

from dotenv import load_dotenv

from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")


def main():
    """Run a basic SearchScraper example with markdown output."""
    print("🔍 Basic SearchScraper Markdown Example")
    print("=" * 50)

    # Initialize the client with API key from environment
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ SGAI_API_KEY not found in environment variables.")
        print("Please create a .env file with: SGAI_API_KEY=your_api_key_here")
        return False

    client = Client(api_key=api_key)

    try:
        # Configuration
        user_prompt = "Latest developments in artificial intelligence"
        num_results = 3

        print(f"📝 Query: {user_prompt}")
        print(f"📊 Results: {num_results} websites")
        print("🔧 Mode: Markdown conversion")
        print("💰 Cost: 2 credits per page (vs 10 for AI extraction)")

        # Send a searchscraper request in markdown mode
        response = client.searchscraper(
            user_prompt=user_prompt,
            num_results=num_results,
            extraction_mode=False,  # False = markdown mode, True = AI extraction mode
        )

        print("\n✅ SearchScraper markdown completed successfully!")
        print(f"📄 Request ID: {response.get('request_id', 'N/A')}")

        # For async requests, you would need to poll for results
        if 'request_id' in response:
            print("📝 This is an async request. Use get_searchscraper() to retrieve results.")
            print(f"🔍 Use: client.get_searchscraper('{response['request_id']}')")
        else:
            # If it's a sync response, display the results
            if 'markdown_content' in response:
                markdown_content = response.get("markdown_content", "")
                print(f"\n📝 Markdown Content Preview:")
                print(f"{markdown_content[:500]}{'...' if len(markdown_content) > 500 else ''}")

            if 'reference_urls' in response:
                print(f"\n🔗 References: {len(response.get('reference_urls', []))}")
                print("\n🔗 Reference URLs:")
                for i, url in enumerate(response.get("reference_urls", []), 1):
                    print(f"  {i}. {url}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    finally:
        # Close the client
        client.close()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

