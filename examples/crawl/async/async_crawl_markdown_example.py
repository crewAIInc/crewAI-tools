#!/usr/bin/env python3
"""
Async example demonstrating the ScrapeGraphAI Crawler markdown conversion mode.

This example shows how to use the async crawler in markdown conversion mode:
- Cost-effective markdown conversion (NO AI/LLM processing)
- 2 credits per page (80% savings compared to AI mode)
- Clean HTML to markdown conversion with metadata extraction

Requirements:
- Python 3.7+
- scrapegraph-py
- aiohttp (installed with scrapegraph-py)
- A valid API key

Usage:
    python async_crawl_markdown_example.py
"""

import asyncio
import json
import os
from typing import Any, Dict

from scrapegraph_py import AsyncClient


async def poll_for_result(
    client: AsyncClient, crawl_id: str, max_attempts: int = 20
) -> Dict[str, Any]:
    """
    Poll for crawl results with intelligent backoff to avoid rate limits.

    Args:
        client: The async ScrapeGraph client
        crawl_id: The crawl ID to poll for
        max_attempts: Maximum number of polling attempts

    Returns:
        The final result or raises an exception on timeout/failure
    """
    print("⏳ Starting to poll for results with rate-limit protection...")

    # Initial wait to give the job time to start processing
    await asyncio.sleep(15)

    for attempt in range(max_attempts):
        try:
            result = await client.get_crawl(crawl_id)
            status = result.get("status")

            if status == "success":
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

    # Initialize the async client
    client = AsyncClient.from_env()

    # Target URL for markdown conversion
    url = "https://scrapegraphai.com/"

    print(f"🌐 Target URL: {url}")
    print("🤖 AI Prompt: None (no AI processing)")
    print("📊 Crawl Depth: 2")
    print("📄 Max Pages: 2")
    print("🗺️ Use Sitemap: False")
    print("💡 Mode: Pure HTML to markdown conversion")
    print()

    # Start the markdown conversion job
    print("🚀 Starting markdown conversion job...")

    # Call crawl with extraction_mode=False for markdown conversion
    response = await client.crawl(
        url=url,
        extraction_mode=False,  # FALSE = Markdown conversion mode (NO AI/LLM used)
        depth=2,
        max_pages=2,
        same_domain_only=True,
        sitemap=False,  # Use sitemap for better coverage
        # Note: No prompt or data_schema needed when extraction_mode=False
    )

    crawl_id = response.get("crawl_id") or response.get("task_id")

    if not crawl_id:
        print("❌ Failed to start markdown conversion job")
        return

    print(f"📋 Crawl ID: {crawl_id}")
    print("⏳ Polling for results...")
    print()

    # Poll for results with rate-limit protection
    try:
        result = await poll_for_result(client, crawl_id, max_attempts=20)

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
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("⚠️ Please set your API key in the environment variable SGAI_API_KEY")
        print("   export SGAI_API_KEY=your_api_key_here")
        print()
        print("   You can get your API key from: https://dashboard.scrapegraphai.com")
        return

    print(f"🔑 Using API key: {api_key[:10]}...")
    print()

    # Run the markdown conversion example
    await markdown_crawling_example()

    print("\n" + "=" * 60)
    print("🎉 Example completed!")
    print("💡 This demonstrates async markdown conversion mode:")
    print("   • Cost-effective: Only 2 credits per page")
    print("   • No AI/LLM processing - pure HTML to markdown conversion")
    print("   • Perfect for content archival and documentation")
    print("   • 80% cheaper than AI extraction modes!")


if __name__ == "__main__":
    asyncio.run(main())
