#!/usr/bin/env python3
"""
Async Step-by-Step Cookies Example

This example demonstrates how to use cookies with SmartScraper API using async/await patterns.
It shows how to set up and execute requests with custom cookies for authentication and session management.
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


def step_3_define_cookies():
    """Step 3: Define cookies for authentication"""
    print("\nSTEP 3: Define Cookies")
    print("=" * 40)

    # Example cookies for a website that requires authentication
    cookies = {
        "session_id": "abc123def456ghi789",
        "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "remember_me": "true",
        "language": "en",
        "theme": "dark",
    }

    print("🍪 Cookies configured:")
    for key, value in cookies.items():
        if "token" in key.lower():
            # Mask sensitive tokens
            masked_value = value[:20] + "..." if len(value) > 20 else value
            print(f"   {key}: {masked_value}")
        else:
            print(f"   {key}: {value}")

    print(f"\n📊 Total cookies: {len(cookies)}")
    return cookies


def step_4_define_request_parameters():
    """Step 4: Define the request parameters"""
    print("\nSTEP 4: Define Request Parameters")
    print("=" * 40)

    # Configuration parameters
    website_url = "https://example.com/dashboard"
    user_prompt = "Extract user profile information and account details"

    print("🌐 Website URL:")
    print(f"   {website_url}")
    print("\n📝 User Prompt:")
    print(f"   {user_prompt}")
    print("\n🎯 Goal: Access authenticated content using cookies")

    return {"website_url": website_url, "user_prompt": user_prompt}


def step_5_prepare_headers(api_key):
    """Step 5: Prepare request headers"""
    print("\nSTEP 5: Prepare Request Headers")
    print("=" * 40)

    headers = {
        "SGAI-APIKEY": api_key,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    print("📋 Headers configured:")
    for key, value in headers.items():
        if key == "SGAI-APIKEY":
            print(f"   {key}: {value[:10]}...{value[-10:]}")  # Mask API key
        else:
            print(f"   {key}: {value}")

    return headers


async def step_6_execute_cookies_request(headers, cookies, config):
    """Step 6: Execute the request with cookies"""
    print("\nSTEP 6: Execute Request with Cookies")
    print("=" * 40)

    url = "http://localhost:8001/v1/smartscraper"

    # Request payload with cookies
    payload = {
        "website_url": config["website_url"],
        "user_prompt": config["user_prompt"],
        "output_schema": {},
        "cookies": cookies,
    }

    print("🚀 Starting request with cookies...")
    print("🍪 Using authentication cookies for access...")

    try:
        # Start timing
        start_time = time.time()

        # Use timeout for cookies requests
        async with httpx.AsyncClient(timeout=120.0) as client:
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
        print(f"❌ Request timed out after {duration:.2f} seconds (>120s timeout)")
        print("This may indicate authentication issues or slow response.")
        return None, duration

    except httpx.RequestError as e:
        duration = time.time() - start_time
        print(f"❌ Request error after {duration:.2f} seconds: {e}")
        print("Common causes:")
        print("  - Server is not running")
        print("  - Invalid cookies")
        print("  - Network connectivity issues")
        return None, duration

    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Unexpected error after {duration:.2f} seconds: {e}")
        return None, duration


def step_7_process_results(result, duration):
    """Step 7: Process and display the results"""
    print("\nSTEP 7: Process Results")
    print("=" * 40)

    if result is None:
        print("❌ No results to process")
        return

    print("📋 Processing authenticated results...")

    # Display results based on type
    if isinstance(result, dict):
        print("\n🔍 Response Structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Check for authentication success indicators
        if "result" in result:
            print("\n✨ Authentication successful! Data extracted with cookies")

    elif isinstance(result, list):
        print(f"\n✅ Authentication successful! Extracted {len(result)} items")

        # Show first few items
        print("\n📦 Sample Results:")
        for i, item in enumerate(result[:3]):  # Show first 3 items
            print(f"  {i+1}. {item}")

        if len(result) > 3:
            print(f"  ... and {len(result) - 3} more items")

    else:
        print(f"\n📋 Result: {result}")

    print(f"\n⏱️  Total processing time: {duration:.2f} seconds")


def step_8_show_curl_equivalent(api_key, cookies, config):
    """Step 8: Show equivalent curl command"""
    print("\nSTEP 8: Equivalent curl Command")
    print("=" * 40)

    # Convert cookies dict to curl format
    cookies_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    curl_command = f"""
