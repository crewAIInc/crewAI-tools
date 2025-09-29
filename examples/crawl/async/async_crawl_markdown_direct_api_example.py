#!/usr/bin/env python3
"""
Async example script demonstrating the ScrapeGraphAI Crawler markdown conversion mode.

This example shows how to use the crawler in markdown conversion mode:
- Cost-effective markdown conversion (NO AI/LLM processing)
- 2 credits per page (80% savings compared to AI mode)
- Clean HTML to markdown conversion with metadata extraction

Requirements:
- Python 3.7+
- aiohttp
- python-dotenv
- A .env file with your API_KEY

Example .env file:
API_KEY=your_api_key_here
"""

import asyncio
import json
import os
from typing import Any, Dict

import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration - API key from environment or fallback
API_KEY = os.getenv("TEST_API_KEY", "sgai-xxx")  # Load from .env file
BASE_URL = os.getenv("BASE_URL", "http://localhost:8001")  # Can be overridden via env


async def make_request(url: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Make an HTTP request to the API."""
    headers = {"Content-Type": "application/json", "SGAI-APIKEY": API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            return await response.json()


async def poll_result(task_id: str) -> Dict[str, Any]:
    """Poll for the result of a crawl job with rate limit handling."""
    headers = {"SGAI-APIKEY": API_KEY}
    url = f"{BASE_URL}/v1/crawl/{task_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 429:
                # Rate limited - return special status to handle in polling loop
                return {"status": "rate_limited", "retry_after": 60}
            return await response.json()


async def poll_with_backoff(task_id: str, max_attempts: int = 20) -> Dict[str, Any]:
    """
    Poll for crawl results with intelligent backoff to avoid rate limits.

    Args:
        task_id: The task ID to poll for
        max_attempts: Maximum number of polling attempts

    Returns:
        The final result or raises an exception on timeout/failure
    """
    print("⏳ Starting to poll for results with rate-limit protection...")

    # Initial wait to give the job time to start processing
    await asyncio.sleep(15)

    for attempt in range(max_attempts):
        try:
            result = await poll_result(task_id)
            status = result.get("status")

            if status == "rate_limited":
                wait_time = min(
                    90, 30 + (attempt * 10)
                )  # Exponential backoff for rate limits
                print(f"⚠️ Rate limited! Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
                continue

            elif status == "success":
                return result

            elif status == "failed":
                raise Exception(f"Crawl failed: {result.get('error', 'Unknown error')}")

            else:
                # Calculate progressive wait time: start at 15s, increase gradually
                base_wait = 15
                progressive_wait = min(60, base_wait + (attempt * 3))  # Cap at 60s

                print(
                    f"⏳ Status: {status} (attempt {attempt + 1}/{max_attempts}) - waiting {progressive_wait}s..."
                )
                await asyncio.sleep(progressive_wait)

        except Exception as e:
            if "rate" in str(e).lower() or "429" in str(e):
                wait_time = min(90, 45 + (attempt * 10))
                print(f"⚠️ Rate limit detected in error, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            else:
                print(f"❌ Error polling for results: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(20)  # Wait before retry
                    continue
                raise

    raise Exception(f"⏰ Timeout: Job did not complete after {max_attempts} attempts")


async def markdown_crawling_example():
    """
    Markdown Conversion Mode (NO AI/LLM Used)

    This example demonstrates cost-effective crawling that converts pages to clean markdown
    WITHOUT any AI processing. Perfect for content archival and when you only need clean markdown.
    """
    print("=" * 60)
    print("ASYNC MARKDOWN CONVERSION MODE (NO AI/LLM)")
    print("=" * 60)
    print("Use case: Get clean markdown content without AI processing")
    print("Cost: 2 credits per page (80% savings!)")
    print("Features: Clean markdown conversion, metadata extraction")
    print("⚠️ NO AI/LLM PROCESSING - Pure HTML to markdown conversion only!")
    print()

    # Markdown conversion request - NO AI/LLM processing
    request_data = {
        "url": "https://scrapegraphai.com/",
        "extraction_mode": False,  # FALSE = Markdown conversion mode (NO AI/LLM used)
        "depth": 2,
        "max_pages": 2,
        "same_domain_only": True,
        "sitemap": False,  # Use sitemap for better coverage
        # Note: No prompt needed when extraction_mode = False
    }

    print(f"🌐 Target URL: {request_data['url']}")
    print("🤖 AI Prompt: None (no AI processing)")
    print(f"📊 Crawl Depth: {request_data['depth']}")
    print(f"📄 Max Pages: {request_data['max_pages']}")
    print(f"🗺️ Use Sitemap: {request_data['sitemap']}")
    print("💡 Mode: Pure HTML to markdown conversion")
    print()

    # Start the markdown conversion job
    print("🚀 Starting markdown conversion job...")
    response = await make_request(f"{BASE_URL}/v1/crawl", request_data)
    task_id = response.get("task_id")

    if not task_id:
        print("❌ Failed to start markdown conversion job")
        return

    print(f"📋 Task ID: {task_id}")
    print("⏳ Polling for results...")
    print()

    # Poll for results with rate-limit protection
    try:
        result = await poll_with_backoff(task_id, max_attempts=20)

        print("✅ Markdown conversion completed successfully!")
        print()

        result_data = result.get("result", {})
        pages = result_data.get("pages", [])
        crawled_urls = result_data.get("crawled_urls", [])
        credits_used = result_data.get("credits_used", 0)
        pages_processed = result_data.get("pages_processed", 0)

        # Prepare JSON output
        json_output = {
            "conversion_results": {
                "pages_processed": pages_processed,
                "credits_used": credits_used,
                "cost_per_page": (
                    credits_used / pages_processed if pages_processed > 0 else 0
                ),
                "crawled_urls": crawled_urls,
            },
            "markdown_content": {"total_pages": len(pages), "pages": []},
        }

        # Add page details to JSON
        for i, page in enumerate(pages):
            metadata = page.get("metadata", {})
            page_data = {
                "page_number": i + 1,
                "url": page.get("url"),
                "title": page.get("title"),
                "metadata": {
                    "word_count": metadata.get("word_count", 0),
                    "headers": metadata.get("headers", []),
                    "links_count": metadata.get("links_count", 0),
                },
                "markdown_content": page.get("markdown", ""),
            }
            json_output["markdown_content"]["pages"].append(page_data)

        # Print JSON output
        print("📊 RESULTS IN JSON FORMAT:")
        print("-" * 40)
        print(json.dumps(json_output, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Markdown conversion failed: {str(e)}")


async def main():
    """Run the async markdown crawling example."""
    print("🌐 ScrapeGraphAI Async Crawler - Markdown Conversion Example")
    print("Cost-effective HTML to Markdown conversion (NO AI/LLM)")
    print("=" * 60)

    # Check if API key is set
    if API_KEY == "sgai-xxx":
        print("⚠️ Please set your API key in the .env file")
        print("   Create a .env file with your API key:")
        print("   API_KEY=your_api_key_here")
        print()
        print("   You can get your API key from: https://dashboard.scrapegraphai.com")
        print()
        print("   Example .env file:")
        print("   API_KEY=sgai-your-actual-api-key-here")
        print("   BASE_URL=https://api.scrapegraphai.com  # Optional")
        return

    print(f"🔑 Using API key: {API_KEY[:10]}...")
    print(f"🌐 Base URL: {BASE_URL}")
    print()

    # Run the single example
    await markdown_crawling_example()  # Markdown conversion mode (NO AI)

    print("\n" + "=" * 60)
    print("🎉 Example completed!")
    print("💡 This demonstrates async markdown conversion mode:")
    print("   • Cost-effective: Only 2 credits per page")
    print("   • No AI/LLM processing - pure HTML to markdown conversion")
    print("   • Perfect for content archival and documentation")
    print("   • 80% cheaper than AI extraction modes!")


if __name__ == "__main__":
    asyncio.run(main())
