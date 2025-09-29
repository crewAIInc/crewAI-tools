#!/usr/bin/env python3
"""
Async Step-by-Step SmartScraper Movements Example

This example demonstrates how to use interactive movements with SmartScraper API
using async/await patterns for better performance and concurrency.
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


async def check_server_connectivity(base_url: str) -> bool:
    """Check if the server is running and accessible"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try to access the health endpoint
            health_url = base_url.replace("/v1/smartscraper", "/healthz")
            response = await client.get(health_url)
            return response.status_code == 200
    except Exception:
        return False


async def async_smart_scraper_movements():
    """Async example of making a movements request to the smartscraper API"""

    # Load environment variables from .env file
    load_dotenv()

    # Get API key from .env file
    api_key = os.getenv("TEST_API_KEY")
    if not api_key:
        raise ValueError(
            "API key must be provided or set in .env file as TEST_API_KEY. "
            "Create a .env file with: TEST_API_KEY=your_api_key_here"
        )

    steps = [
        "click on search bar",
        "wait for 500ms",
        "fill email input box with mdehsan873@gmail.com",
        "wait a sec",
        "click on the first time of search result",
        "wait for 2 seconds to load the result of search",
    ]
    website_url = "https://github.com/"
    user_prompt = "Extract user profile"

    headers = {
        "SGAI-APIKEY": api_key,
        "Content-Type": "application/json",
    }

    body = {
        "website_url": website_url,
        "user_prompt": user_prompt,
        "output_schema": {},
        "steps": steps,
    }

    print("🚀 Starting Async Smart Scraper with Interactive Movements...")
    print(f"🌐 Website URL: {website_url}")
    print(f"🎯 User Prompt: {user_prompt}")
    print(f"📋 Steps: {len(steps)} interactive steps")
    print("\n" + "=" * 60)

    # Start timer
    start_time = time.time()
    print(
        f"⏱️  Timer started at: {time.strftime('%H:%M:%S', time.localtime(start_time))}"
    )
    print("🔄 Processing async request...")

    try:
        # Use longer timeout for movements requests as they may take more time
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                "http://localhost:8001/v1/smartscraper",
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
                        print(
                            json.dumps(result["result"], indent=2, ensure_ascii=False)
                        )
                    else:
                        print("No result data found")

            else:
                print(f"❌ Request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")

    except httpx.TimeoutException:
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time / 60
        print(
            f"⏱️  Timer stopped at: {time.strftime('%H:%M:%S', time.localtime(end_time))}"
        )
        print(
            f"⚡ Execution time before timeout: {execution_time:.2f} seconds ({execution_minutes:.2f} minutes)"
        )
        print("⏰ Request timed out after 300 seconds")
    except httpx.RequestError as e:
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


async def async_markdownify_movements():
    """
    Async enhanced markdownify function with comprehensive features and timing.

    Note: Markdownify doesn't support interactive movements like Smart Scraper.
    Instead, it excels at converting websites to clean markdown format.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Get API key from .env file
    api_key = os.getenv("TEST_API_KEY")
    if not api_key:
        raise ValueError(
            "API key must be provided or set in .env file as TEST_API_KEY. "
            "Create a .env file with: TEST_API_KEY=your_api_key_here"
        )

    steps = [
        "click on search bar",
        "wait for 500ms",
        "fill email input box with mdehsan873@gmail.com",
        "wait a sec",
        "click on the first time of search result",
        "wait for 2 seconds to load the result of search",
    ]

    # Target website configuration
    website_url = "https://scrapegraphai.com/"

    # Enhanced headers for better scraping (similar to interactive movements)
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # Prepare API request headers
    headers = {
        "SGAI-APIKEY": api_key,
        "Content-Type": "application/json",
    }

    # Request body for markdownify
    body = {
        "website_url": website_url,
        "headers": custom_headers,
        "steps": steps,
    }

    print("🚀 Starting Async Markdownify with Enhanced Features...")
    print(f"🌐 Website URL: {website_url}")
    print(f"📋 Custom Headers: {len(custom_headers)} headers configured")
    print("🎯 Goal: Convert website to clean markdown format")
    print("\n" + "=" * 60)

    # Start timer
    start_time = time.time()
    print(
        f"⏱️  Timer started at: {time.strftime('%H:%M:%S', time.localtime(start_time))}"
    )
    print("🔄 Processing async markdown conversion...")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:8001/v1/markdownify",
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
                f"📊 Performance: {execution_time:.1f}s ({execution_minutes:.1f}m) for markdown conversion"
            )

            if response.status_code == 200:
                result = response.json()
                markdown_content = result.get("result", "")

                print("✅ Request completed successfully!")
                print(f"📊 Request ID: {result.get('request_id', 'N/A')}")
                print(f"🔄 Status: {result.get('status', 'N/A')}")
                print(f"📝 Content Length: {len(markdown_content)} characters")

                if result.get("error"):
                    print(f"❌ Error: {result['error']}")
                else:
                    print("\n📋 MARKDOWN CONVERSION RESULTS:")
                    print("=" * 60)

                    # Display markdown statistics
                    lines = markdown_content.split("\n")
                    words = len(markdown_content.split())

                    print("📊 Statistics:")
                    print(f"   - Total Lines: {len(lines)}")
                    print(f"   - Total Words: {words}")
                    print(f"   - Total Characters: {len(markdown_content)}")
                    print(
                        f"   - Processing Speed: {len(markdown_content)/execution_time:.0f} chars/second"
                    )

                    # Display first 500 characters
                    print("\n🔍 First 500 characters:")
                    print("-" * 50)
                    print(markdown_content[:500])
                    if len(markdown_content) > 500:
                        print("...")
                    print("-" * 50)

                    # Save to file
                    filename = f"async_markdownify_output_{int(time.time())}.md"
                    await save_markdown_to_file_async(markdown_content, filename)

                    # Display content analysis
                    analyze_markdown_content(markdown_content)

            else:
                print(f"❌ Request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")

    except httpx.TimeoutException:
        end_time = time.time()
        execution_time = end_time - start_time
        execution_minutes = execution_time / 60
        print(
            f"⏱️  Timer stopped at: {time.strftime('%H:%M:%S', time.localtime(end_time))}"
        )
        print(
            f"⚡ Execution time before timeout: {execution_time:.2f} seconds ({execution_minutes:.2f} minutes)"
        )
        print("⏰ Request timed out after 120 seconds")
    except httpx.RequestError as e:
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


async def save_markdown_to_file_async(markdown_content: str, filename: str):
    """
    Save markdown content to a file with enhanced error handling (async version).

    Args:
        markdown_content: The markdown content to save
        filename: The name of the file to save to
    """
    try:
        # Use asyncio to run the file operation in a thread pool
        await asyncio.to_thread(_write_file_sync, markdown_content, filename)
        print(f"💾 Markdown saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving file: {str(e)}")


def _write_file_sync(markdown_content: str, filename: str):
    """Synchronous file writing function for asyncio.to_thread"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)