curl --location 'http://localhost:8001/v1/smartscraper' \\
--header 'SGAI-APIKEY: {api_key}' \\
--header 'Content-Type: application/json' \\
--header 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36' \\
--header 'Accept: application/json' \\
--header 'Accept-Language: en-US,en;q=0.9' \\
--header 'Accept-Encoding: gzip, deflate, br' \\
--header 'Connection: keep-alive' \\
--cookie '{cookies_str}' \\
--data '{{
    "website_url": "{config['website_url']}",
    "user_prompt": "{config['user_prompt']}",
    "output_schema": {{}},
    "cookies": {json.dumps(cookies)}
}}'
    """

    print("Equivalent curl command:")
    print(curl_command)


def step_9_cookie_management_tips():
    """Step 9: Provide cookie management tips"""
    print("\nSTEP 9: Cookie Management Tips")
    print("=" * 40)

    print("🍪 Best Practices for Cookie Management:")
    print("1. 🔐 Store sensitive cookies securely (environment variables)")
    print("2. ⏰ Set appropriate expiration times")
    print("3. 🧹 Clean up expired cookies regularly")
    print("4. 🔄 Refresh tokens before they expire")
    print("5. 🛡️ Use HTTPS for cookie transmission")
    print("6. 📝 Log cookie usage for debugging")
    print("7. 🚫 Don't hardcode cookies in source code")
    print("8. 🔍 Validate cookie format before sending")


async def main():
    """Main function to run the async step-by-step cookies example"""
    total_start_time = time.time()
    logger.info("Starting Async Step-by-Step Cookies Example")

    print("ScrapeGraph SDK - Async Step-by-Step Cookies Example")
    print("=" * 60)
    print("This example shows the complete async process of setting up and")
    print("executing requests with cookies for authentication")
    print("=" * 60)

    # Step 1: Environment setup
    api_key = await step_1_environment_setup()
    if not api_key:
        return

    # Step 2: Server connectivity check
    server_ok = await step_2_server_connectivity_check(api_key)
    if not server_ok:
        return

    # Step 3: Define cookies
    cookies = step_3_define_cookies()

    # Step 4: Define request parameters
    config = step_4_define_request_parameters()

    # Step 5: Prepare headers
    headers = step_5_prepare_headers(api_key)

    # Step 6: Execute request
    result, duration = await step_6_execute_cookies_request(headers, cookies, config)

    # Step 7: Process results
    step_7_process_results(result, duration)

    # Step 8: Show curl equivalent
    step_8_show_curl_equivalent(api_key, cookies, config)

    # Step 9: Cookie management tips
    step_9_cookie_management_tips()

    total_duration = time.time() - total_start_time
    logger.info(
        f"Example completed! Total execution time: {total_duration:.2f} seconds"
    )

    print("\n" + "=" * 60)
    print("Async step-by-step cookies example completed!")
    print(f"⏱️ Total execution time: {total_duration:.2f} seconds")
    print("\nKey takeaways:")
    print("1. Async/await provides better performance for I/O operations")
    print("2. Cookies enable access to authenticated content")
    print("3. Always validate API key and server connectivity first")
    print("4. Secure cookie storage is crucial for production use")
    print("5. Handle authentication errors gracefully")
    print("6. Use equivalent curl commands for testing")
    print("\nNext steps:")
    print("- Implement secure cookie storage")
    print("- Add cookie refresh logic")
    print("- Handle authentication failures")
    print("- Monitor cookie expiration")
    print("- Implement retry logic for failed requests")


if __name__ == "__main__":
    asyncio.run(main())
