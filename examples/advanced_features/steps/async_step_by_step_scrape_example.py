"""
Async step-by-step example demonstrating how to use the Scrape API with the scrapegraph-py async SDK.

This example shows the basic async workflow:
1. Initialize the async client
2. Make a scrape request asynchronously
3. Handle the response
4. Save the HTML content
5. Basic analysis

Requirements:
- Python 3.7+
- scrapegraph-py
- python-dotenv
- aiohttp
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from scrapegraph_py import AsyncClient

# Load environment variables from .env file
load_dotenv()


async def step_1_initialize_async_client():
    """Step 1: Initialize the scrapegraph-py async client."""
    print("🔑 Step 1: Initializing async client...")
    
    try:
        # Initialize async client using environment variable
        client = AsyncClient.from_env()
        print("✅ Async client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize async client: {str(e)}")
        print("Make sure you have SGAI_API_KEY in your .env file")
        raise


async def step_2_make_async_scrape_request(client, url, render_js=False):
    """Step 2: Make a scrape request asynchronously."""
    print(f"\n🌐 Step 2: Making async scrape request to {url}")
    print(f"🔧 Render heavy JS: {render_js}")
    
    try:
        # Make the scrape request asynchronously
        result = await client.scrape(
            website_url=url,
            render_heavy_js=render_js
        )
        print("✅ Async scrape request completed successfully")
        return result
    except Exception as e:
        print(f"❌ Async scrape request failed: {str(e)}")
        raise


def step_3_handle_response(result):
    """Step 3: Handle and analyze the response."""
    print(f"\n📊 Step 3: Analyzing response...")
    
    # Check if we got HTML content
    html_content = result.get("html", "")
    if not html_content:
        print("❌ No HTML content received")
        return None
    
    # Basic response analysis
    print(f"✅ Received HTML content")
    print(f"📏 Content length: {len(html_content):,} characters")
    print(f"📄 Lines: {len(html_content.splitlines()):,}")
    
    # Check for common HTML elements
    has_doctype = html_content.strip().startswith("<!DOCTYPE")
    has_html = "<html" in html_content.lower()
    has_head = "<head" in html_content.lower()
    has_body = "<body" in html_content.lower()
    
    print(f"🏗️ Structure: DOCTYPE={has_doctype}, HTML={has_html}, HEAD={has_head}, BODY={has_body}")
    
    return html_content


def step_4_save_html_content(html_content, filename, output_dir="async_scrape_steps_output"):
    """Step 4: Save the HTML content to a file."""
    print(f"\n💾 Step 4: Saving HTML content...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save HTML file
    html_file = output_path / f"{filename}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ HTML content saved to: {html_file}")
    return html_file


def step_5_basic_analysis(html_content):
    """Step 5: Perform basic HTML analysis."""
    print(f"\n🔍 Step 5: Basic HTML analysis...")
    
    # Count common HTML elements
    elements = {
        "script": html_content.lower().count("<script"),
        "style": html_content.lower().count("<style"),
        "div": html_content.lower().count("<div"),
        "p": html_content.lower().count("<p"),
        "img": html_content.lower().count("<img"),
        "a": html_content.lower().count("<a"),
        "span": html_content.lower().count("<span"),
        "table": html_content.lower().count("<table"),
    }
    
    print("📊 Element counts:")
    for element, count in elements.items():
        if count > 0:
            print(f"  {element}: {count}")
    
    # Check for JavaScript and CSS
    has_js = elements["script"] > 0
    has_css = elements["style"] > 0
    
    print(f"\n🎨 Content types:")
    print(f"  JavaScript: {'Yes' if has_js else 'No'}")
    print(f"  CSS: {'Yes' if has_css else 'No'}")
    
    return elements


async def main():
    """Main function demonstrating async step-by-step scrape usage."""
    print("🚀 Async Step-by-Step Scrape API Example")
    print("=" * 55)
    
    # Test URL
    test_url = "https://example.com"
    
    try:
        # Step 1: Initialize async client
        async with AsyncClient.from_env() as client:
            print("✅ Async client initialized successfully")
            
            # Step 2: Make async scrape request
            result = await step_2_make_async_scrape_request(client, test_url, render_js=False)
            
            # Step 3: Handle response
            html_content = step_3_handle_response(result)
            if not html_content:
                print("❌ Cannot proceed without HTML content")
                return
            
            # Step 4: Save content
            filename = "async_example_website"
            saved_file = step_4_save_html_content(html_content, filename)
            
            # Step 5: Basic analysis
            elements = step_5_basic_analysis(html_content)
            
            # Summary
            print(f"\n🎯 Summary:")
            print(f"✅ Successfully processed {test_url} asynchronously")
            print(f"💾 HTML saved to: {saved_file}")
            print(f"📊 Analyzed {len(html_content):,} characters of HTML content")
            
            print("✅ Async client closed successfully")
        
    except Exception as e:
        print(f"\n💥 Error occurred: {str(e)}")
        print("Check your API key and internet connection")


if __name__ == "__main__":
    asyncio.run(main())
