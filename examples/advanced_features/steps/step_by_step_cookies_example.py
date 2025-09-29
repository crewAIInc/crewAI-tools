#!/usr/bin/env python3
"""
Step-by-Step Cookies Example

This example demonstrates the cookies integration process step by step, showing each stage
of setting up and executing a SmartScraper request with cookies for authentication.
"""

import json
import os
import time
from typing import Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraph_py import Client
from scrapegraph_py.exceptions import APIError

# Load environment variables from .env file
load_dotenv()


class CookieInfo(BaseModel):
    """Model representing cookie information."""

    cookies: Dict[str, str] = Field(description="Dictionary of cookie key-value pairs")


class UserProfile(BaseModel):
    """Model representing user profile information."""

    username: str = Field(description="User's username")
    email: Optional[str] = Field(description="User's email address")
    preferences: Optional[Dict[str, str]] = Field(description="User preferences")


def step_1_environment_setup():
    """Step 1: Set up environment and API key"""
    print("STEP 1: Environment Setup")
    print("=" * 40)

    # Check if API key is available
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return None

    print("✅ API key found in environment")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    return api_key


def step_2_client_initialization(api_key):
    """Step 2: Initialize the ScrapeGraph client"""
    print("\nSTEP 2: Client Initialization")
    print("=" * 40)

    try:
        client = Client(api_key=api_key)
        print("✅ Client initialized successfully")
        print(f"🔧 Client type: {type(client)}")
        return client
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return None


def step_3_define_schema():
    """Step 3: Define the output schema for structured data"""
    print("\nSTEP 3: Define Output Schema")
    print("=" * 40)

    print("📋 Defining Pydantic models for structured output:")
    print("   - CookieInfo: Cookie information structure")
    print("   - UserProfile: User profile data (for authenticated requests)")

    # Show the schema structure
    schema_example = CookieInfo.model_json_schema()
    print(f"✅ Schema defined with {len(schema_example['properties'])} properties")

    return CookieInfo


def step_4_prepare_cookies():
    """Step 4: Prepare cookies for authentication"""
    print("\nSTEP 4: Prepare Cookies")
    print("=" * 40)

    # Example cookies for different scenarios
    print("🍪 Preparing cookies for authentication...")

    # Basic test cookies
    basic_cookies = {"cookies_key": "cookies_value", "test_cookie": "test_value"}

    # Session cookies
    session_cookies = {"session_id": "abc123def456", "user_token": "xyz789ghi012"}

    # Authentication cookies
    auth_cookies = {
        "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "user_id": "user123",
        "csrf_token": "csrf_abc123",
    }

    print("📋 Available cookie sets:")
    print(f"   1. Basic cookies: {len(basic_cookies)} items")
    print(f"   2. Session cookies: {len(session_cookies)} items")
    print(f"   3. Auth cookies: {len(auth_cookies)} items")

    # Use basic cookies for this example
    selected_cookies = basic_cookies
    print(f"\n✅ Using basic cookies: {selected_cookies}")

    return selected_cookies


def step_5_format_cookies_for_headers(cookies):
    """Step 5: Format cookies for HTTP headers"""
    print("\nSTEP 5: Format Cookies for Headers")
    print("=" * 40)

    print("🔧 Converting cookies dictionary to HTTP Cookie header...")

    # Convert cookies dict to Cookie header string
    cookie_header = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    # Create headers dictionary
    headers = {"Cookie": cookie_header}

    print("📋 Cookie formatting:")
    print(f"   Original cookies: {cookies}")
    print(f"   Cookie header: {cookie_header}")
    print(f"   Headers dict: {headers}")

    return headers


def step_6_configure_request():
    """Step 6: Configure the request parameters"""
    print("\nSTEP 6: Configure Request Parameters")
    print("=" * 40)

    # Configuration parameters
    website_url = "https://httpbin.org/cookies"
    user_prompt = "Extract all cookies info"

    print("🌐 Website URL:")
    print(f"   {website_url}")
    print("\n📝 User Prompt:")
    print(f"   {user_prompt}")
    print("\n🔧 Additional Features:")
    print("   - Cookies authentication")
    print("   - Structured output schema")

    return {"website_url": website_url, "user_prompt": user_prompt}


def step_7_execute_request(client, config, headers, output_schema):
    """Step 7: Execute the request with cookies"""
    print("\nSTEP 7: Execute Request with Cookies")
    print("=" * 40)

    print("🚀 Starting request with cookies...")
    print("🍪 Cookies will be sent in HTTP headers")

    try:
        # Start timing
        start_time = time.time()

        # Perform the scraping with cookies
        result = client.smartscraper(
            website_url=config["website_url"],
            user_prompt=config["user_prompt"],
            headers=headers,
            output_schema=output_schema,
        )

        # Calculate duration
        duration = time.time() - start_time

        print(f"✅ Request completed in {duration:.2f} seconds")
        print(f"📊 Response type: {type(result)}")

        return result, duration

    except APIError as e:
        print(f"❌ API Error: {e}")
        print("This could be due to:")
        print("  - Invalid API key")
        print("  - Rate limiting")
        print("  - Server issues")
        return None, 0

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("This could be due to:")
        print("  - Network connectivity issues")
        print("  - Invalid website URL")
        print("  - Cookie format issues")
        return None, 0


