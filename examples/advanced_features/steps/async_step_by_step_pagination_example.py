#!/usr/bin/env python3
"""
Async Step-by-Step Pagination Example

This example demonstrates the pagination process step by step using async/await patterns,
showing each stage of setting up and executing a paginated SmartScraper request.
"""

import asyncio
import json
import logging
import os
import time

import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


async def step_1_environment_setup():
    """Step 1: Set up environment and API key"""
    print("STEP 1: Environment Setup")
    print("=" * 40)

    # Check if API key is available
    api_key = os.getenv("TEST_API_KEY")
    if not api_key:
        print("❌ Error: TEST_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export TEST_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: TEST_API_KEY=your-api-key-here")
        return None

    print("✅ API key found in environment")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    return api_key


async def step_2_server_connectivity_check(api_key):
    """Step 2: Check server connectivity"""
    print("\nSTEP 2: Server Connectivity Check")
    print("=" * 40)

    url = "http://localhost:8001/v1/smartscraper"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to access the health endpoint
            health_url = url.replace("/v1/smartscraper", "/healthz")
            response = await client.get(health_url)

            if response.status_code == 200:
                print("✅ Server is accessible")
                print(f"🔗 Health endpoint: {health_url}")
                return True
            else:
                print(
                    f"❌ Server health check failed with status {response.status_code}"
                )
                return False
    except Exception as e:
        print(f"❌ Server connectivity check failed: {e}")
        print("Please ensure the server is running:")
        print("  poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        return False


def step_3_define_request_parameters():
    """Step 3: Define the request parameters"""
    print("\nSTEP 3: Define Request Parameters")
    print("=" * 40)

    # Configuration parameters
    website_url = "https://www.amazon.in/s?k=tv&crid=1TEF1ZFVLU8R8&sprefix=t%2Caps%2C390&ref=nb_sb_noss_2"
    user_prompt = "Extract all product info including name, price, rating, image_url, and description"
    total_pages = 3

    print("🌐 Website URL:")
    print(f"   {website_url}")
    print("\n📝 User Prompt:")
    print(f"   {user_prompt}")
    print(f"\n📄 Total Pages: {total_pages}")
    print(f"📊 Expected Products: ~{total_pages * 20} (estimated)")

    return {
        "website_url": website_url,
        "user_prompt": user_prompt,
        "total_pages": total_pages,
    }


def step_4_prepare_headers(api_key):
    """Step 4: Prepare request headers"""
    print("\nSTEP 4: Prepare Request Headers")
    print("=" * 40)

    headers = {
        "sec-ch-ua-platform": '"macOS"',
        "SGAI-APIKEY": api_key,
        "Referer": "https://dashboard.scrapegraphai.com/",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    print("📋 Headers configured:")
    for key, value in headers.items():
        if key == "SGAI-APIKEY":
            print(f"   {key}: {value[:10]}...{value[-10:]}")  # Mask API key
        else:
            print(f"   {key}: {value}")

    return headers


async def step_5_execute_pagination_request(headers, config):
    """Step 5: Execute the pagination request"""
    print("\nSTEP 5: Execute Pagination Request")
    print("=" * 40)

    url = "http://localhost:8001/v1/smartscraper"

    # Request payload with pagination
    payload = {
        "website_url": config["website_url"],
        "user_prompt": config["user_prompt"],
        "output_schema": {},
        "total_pages": config["total_pages"],
    }

    print("🚀 Starting pagination request...")
    print("⏱️  This may take several minutes for multiple pages...")

    try:
        # Start timing
        start_time = time.time()

        # Use longer timeout for pagination requests as they may take more time
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(url, headers=headers, json=payload)

        # Calculate duration
        duration = time.time() - start_time

        print(f"✅ Request completed in {duration:.2f} seconds")
        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            return result, duration
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None, duration

    except httpx.TimeoutException:
        duration = time.time() - start_time
        print(f"❌ Request timed out after {duration:.2f} seconds (>600s timeout)")
        print(
            "This may indicate the server is taking too long to process the pagination request."
        )
        return None, duration

    except httpx.RequestError as e:
        duration = time.time() - start_time
        print(f"❌ Request error after {duration:.2f} seconds: {e}")
        print("Common causes:")
        print("  - Server is not running")
        print("  - Wrong port (check server logs)")
        print("  - Network connectivity issues")
        return None, duration

    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Unexpected error after {duration:.2f} seconds: {e}")
        return None, duration


def step_6_process_results(result, duration):
    """Step 6: Process and display the results"""
    print("\nSTEP 6: Process Results")
    print("=" * 40)

    if result is None:
        print("❌ No results to process")
        return

    print("📋 Processing pagination results...")

    # Display results based on type
    if isinstance(result, dict):
        print("\n🔍 Response Structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Check for pagination success indicators
        if "data" in result:
            print("\n✨ Pagination successful! Data extracted from multiple pages")

    elif isinstance(result, list):
        print(f"\n✅ Pagination successful! Extracted {len(result)} items")

        # Show first few items
        print("\n📦 Sample Results:")
        for i, item in enumerate(result[:3]):  # Show first 3 items
            print(f"  {i+1}. {item}")

        if len(result) > 3:
            print(f"  ... and {len(result) - 3} more items")

    else:
        print(f"\n📋 Result: {result}")

    print(f"\n⏱️  Total processing time: {duration:.2f} seconds")


def step_7_show_curl_equivalent(api_key, config):
    """Step 7: Show equivalent curl command"""
    print("\nSTEP 7: Equivalent curl Command")
    print("=" * 40)

    curl_command = f"""
curl --location 'http://localhost:8001/v1/smartscraper' \\
--header 'sec-ch-ua-platform: "macOS"' \\
--header 'SGAI-APIKEY: {api_key}' \\
--header 'Referer: https://dashboard.scrapegraphai.com/' \\
--header 'sec-ch-ua: "Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"' \\
--header 'sec-ch-ua-mobile: ?0' \\
--header 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \\
--header 'Accept: application/json' \\
--header 'Content-Type: application/json' \\
--data '{{
    "website_url": "{config['website_url']}",
    "user_prompt": "{config['user_prompt']}",
    "output_schema": {{}},
    "total_pages": {config['total_pages']}
}}'
    """

    print("Equivalent curl command:")
    print(curl_command)


async def main():
    """Main function to run the async step-by-step pagination example"""
    total_start_time = time.time()
    logger.info("Starting Async Step-by-Step Pagination Example")

    print("ScrapeGraph SDK - Async Step-by-Step Pagination Example")
    print("=" * 60)
    print("This example shows the complete async process of setting up and")
    print("executing a pagination request with SmartScraper API")
    print("=" * 60)

    # Step 1: Environment setup
    api_key = await step_1_environment_setup()
    if not api_key:
        return

    # Step 2: Server connectivity check
    server_ok = await step_2_server_connectivity_check(api_key)
    if not server_ok:
        return

    # Step 3: Define request parameters
    config = step_3_define_request_parameters()

    # Step 4: Prepare headers
    headers = step_4_prepare_headers(api_key)

    # Step 5: Execute request
    result, duration = await step_5_execute_pagination_request(headers, config)

    # Step 6: Process results
    step_6_process_results(result, duration)

    # Step 7: Show curl equivalent
    step_7_show_curl_equivalent(api_key, config)

    total_duration = time.time() - total_start_time
    logger.info(
        f"Example completed! Total execution time: {total_duration:.2f} seconds"
    )

    print("\n" + "=" * 60)
    print("Async step-by-step pagination example completed!")
    print(f"⏱️ Total execution time: {total_duration:.2f} seconds")
    print("\nKey takeaways:")
    print("1. Async/await provides better performance for I/O operations")
    print("2. Always validate your API key and server connectivity first")
    print("3. Define clear request parameters for structured data")
    print("4. Configure pagination parameters carefully")
    print("5. Handle errors gracefully with proper timeouts")
    print("6. Use equivalent curl commands for testing")
    print("\nNext steps:")
    print("- Try different websites and prompts")
    print("- Experiment with different page counts")
    print("- Add error handling for production use")
    print("- Consider rate limiting for large requests")
    print("- Implement retry logic for failed requests")


if __name__ == "__main__":
    asyncio.run(main())