def analyze_markdown_content(markdown_content: str):
    """
    Analyze the markdown content and provide insights.

    Args:
        markdown_content: The markdown content to analyze
    """
    print("\n🔍 CONTENT ANALYSIS:")
    print("-" * 50)

    # Count different markdown elements
    lines = markdown_content.split("\n")
    headers = [line for line in lines if line.strip().startswith("#")]
    links = [line for line in lines if "[" in line and "](" in line]
    code_blocks = markdown_content.count("```")

    print(f"📑 Headers found: {len(headers)}")
    print(f"🔗 Links found: {len(links)}")
    print(
        f"💻 Code blocks: {code_blocks // 2}"
    )  # Divide by 2 since each block has opening and closing

    # Show first few headers if they exist
    if headers:
        print("\n📋 First few headers:")
        for i, header in enumerate(headers[:3]):
            print(f"   {i+1}. {header.strip()}")
        if len(headers) > 3:
            print(f"   ... and {len(headers) - 3} more")


def show_curl_equivalent():
    """Show the equivalent curl command for reference"""

    # Load environment variables from .env file
    load_dotenv()

    api_key = os.getenv("TEST_API_KEY", "your-api-key-here")
    curl_command = f"""
curl --location 'http://localhost:8001/v1/smartscraper' \\
--header 'SGAI-APIKEY: {api_key}' \\
--header 'Content-Type: application/json' \\
--data '{{
    "website_url": "https://github.com/",
    "user_prompt": "Extract user profile",
    "output_schema": {{}},
    "steps": [
        "click on search bar",
        "wait for 500ms",
        "fill email input box with mdehsan873@gmail.com",
        "wait a sec",
        "click on the first time of search result",
        "wait for 2 seconds to load the result of search"
    ]
}}'
    """

    print("Equivalent curl command:")
    print(curl_command)


async def main():
    """Main function to run the async movements examples"""
    total_start_time = time.time()
    logger.info("Starting Async SmartScraper Movements Examples")

    try:
        print("🎯 ASYNC SMART SCRAPER MOVEMENTS EXAMPLES")
        print("=" * 60)
        print("This example demonstrates async interactive movements with timing")
        print()

        # Show the curl equivalent
        show_curl_equivalent()

        print("\n" + "=" * 60)

        # Make the actual API requests
        print("1️⃣ Running SmartScraper Movements Example...")
        await async_smart_scraper_movements()

        print("\n" + "=" * 60)
        print("2️⃣ Running Markdownify Movements Example...")
        await async_markdownify_movements()

        total_duration = time.time() - total_start_time
        logger.info(
            f"Examples completed! Total execution time: {total_duration:.2f} seconds"
        )

        print("\n" + "=" * 60)
        print("Examples completed!")
        print(f"⏱️ Total execution time: {total_duration:.2f} seconds")
        print("\nKey takeaways:")
        print("1. Async/await provides better performance for I/O operations")
        print("2. Movements allow for interactive browser automation")
        print("3. Each step is executed sequentially")
        print("4. Timing is crucial for successful interactions")
        print("5. Error handling is important for robust automation")
        print("\nNext steps:")
        print("- Customize the steps for your specific use case")
        print("- Add more complex interactions")
        print("- Implement retry logic for failed steps")
        print("- Use structured output schemas for better data extraction")

    except Exception as e:
        print(f"💥 Error occurred: {str(e)}")
        print("\n🛠️ Troubleshooting:")
        print("1. Make sure your .env file contains TEST_API_KEY")
        print("2. Ensure the API server is running on localhost:8001")
        print("3. Check your internet connection")
        print("4. Verify the target website is accessible")


if __name__ == "__main__":
    asyncio.run(main())