def step_8_process_results(result, duration, cookies):
    """Step 8: Process and display the results"""
    print("\nSTEP 8: Process Results")
    print("=" * 40)

    if result is None:
        print("❌ No results to process")
        return

    print("📋 Processing cookies response...")

    # Display results
    if isinstance(result, dict):
        print("\n🔍 Response Structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Check if cookies were received correctly
        if "cookies" in result:
            received_cookies = result["cookies"]
            print(f"\n🍪 Cookies sent: {cookies}")
            print(f"🍪 Cookies received: {received_cookies}")

            # Verify cookies match
            if received_cookies == cookies:
                print("✅ Cookies match perfectly!")
            else:
                print("⚠️  Cookies don't match exactly (this might be normal)")

    elif isinstance(result, list):
        print(f"\n✅ Request successful! Extracted {len(result)} items")
        print("\n📦 Results:")
        for i, item in enumerate(result[:3]):  # Show first 3 items
            print(f"  {i+1}. {item}")

        if len(result) > 3:
            print(f"  ... and {len(result) - 3} more items")

    else:
        print(f"\n📋 Result: {result}")

    print(f"\n⏱️  Total processing time: {duration:.2f} seconds")


def step_9_test_different_scenarios(client, output_schema):
    """Step 9: Test different cookie scenarios"""
    print("\nSTEP 9: Test Different Cookie Scenarios")
    print("=" * 40)

    scenarios = [
        {
            "name": "Session Cookies",
            "cookies": {"session_id": "abc123", "user_token": "xyz789"},
            "description": "Basic session management",
        },
        {
            "name": "Authentication Cookies",
            "cookies": {"auth_token": "secret123", "preferences": "dark_mode"},
            "description": "User authentication and preferences",
        },
        {
            "name": "Complex Cookies",
            "cookies": {
                "session_id": "abc123def456",
                "user_id": "user789",
                "cart_id": "cart101112",
                "preferences": "dark_mode,usd",
            },
            "description": "E-commerce scenario with multiple cookies",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Testing Scenario {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Cookies: {scenario['cookies']}")

        # Format cookies for headers
        cookie_header = "; ".join([f"{k}={v}" for k, v in scenario["cookies"].items()])
        headers = {"Cookie": cookie_header}

        try:
            # Quick test request
            result = client.smartscraper(
                website_url="https://httpbin.org/cookies",
                user_prompt=f"Extract cookies for {scenario['name']}",
                headers=headers,
                output_schema=output_schema,
            )
            print(f"   ✅ Success: {type(result)}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}...")


def step_10_cleanup(client):
    """Step 10: Clean up resources"""
    print("\nSTEP 10: Cleanup")
    print("=" * 40)

    try:
        client.close()
        print("✅ Client session closed successfully")
        print("🔒 Resources freed")
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {e}")


def main():
    """Main function to run the step-by-step cookies example"""

    print("ScrapeGraph SDK - Step-by-Step Cookies Example")
    print("=" * 60)
    print("This example shows the complete process of setting up and")
    print("executing a SmartScraper request with cookies for authentication")
    print("=" * 60)

    # Step 1: Environment setup
    api_key = step_1_environment_setup()
    if not api_key:
        return

    # Step 2: Client initialization
    client = step_2_client_initialization(api_key)
    if not client:
        return

    # Step 3: Define schema
    output_schema = step_3_define_schema()

    # Step 4: Prepare cookies
    cookies = step_4_prepare_cookies()

    # Step 5: Format cookies for headers
    headers = step_5_format_cookies_for_headers(cookies)

    # Step 6: Configure request
    config = step_6_configure_request()

    # Step 7: Execute request
    result, duration = step_7_execute_request(client, config, headers, output_schema)

    # Step 8: Process results
    step_8_process_results(result, duration, cookies)

    # Step 9: Test different scenarios
    step_9_test_different_scenarios(client, output_schema)

    # Step 10: Cleanup
    step_10_cleanup(client)

    print("\n" + "=" * 60)
    print("Step-by-step cookies example completed!")
    print("\nKey takeaways:")
    print("1. Cookies are passed via HTTP headers")
    print("2. Cookie format: 'key1=value1; key2=value2'")
    print("3. Always validate your API key first")
    print("4. Test different cookie scenarios")
    print("5. Handle errors gracefully")
    print("\nCommon use cases:")
    print("- Authentication for protected pages")
    print("- Session management for dynamic content")
    print("- User preferences and settings")
    print("- Shopping cart and user state")
    print("\nNext steps:")
    print("- Try with real websites that require authentication")
    print("- Experiment with different cookie combinations")
    print("- Add error handling for production use")
    print("- Consider security implications of storing cookies")


if __name__ == "__main__":
    main()
