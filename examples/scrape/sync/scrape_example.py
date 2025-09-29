"""
Basic synchronous example demonstrating how to use the Scrape API.

This example shows:
1. How to make a basic scrape request
2. How to use render_heavy_js for JavaScript-heavy websites
3. How to add custom headers
4. How to handle the response

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
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import time
from pathlib import Path
from dotenv import load_dotenv

from scrapegraph_py import Client

# Load environment variables from .env file
load_dotenv()


def basic_scrape_example():
    """Demonstrate basic scrape functionality."""
    print("🌐 Basic Scrape Example")
    print("=" * 30)
    
    # Initialize client
    client = Client.from_env()
    
    try:
        # Basic scrape request
        print("Making basic scrape request...")
        result = client.scrape(
            website_url="https://example.com",
            render_heavy_js=False
        )
        
        # Display results
        html_content = result.get("html", "")
        print(f"✅ Success! Received {len(html_content):,} characters of HTML")
        print(f"Request ID: {result.get('request_id', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    finally:
        client.close()


def scrape_with_heavy_js():
    """Demonstrate scraping with heavy JavaScript rendering."""
    print("\n🚀 Heavy JavaScript Rendering Example")
    print("=" * 45)
    
    client = Client.from_env()
    
    try:
        print("Making scrape request with heavy JS rendering...")
        start_time = time.time()
        
        result = client.scrape(
            website_url="https://example.com",
            render_heavy_js=True  # Enable JavaScript rendering
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
    finally:
        client.close()


def scrape_with_custom_headers():
    """Demonstrate scraping with custom headers."""
    print("\n🔧 Custom Headers Example")
    print("=" * 30)
    
    client = Client.from_env()
    
    # Custom headers for better compatibility
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        print("Making scrape request with custom headers...")
        result = client.scrape(
            website_url="https://httpbin.org/html",
            render_heavy_js=False,
            headers=custom_headers
        )
        
        html_content = result.get("html", "")
        print(f"✅ Success! Received {len(html_content):,} characters of HTML")
        print(f"Request ID: {result.get('request_id', 'N/A')}")
        
        # Show a preview of the HTML
        preview = html_content[:200].replace('\n', ' ').strip()
        print(f"HTML Preview: {preview}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    finally:
        client.close()


def save_html_to_file(html_content: str, filename: str):
    """Save HTML content to a file."""
    output_dir = Path("scrape_output")
    output_dir.mkdir(exist_ok=True)
    
    file_path = output_dir / f"{filename}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"💾 HTML saved to: {file_path}")
    return file_path


def demonstrate_curl_equivalent():
    """Show the equivalent curl commands."""
    print("\n🌐 Equivalent curl commands:")
    print("=" * 35)
    
    print("1. Basic scrape:")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": false")
    print("  }'")
    
    print("\n2. With heavy JS rendering:")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": true")
    print("  }'")


def main():
    """Main function demonstrating scrape functionality."""
    print("🚀 Scrape API Examples")
    print("=" * 25)
    
    # Show curl equivalents first
    demonstrate_curl_equivalent()
    
    try:
        # Run examples
        result1 = basic_scrape_example()
        result2 = scrape_with_heavy_js()
        result3 = scrape_with_custom_headers()
        
        # Save results if successful
        if result1:
            html1 = result1.get("html", "")
            if html1:
                save_html_to_file(html1, "basic_scrape")
        
        if result3:
            html3 = result3.get("html", "")
            if html3:
                save_html_to_file(html3, "custom_headers_scrape")
        
        print("\n🎯 Summary:")
        print(f"✅ Basic scrape: {'Success' if result1 else 'Failed'}")
        print(f"✅ Heavy JS scrape: {'Success' if result2 else 'Failed'}")
        print(f"✅ Custom headers scrape: {'Success' if result3 else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    print("\n📚 Next steps:")
    print("• Try the curl commands in your terminal")
    print("• Experiment with different websites")
    print("• Test with your own custom headers")
    print("• Compare render_heavy_js=true vs false for dynamic sites")


if __name__ == "__main__":
    main()
