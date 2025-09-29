#!/usr/bin/env python3
"""
Example demonstrating how to use the Markdownify API with enhanced features.

This example shows how to:
1. Set up the API request for markdownify with custom headers
2. Make the API call to convert a website to markdown
3. Handle the response and save the markdown content
4. Display comprehensive results with statistics and timing

Note: Unlike Smart Scraper, Markdownify doesn't support interactive movements/steps.
It focuses on converting websites to clean markdown format.

Requirements:
- Python 3.7+
- requests
- python-dotenv
- A .env file with your TEST_API_KEY

Example .env file:
TEST_API_KEY=your_api_key_here
"""

import os
import time

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def markdownify_movements():
    """
    Enhanced markdownify function with comprehensive features and timing.

    Note: Markdownify doesn't support interactive movements like Smart Scraper.
    Instead, it excels at converting websites to clean markdown format.
    """
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

    print("🚀 Starting Markdownify with Enhanced Features...")
    print(f"🌐 Website URL: {website_url}")
    print(f"📋 Custom Headers: {len(custom_headers)} headers configured")
    print("🎯 Goal: Convert website to clean markdown format")
    print("\n" + "=" * 60)

    # Start timer
    start_time = time.time()
    print(
        f"⏱️  Timer started at: {time.strftime('%H:%M:%S', time.localtime(start_time))}"
    )
    print("🔄 Processing markdown conversion...")

    try:
        response = requests.post(
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
                filename = f"markdownify_output_{int(time.time())}.md"
                save_markdown_to_file(markdown_content, filename)

                # Display content analysis
                analyze_markdown_content(markdown_content)

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


def save_markdown_to_file(markdown_content: str, filename: str):
    """
    Save markdown content to a file with enhanced error handling.

    Args:
        markdown_content: The markdown content to save
        filename: The name of the file to save to
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"💾 Markdown saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving file: {str(e)}")


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
curl --location 'http://localhost:8001/v1/markdownify' \\
--header 'SGAI-APIKEY: {api_key}' \\
--header 'Content-Type: application/json' \\
--data '{{
    "website_url": "https://scrapegraphai.com/",
    "headers": {{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }},
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


def main():
    """
    Main function to run the markdownify movements example with timing.
    """
    try:
        print("🎯 MARKDOWNIFY MOVEMENTS EXAMPLE")
        print("=" * 60)
        print("Note: Markdownify converts websites to clean markdown format")
        print("Unlike Smart Scraper, it doesn't support interactive movements")
        print("but excels at creating readable markdown content.")
        print("This example includes comprehensive timing information.")
        print()

        # Show the curl equivalent
        show_curl_equivalent()

        print("\n" + "=" * 60)

        # Make the actual API request
        markdownify_movements()

        print("\n" + "=" * 60)
        print("Example completed!")
        print("\nKey takeaways:")
        print("1. Markdownify excels at converting websites to clean markdown")
        print("2. Custom headers can improve scraping success")
        print("3. Content analysis provides valuable insights")
        print("4. File saving enables content persistence")
        print("\nNext steps:")
        print("- Try different websites and content types")
        print("- Customize headers for specific websites")
        print("- Implement content filtering and processing")
        print("- Use the saved markdown files for further analysis")

    except Exception as e:
        print(f"💥 Error occurred: {str(e)}")
        print("\n🛠️ Troubleshooting:")
        print("1. Make sure your .env file contains TEST_API_KEY")
        print("2. Ensure the API server is running on localhost:8001")
        print("3. Check your internet connection")
        print("4. Verify the target website is accessible")


if __name__ == "__main__":
    main()
