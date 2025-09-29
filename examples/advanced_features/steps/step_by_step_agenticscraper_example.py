#!/usr/bin/env python3
"""
Step-by-Step AgenticScraper Example

This example demonstrates how to use the AgenticScraper API for automated browser interactions.
It shows how to make actual HTTP requests with step-by-step browser actions.
"""

import json
import os
import time

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def agentic_scraper_request():
    """Example of making a request to the agentic scraper API"""

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

    print("🤖 Starting Agentic Scraper with Automated Actions...")
    print(f"🌐 Website URL: {website_url}")
    print(f"🔧 Use Session: True")
    print(f"📋 Steps: {len(steps)} automated actions")
    print("\n" + "=" * 60)

    # Start timer
    start_time = time.time()
    print(
        f"⏱️  Timer started at: {time.strftime('%H:%M:%S', time.localtime(start_time))}"
    )
    print("🔄 Processing request...")

    try:
        response = requests.post(
            "http://localhost:8001/v1/agentic-scrapper",
            json=body,
            headers=headers,
        )

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

        if response.status_code == 200:
            result = response.json()
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
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
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


def main():
    """Main function to run the agentic scraper example"""
    try:
        print("🤖 AGENTIC SCRAPER EXAMPLE")
        print("=" * 60)
        print("This example demonstrates automated browser interactions")
        print()

        # Show the curl equivalent
        show_curl_equivalent()

        print("\n" + "=" * 60)

        # Make the actual API request
        agentic_scraper_request()

        print("\n" + "=" * 60)
        print("Example completed!")
        print("\nKey takeaways:")
        print("1. Agentic scraper enables automated browser actions")
        print("2. Each step is executed sequentially")
        print("3. Session management allows for complex workflows")
        print("4. Perfect for login flows and form interactions")
        print("\nNext steps:")
        print("- Customize the steps for your specific use case")
        print("- Add more complex automation sequences")
        print("- Implement error handling for failed actions")
        print("- Use session management for multi-step workflows")

    except Exception as e:
        print(f"💥 Error occurred: {str(e)}")
        print("\n🛠️ Troubleshooting:")
        print("1. Make sure your .env file contains SGAI_API_KEY")
        print("2. Ensure the API server is running on localhost:8001")
        print("3. Check your internet connection")
        print("4. Verify the target website is accessible")


if __name__ == "__main__":
    main()
