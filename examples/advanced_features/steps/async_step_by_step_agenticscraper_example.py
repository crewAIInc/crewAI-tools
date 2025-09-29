#!/usr/bin/env python3
"""
Async Step-by-Step AgenticScraper Example

This example demonstrates how to use the AgenticScraper API asynchronously
for automated browser interactions with proper async/await patterns.
"""

import asyncio
import json
import os
import time

import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def agentic_scraper_request():
    """Example of making an async request to the agentic scraper API"""

    # Get API key from .env file
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key must be provided or set in .env file as SGAI_API_KEY. "
            "Create a .env file with: SGAI_API_KEY=your_api_key_here"
        )

    steps = [
        "Type email@gmail.com in email input box",
        "Type test-password@123 in password inputbox",
        "click on login"
    ]
    website_url = "https://dashboard.scrapegraphai.com/"

    headers = {
        "SGAI-APIKEY": api_key,
        "Content-Type": "application/json",
    }

    body = {
        "url": website_url,
        "use_session": True,
        "steps": steps,
    }

    print("🤖 Starting Async Agentic Scraper with Automated Actions...")
    print(f"🌐 Website URL: {website_url}")
    print(f"🔧 Use Session: True")
    print(f"📋 Steps: {len(steps)} automated actions")
    print("\n" + "=" * 60)

    # Start timer
    start_time = time.time()
    print(
        f"⏱️  Timer started at: {time.strftime('%H:%M:%S', time.localtime(start_time))}"
    )
    print("🔄 Processing request asynchronously...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/v1/agentic-scrapper",
                json=body,
                headers=headers,
            ) as response:
                # Calculate execution time
                end_time = time.time()
                execution_time = end_time - start_time
                execution_minutes = execution_time / 60

                print(
                    f"⏱️  Timer stopped at: {time.strftime('%H:%M:%S', time.localtime(end_time))}"
                )
                print(
                    f"⚡ Total execution time: {execution_time:.2f} seconds ({execution_minutes:.2f} minutes)"
                )
                print(
                    f"📊 Performance: {execution_time:.1f}s ({execution_minutes:.1f}m) for {len(steps)} steps"
                )

                if response.status == 200:
                    result = await response.json()
                    print("✅ Request completed successfully!")
                    print(f"📊 Request ID: {result.get('request_id', 'N/A')}")
                    print(f"🔄 Status: {result.get('status', 'N/A')}")

                    if result.get("error"):
                        print(f"❌ Error: {result['error']}")
                    else:
                        print("\n📋 EXTRACTED DATA:")
                        print("=" * 60)

                        # Pretty print the result with proper indentation
                        if "result" in result:
                            print(json.dumps(result["result"], indent=2, ensure_ascii=False))
                        else:
                            print("No result data found")

                else:
                    response_text = await response.text()
                    print(f"❌ Request failed with status code: {response.status}")
                    print(f"Response: {response_text}")

    except aiohttp.ClientError as e:
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time / 60
        print(
            f"⏱️  Timer stopped at: {time.strftime('%H:%M:%S', time.localtime(end_time))}"
        )
        print(
            f"⚡ Execution time before error: {execution_time:.2f} seconds ({execution_minutes:.2f} minutes)"
        )
        print(f"🌐 Network error: {str(e)}")
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time / 60
        print(
            f"⏱️  Timer stopped at: {time.strftime('%H:%M:%S', time.localtime(end_time))}"
        )
        print(
            f"⚡ Execution time before error: {execution_time:.2f} seconds ({execution_minutes:.2f} minutes)"
        )
        print(f"💥 Unexpected error: {str(e)}")


def show_curl_equivalent():
    """Show the equivalent curl command for reference"""

    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv("SGAI_API_KEY", "your-api-key-here")
    curl_command = f"""
curl --location 'http://localhost:8001/v1/agentic-scrapper' \\
--header 'SGAI-APIKEY: {api_key}' \\
--header 'Content-Type: application/json' \\
--data-raw '{{
    "url": "https://dashboard.scrapegraphai.com/",
    "use_session": true,
    "steps": [
        "Type email@gmail.com in email input box",
        "Type test-password@123 in password inputbox",
        "click on login"
    ]
}}'
    """

    print("Equivalent curl command:")
    print(curl_command)


async def main():
    """Main async function to run the agentic scraper example"""
    try:
        print("🤖 ASYNC AGENTIC SCRAPER EXAMPLE")
        print("=" * 60)
        print("This example demonstrates async automated browser interactions")
        print()

        # Show the curl equivalent
        show_curl_equivalent()

        print("\n" + "=" * 60)

        # Make the actual API request
        await agentic_scraper_request()

        print("\n" + "=" * 60)
        print("Example completed!")
        print("\nKey takeaways:")
        print("1. Async agentic scraper enables non-blocking automation")
        print("2. Each step is executed sequentially but asynchronously")
        print("3. Session management allows for complex workflows")
        print("4. Perfect for concurrent automation tasks")
        print("\nNext steps:")
        print("- Run multiple agentic scrapers concurrently")
        print("- Combine with other async operations")
        print("- Implement async error handling")
        print("- Use async session management for efficiency")

    except Exception as e:
        print(f"💥 Error occurred: {str(e)}")
        print("\n🛠️ Troubleshooting:")
        print("1. Make sure your .env file contains SGAI_API_KEY")
        print("2. Ensure the API server is running on localhost:8001")
        print("3. Check your internet connection")
        print("4. Verify the target website is accessible")


if __name__ == "__main__":
    asyncio.run(main())
