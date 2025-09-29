"""
Async example demonstrating how to use the Scrape API with the scrapegraph-py SDK.

This example shows how to:
1. Set up the async client for Scrape
2. Make async API calls to get HTML content from websites
3. Handle responses and save HTML content
4. Demonstrate both regular and heavy JS rendering modes
5. Process multiple websites concurrently

Requirements:
- Python 3.7+
- scrapegraph-py
- python-dotenv
- aiofiles (for async file operations)
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from scrapegraph_py import AsyncClient

# Load environment variables from .env file
load_dotenv()


async def scrape_website(
    client: AsyncClient,
    website_url: str,
    render_heavy_js: bool = False,
    headers: Optional[dict[str, str]] = None,
) -> dict:
    """
    Get HTML content from a website using the async Scrape API.

    Args:
        client: The async scrapegraph-py client instance
        website_url: The URL of the website to get HTML from
        render_heavy_js: Whether to render heavy JavaScript (defaults to False)
        headers: Optional headers to send with the request

    Returns:
        dict: A dictionary containing the HTML content and metadata

    Raises:
        Exception: If the API request fails
    """
    js_mode = "with heavy JS rendering" if render_heavy_js else "without JS rendering"
    print(f"Getting HTML content from: {website_url}")
    print(f"Mode: {js_mode}")

    start_time = time.time()
    
    try:
        result = await client.scrape(
            website_url=website_url,
            render_heavy_js=render_heavy_js,
            headers=headers,
        )
        execution_time = time.time() - start_time
        print(f"Execution time: {execution_time:.2f} seconds")
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        raise


async def save_html_content(
    html_content: str, filename: str, output_dir: str = "async_scrape_output"
):
    """
    Save HTML content to a file asynchronously.

    Args:
        html_content: The HTML content to save
        filename: The name of the file (without extension)
        output_dir: The directory to save the file in
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Save HTML file
    html_file = output_path / f"{filename}.html"
    
    # Use asyncio to run file I/O in a thread pool
    await asyncio.to_thread(
        lambda: html_file.write_text(html_content, encoding="utf-8")
    )

    print(f"HTML content saved to: {html_file}")
    return html_file


def analyze_html_content(html_content: str) -> dict:
    """
    Analyze HTML content and provide basic statistics.

    Args:
        html_content: The HTML content to analyze

    Returns:
        dict: Basic statistics about the HTML content
    """
    stats = {
        "total_length": len(html_content),
        "lines": len(html_content.splitlines()),
        "has_doctype": html_content.strip().startswith("<!DOCTYPE"),
        "has_html_tag": "<html" in html_content.lower(),
        "has_head_tag": "<head" in html_content.lower(),
        "has_body_tag": "<body" in html_content.lower(),
        "script_tags": html_content.lower().count("<script"),
        "style_tags": html_content.lower().count("<style"),
        "div_tags": html_content.lower().count("<div"),
        "p_tags": html_content.lower().count("<p"),
        "img_tags": html_content.lower().count("<img"),
        "link_tags": html_content.lower().count("<link"),
    }

    return stats


async def process_website(
    client: AsyncClient,
    website: dict,
) -> dict:
    """
    Process a single website and return results.

    Args:
        client: The async client instance
        website: Website configuration dictionary

    Returns:
        dict: Processing results
    """
    print(f"\nProcessing: {website['description']}")
    print("-" * 40)

    try:
        # Get HTML content
        result = await scrape_website(
            client=client,
            website_url=website["url"],
            render_heavy_js=website["render_heavy_js"],
        )

        # Display response metadata
        print(f"Request ID: {result.get('scrape_request_id', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Error: {result.get('error', 'None')}")

        # Analyze HTML content
        html_content = result.get("html", "")
        if html_content:
            stats = analyze_html_content(html_content)
            print(f"\nHTML Content Analysis:")
            print(f"  Total length: {stats['total_length']:,} characters")
            print(f"  Lines: {stats['lines']:,}")
            print(f"  Has DOCTYPE: {stats['has_doctype']}")
            print(f"  Has HTML tag: {stats['has_html_tag']}")
            print(f"  Has Head tag: {stats['has_head_tag']}")
            print(f"  Has Body tag: {stats['has_body_tag']}")
            print(f"  Script tags: {stats['script_tags']}")
            print(f"  Style tags: {stats['style_tags']}")
            print(f"  Div tags: {stats['div_tags']}")
            print(f"  Paragraph tags: {stats['p_tags']}")
            print(f"  Image tags: {stats['img_tags']}")
            print(f"  Link tags: {stats['link_tags']}")

            # Save HTML content
            filename = f"{website['name']}_{'js' if website['render_heavy_js'] else 'nojs'}"
            saved_file = await save_html_content(html_content, filename)

            # Show first 500 characters as preview
            preview = html_content[:500].replace("\n", " ").strip()
            print(f"\nHTML Preview (first 500 chars):")
            print(f"  {preview}...")

            return {
                "success": True,
                "website": website["url"],
                "saved_file": str(saved_file),
                "stats": stats,
                "preview": preview
            }
        else:
            print("No HTML content received")
            return {
                "success": False,
                "website": website["url"],
                "error": "No HTML content received"
            }

    except Exception as e:
        print(f"Error processing {website['url']}: {str(e)}")
        return {
            "success": False,
            "website": website["url"],
            "error": str(e)
        }


async def main():
    """
    Main async function demonstrating Scrape API usage.
    """
    # Example websites to test
    test_websites = [
        {
            "url": "https://example.com",
            "name": "example",
            "render_heavy_js": False,
            "description": "Simple static website",
        },
        {
            "url": "https://httpbin.org/html",
            "name": "httpbin_html",
            "render_heavy_js": False,
            "description": "HTTP testing service",
        },
    ]

    print("Async Scrape API Example with scrapegraph-py SDK")
    print("=" * 60)

    # Initialize the async client
    try:
        async with AsyncClient.from_env() as client:
            print("✅ Async client initialized successfully")

            # Process websites concurrently
            print(f"\n🚀 Processing {len(test_websites)} websites concurrently...")
            
            tasks = [
                process_website(client, website)
                for website in test_websites
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Display summary
            print(f"\n📊 Processing Summary")
            print("=" * 40)
            
            successful = 0
            for result in results:
                if isinstance(result, Exception):
                    print(f"❌ Exception occurred: {result}")
                elif result["success"]:
                    successful += 1
                    print(f"✅ {result['website']}: {result['saved_file']}")
                else:
                    print(f"❌ {result['website']}: {result.get('error', 'Unknown error')}")
            
            print(f"\n🎯 Results: {successful}/{len(test_websites)} websites processed successfully")

    except Exception as e:
        print(f"❌ Failed to initialize async client: {str(e)}")
        print("Make sure you have SGAI_API_KEY in your .env file")
        return

    print("\n✅ Async processing completed")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
