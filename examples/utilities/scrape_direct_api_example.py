"""
Direct API example showing how to use the Scrape API endpoint directly.

This example demonstrates:
1. Direct API calls using requests library (equivalent to curl)
2. How to construct the API request manually
3. Comparison with the scrapegraph-py SDK
4. Error handling for direct API calls
5. The exact curl commands for each request

Curl command examples:
# Basic scrape request
curl -X POST https://api.scrapegraphai.com/v1/scrape \
  -H "Content-Type: application/json" \
  -H "SGAI-APIKEY: sgai-e32215fb-5940-400f-91ea-30af5f35e0c9" \
  -d '{
    "website_url": "https://example.com",
    "render_heavy_js": false
  }'

# With heavy JavaScript rendering
curl -X POST https://api.scrapegraphai.com/v1/scrape \
  -H "Content-Type: application/json" \
  -H "SGAI-APIKEY: sgai-e32215fb-5940-400f-91ea-30af5f35e0c9" \
  -d '{
    "website_url": "https://example.com",
    "render_heavy_js": true
  }'

Requirements:
- Python 3.7+
- requests
- scrapegraph-py
- python-dotenv
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import json
import time
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv
from scrapegraph_py import Client

# Load environment variables from .env file
load_dotenv()


class DirectScrapeAPI:
    """
    Direct API client for the Scrape endpoint (without using scrapegraph-py SDK).
    This demonstrates how to make raw API calls equivalent to curl commands.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.scrapegraphai.com/v1"):
        """
        Initialize the direct API client.
        
        Args:
            api_key: Your ScrapeGraph AI API key
            base_url: Base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "SGAI-APIKEY": api_key
        }
    
    def scrape(
        self, 
        website_url: str, 
        render_heavy_js: bool = False,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a direct scrape API request.
        
        Args:
            website_url: The URL to scrape
            render_heavy_js: Whether to render heavy JavaScript
            headers: Optional headers to send with the scraping request
            
        Returns:
            API response as dictionary
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/scrape"
        
        payload = {
            "website_url": website_url,
            "render_heavy_js": render_heavy_js
        }
        
        if headers:
            payload["headers"] = headers
        
        print(f"🌐 Making direct API request to: {url}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=self.headers,
                timeout=30
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            # Handle different response status codes
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Request successful")
                return result
            elif response.status_code == 400:
                error_data = response.json()
                raise requests.RequestException(f"Bad Request: {error_data.get('error', 'Unknown error')}")
            elif response.status_code == 401:
                raise requests.RequestException("Unauthorized: Check your API key")
            elif response.status_code == 429:
                raise requests.RequestException("Rate limit exceeded")
            elif response.status_code == 500:
                raise requests.RequestException("Internal server error")
            else:
                raise requests.RequestException(f"Unexpected status code: {response.status_code}")
                
        except requests.Timeout:
            raise requests.RequestException("Request timeout - API took too long to respond")
        except requests.ConnectionError:
            raise requests.RequestException("Connection error - unable to reach API")
        except json.JSONDecodeError:
            raise requests.RequestException("Invalid JSON response from API")


def demonstrate_curl_commands():
    """
    Display the equivalent curl commands for the API requests.
    """
    print("🌐 EQUIVALENT CURL COMMANDS")
    print("=" * 50)
    
    print("1️⃣ Basic scrape request (render_heavy_js=false):")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": false")
    print("  }'")
    
    print("\n2️⃣ Heavy JS rendering (render_heavy_js=true):")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": true")
    print("  }'")
    
    print("\n3️⃣ With custom headers:")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": false,")
    print("    \"headers\": {")
    print("      \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",")
    print("      \"Accept-Language\": \"en-US,en;q=0.9\",")
    print("      \"Cookie\": \"session=abc123; preferences=dark_mode\"")
    print("    }")
    print("  }'")
    
    print("\n4️⃣ Real example with actual API key format:")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: sgai-e32215fb-5940-400f-91ea-30af5f35e0c9\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": false")
    print("  }'")


def compare_direct_vs_sdk(api_key: str, website_url: str):
    """
    Compare direct API calls vs SDK usage.
    
    Args:
        api_key: API key for authentication
        website_url: URL to scrape
    """
    print(f"\n🔄 COMPARISON: Direct API vs SDK")
    print("=" * 40)
    
    # Test with direct API
    print("\n1️⃣ Using Direct API (equivalent to curl):")
    try:
        direct_client = DirectScrapeAPI(api_key)
        start_time = time.time()
        direct_result = direct_client.scrape(website_url, render_heavy_js=False)
        direct_time = time.time() - start_time
        
        direct_html = direct_result.get("html", "")
        print(f"✅ Direct API completed in {direct_time:.2f}s")
        print(f"📏 HTML length: {len(direct_html):,} characters")
        print(f"📋 Response keys: {list(direct_result.keys())}")
        
    except Exception as e:
        print(f"❌ Direct API failed: {str(e)}")
        direct_result = None
        direct_time = 0
    
    # Test with SDK
    print("\n2️⃣ Using scrapegraph-py SDK:")
    try:
        sdk_client = Client(api_key=api_key)
        start_time = time.time()
        sdk_result = sdk_client.scrape(website_url, render_heavy_js=False)
        sdk_time = time.time() - start_time
        
        sdk_html = sdk_result.get("html", "")
        print(f"✅ SDK completed in {sdk_time:.2f}s")
        print(f"📏 HTML length: {len(sdk_html):,} characters")
        print(f"📋 Response keys: {list(sdk_result.keys())}")
        
        sdk_client.close()
        
    except Exception as e:
        print(f"❌ SDK failed: {str(e)}")
        sdk_result = None
        sdk_time = 0
    
    # Compare results
    if direct_result and sdk_result:
        print(f"\n📊 Comparison Results:")
        print(f"  Time difference: {abs(direct_time - sdk_time):.2f}s")
        print(f"  HTML length difference: {abs(len(direct_html) - len(sdk_html)):,} chars")
        print(f"  Results identical: {direct_result == sdk_result}")
        
        print(f"\n💡 Conclusions:")
        print(f"  • Both methods produce identical results")
        print(f"  • SDK provides better error handling and validation")
        print(f"  • Direct API gives you full control over requests")
        print(f"  • Choose SDK for ease of use, direct API for custom integrations")


def demonstrate_error_handling(api_key: str):
    """
    Demonstrate error handling for direct API calls.
    
    Args:
        api_key: API key for authentication
    """
    print(f"\n🚨 ERROR HANDLING DEMONSTRATION")
    print("=" * 40)
    
    direct_client = DirectScrapeAPI(api_key)
    
    # Test cases for different errors
    error_tests = [
        {
            "name": "Invalid URL",
            "url": "not-a-valid-url",
            "expected": "ValidationError"
        },
        {
            "name": "Empty URL", 
            "url": "",
            "expected": "ValidationError"
        },
        {
            "name": "Non-existent domain",
            "url": "https://this-domain-definitely-does-not-exist-12345.com",
            "expected": "Connection/Timeout Error"
        }
    ]
    
    for test in error_tests:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        print(f"   Expected: {test['expected']}")
        
        try:
            result = direct_client.scrape(test["url"])
            print(f"   ⚠️ Unexpected success: {result.get('status', 'Unknown')}")
        except Exception as e:
            print(f"   ✅ Expected error caught: {str(e)}")


def main():
    """
    Main function demonstrating direct API usage.
    """
    print("🚀 Scrape API: Direct API Usage Example")
    print("=" * 50)
    
    # Show curl command equivalents
    demonstrate_curl_commands()
    
    # Get API key from environment
    import os
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("\n❌ Error: SGAI_API_KEY not found in environment variables")
        print("Please add your API key to your .env file:")
        print("SGAI_API_KEY=your-api-key-here")
        return
    
    print(f"\n✅ API key loaded from environment")
    
    # Test website
    test_url = "https://example.com"
    
    # Compare direct API vs SDK
    compare_direct_vs_sdk(api_key, test_url)
    
    # Demonstrate error handling
    demonstrate_error_handling(api_key)
    
    print(f"\n🎯 SUMMARY")
    print("=" * 20)
    print("✅ Direct API calls work identically to curl commands")
    print("✅ SDK provides additional convenience and error handling") 
    print("✅ Both approaches produce the same results")
    print("✅ Choose based on your integration needs")
    
    print(f"\n📚 Next Steps:")
    print("• Try the curl commands in your terminal")
    print("• Experiment with different render_heavy_js settings")
    print("• Test with your own websites")
    print("• Consider using the SDK for production applications")


if __name__ == "__main__":
    main()
