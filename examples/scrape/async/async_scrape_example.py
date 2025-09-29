"""
Basic asynchronous example demonstrating how to use the Scrape API.

This example shows:
1. How to make async scrape requests
2. How to process multiple URLs concurrently
3. How to use render_heavy_js for JavaScript-heavy websites
4. How to add custom headers in async mode

Equivalent curl command:
curl -X POST https://api.scrapegraphai.com/v1/scrape \
  -H "Content-Type: application/json" \
  -H "SGAI-APIKEY: your-api-key-here" \
  -d '{
    "website_url": "https://example.com",
    "render_heavy_js": false
  }'

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
import time
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

from scrapegraph_py import AsyncClient

# Load environment variables from .env file
load_dotenv()


async def basic_async_scrape():
    """Demonstrate basic async scrape functionality."""
    print("🌐 Basic Async Scrape Example")
    print("=" * 35)
    
    async with AsyncClient.from_env() as client:
        try:
            print("Making basic async scrape request...")
            result = await client.scrape(
                website_url="https://example.com",
                render_heavy_js=False
            )
            
            html_content = result.get("html", "")
            print(f"✅ Success! Received {len(html_content):,} characters of HTML")
            print(f"Request ID: {result.get('request_id', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


async def async_scrape_with_heavy_js():
    """Demonstrate async scraping with heavy JavaScript rendering."""
    print("\n🚀 Async Heavy JavaScript Rendering Example")
    print("=" * 50)
    
    async with AsyncClient.from_env() as client:
        try:
            print("Making async scrape request with heavy JS rendering...")
            start_time = time.time()
            
            result = await client.scrape(
                website_url="https://example.com",
                render_heavy_js=True
            )
            
            execution_time = time.time() - start_time
            html_content = result.get("html", "")
            
            print(f"✅ Success! Received {len(html_content):,} characters of HTML")
            print(f"⏱️ Execution time: {execution_time:.2f} seconds")
            print(f"Request ID: {result.get('request_id', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


async def scrape_single_url(client: AsyncClient, url: str, use_js: bool = False) -> Dict[str, Any]:
    """Scrape a single URL with error handling."""
    try:
        result = await client.scrape(
            website_url=url,
            render_heavy_js=use_js
        )
        
        html_content = result.get("html", "")
        return {
            "url": url,
            "success": True,
            "html_length": len(html_content),
            "request_id": result.get("request_id"),
            "result": result
        }
        
    except Exception as e:
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "html_length": 0
        }


async def concurrent_scraping_example():
    """Demonstrate scraping multiple URLs concurrently."""
    print("\n⚡ Concurrent Scraping Example")
    print("=" * 35)
    
    # URLs to scrape concurrently
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://httpbin.org/json"
    ]
    
    async with AsyncClient.from_env() as client:
        print(f"Scraping {len(urls)} URLs concurrently...")
        start_time = time.time()
        
        # Create tasks for concurrent execution
        tasks = [scrape_single_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Process results
        successful = 0
        total_html_length = 0
        
        for result in results:
            if isinstance(result, Exception):
                print(f"❌ Exception: {result}")
                continue
                
            if result["success"]:
                successful += 1
                total_html_length += result["html_length"]
                print(f"✅ {result['url']}: {result['html_length']:,} chars")
            else:
                print(f"❌ {result['url']}: {result['error']}")
        
        print(f"\n📊 Results:")
        print(f"  Total time: {total_time:.2f} seconds")
        print(f"  Successful: {successful}/{len(urls)}")
        print(f"  Total HTML: {total_html_length:,} characters")
        print(f"  Average per URL: {total_time/len(urls):.2f} seconds")
        
        return results


async def async_scrape_with_custom_headers():
    """Demonstrate async scraping with custom headers."""
    print("\n🔧 Async Custom Headers Example")
    print("=" * 35)
    
    # Custom headers
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    async with AsyncClient.from_env() as client:
        try:
            print("Making async scrape request with custom headers...")
            result = await client.scrape(
                website_url="https://httpbin.org/headers",
                render_heavy_js=False,
                headers=custom_headers
            )
            
            html_content = result.get("html", "")
            print(f"✅ Success! Received {len(html_content):,} characters of HTML")
            print(f"Request ID: {result.get('request_id', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


async def save_html_to_file_async(html_content: str, filename: str):
    """Save HTML content to a file asynchronously."""
    output_dir = Path("async_scrape_output")
    output_dir.mkdir(exist_ok=True)
    
    file_path = output_dir / f"{filename}.html"
    
    # Use asyncio.to_thread for file I/O
    await asyncio.to_thread(
        lambda: file_path.write_text(html_content, encoding="utf-8")
    )
    
    print(f"💾 HTML saved to: {file_path}")
    return file_path


def demonstrate_curl_equivalent():
    """Show the equivalent curl commands."""
    print("🌐 Equivalent curl commands:")
    print("=" * 35)
    
    print("1. Basic async scrape (same as sync):")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": false")
    print("  }'")
    
    print("\n2. Multiple concurrent requests:")
    print("# Run multiple curl commands in parallel:")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{\"website_url\": \"https://example.com\"}' &")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{\"website_url\": \"https://httpbin.org/html\"}' &")
    print("wait  # Wait for all background jobs to complete")


async def main():
    """Main async function demonstrating scrape functionality."""
    print("🚀 Async Scrape API Examples")
    print("=" * 30)
    
    # Show curl equivalents first
    demonstrate_curl_equivalent()
    
    try:
        # Run async examples
        result1 = await basic_async_scrape()
        result2 = await async_scrape_with_heavy_js()
        result3 = await async_scrape_with_custom_headers()
        concurrent_results = await concurrent_scraping_example()
        
        # Save results if successful
        if result1:
            html1 = result1.get("html", "")
            if html1:
                await save_html_to_file_async(html1, "basic_async_scrape")
        
        if result3:
            html3 = result3.get("html", "")
            if html3:
                await save_html_to_file_async(html3, "custom_headers_async_scrape")
        
        print("\n🎯 Summary:")
        print(f"✅ Basic async scrape: {'Success' if result1 else 'Failed'}")
        print(f"✅ Heavy JS async scrape: {'Success' if result2 else 'Failed'}")
        print(f"✅ Custom headers async scrape: {'Success' if result3 else 'Failed'}")
        print(f"✅ Concurrent scraping: {'Success' if concurrent_results else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    print("\n📚 Next steps:")
    print("• Try running multiple curl commands in parallel")
    print("• Experiment with different concurrency levels")
    print("• Test with your own list of URLs")
    print("• Compare async vs sync performance for multiple URLs")


if __name__ == "__main__":
    asyncio.run(main())
