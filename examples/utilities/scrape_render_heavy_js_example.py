"""
Comprehensive example demonstrating the render_heavy_js feature of the Scrape API.

This example shows:
1. The difference between regular and heavy JS rendering
2. How to handle JavaScript-heavy websites
3. When to use render_heavy_js=True vs render_heavy_js=False
4. Performance and cost implications
5. Direct API call equivalent (curl command)

The curl command equivalent to this example:
curl -X POST https://api.scrapegraphai.com/v1/scrape \
  -H "Content-Type: application/json" \
  -H "SGAI-APIKEY: your-api-key-here" \
  -d '{
    "website_url": "https://example.com",
    "render_heavy_js": true
  }'

Requirements:
- Python 3.7+
- scrapegraph-py
- python-dotenv
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from scrapegraph_py import Client

# Load environment variables from .env file
load_dotenv()


def scrape_with_comparison(
    client: Client,
    website_url: str,
    headers: dict = None
) -> Dict[str, Any]:
    """
    Compare scraping results with and without heavy JS rendering.
    
    Args:
        client: The scrapegraph-py client instance
        website_url: The URL to scrape
        headers: Optional headers to send with the request
        
    Returns:
        Dict containing comparison results
    """
    print(f"🌐 Scraping {website_url} with comparison...")
    print("=" * 60)
    
    results = {}
    
    # Test without heavy JS rendering (default)
    print("\n1️⃣ Scraping WITHOUT heavy JS rendering...")
    start_time = time.time()
    
    try:
        result_no_js = client.scrape(
            website_url=website_url,
            render_heavy_js=False,
            headers=headers
        )
        no_js_time = time.time() - start_time
        
        html_no_js = result_no_js.get("html", "")
        results["no_js"] = {
            "success": True,
            "html_length": len(html_no_js),
            "execution_time": no_js_time,
            "html_content": html_no_js,
            "result": result_no_js
        }
        
        print(f"✅ Completed in {no_js_time:.2f} seconds")
        print(f"📏 HTML length: {len(html_no_js):,} characters")
        
    except Exception as e:
        results["no_js"] = {
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time
        }
        print(f"❌ Failed: {str(e)}")
    
    # Test with heavy JS rendering
    print("\n2️⃣ Scraping WITH heavy JS rendering...")
    start_time = time.time()
    
    try:
        result_with_js = client.scrape(
            website_url=website_url,
            render_heavy_js=True,
            headers=headers
        )
        with_js_time = time.time() - start_time
        
        html_with_js = result_with_js.get("html", "")
        results["with_js"] = {
            "success": True,
            "html_length": len(html_with_js),
            "execution_time": with_js_time,
            "html_content": html_with_js,
            "result": result_with_js
        }
        
        print(f"✅ Completed in {with_js_time:.2f} seconds")
        print(f"📏 HTML length: {len(html_with_js):,} characters")
        
    except Exception as e:
        results["with_js"] = {
            "success": False,
            "error": str(e),
            "execution_time": time.time() - start_time
        }
        print(f"❌ Failed: {str(e)}")
    
    return results


def analyze_differences(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the differences between JS and non-JS rendering results.
    
    Args:
        results: Results from scrape_with_comparison
        
    Returns:
        Analysis results
    """
    print("\n🔍 ANALYSIS: Comparing Results")
    print("=" * 40)
    
    analysis = {}
    
    if results["no_js"]["success"] and results["with_js"]["success"]:
        no_js_html = results["no_js"]["html_content"]
        with_js_html = results["with_js"]["html_content"]
        
        # Length comparison
        length_diff = results["with_js"]["html_length"] - results["no_js"]["html_length"]
        length_percent = (length_diff / results["no_js"]["html_length"]) * 100 if results["no_js"]["html_length"] > 0 else 0
        
        # Time comparison
        time_diff = results["with_js"]["execution_time"] - results["no_js"]["execution_time"]
        time_percent = (time_diff / results["no_js"]["execution_time"]) * 100 if results["no_js"]["execution_time"] > 0 else 0
        
        # Content analysis
        no_js_scripts = no_js_html.lower().count("<script")
        with_js_scripts = with_js_html.lower().count("<script")
        
        no_js_divs = no_js_html.lower().count("<div")
        with_js_divs = with_js_html.lower().count("<div")
        
        analysis = {
            "length_difference": length_diff,
            "length_percent_change": length_percent,
            "time_difference": time_diff,
            "time_percent_change": time_percent,
            "script_tags_no_js": no_js_scripts,
            "script_tags_with_js": with_js_scripts,
            "div_tags_no_js": no_js_divs,
            "div_tags_with_js": with_js_divs,
        }
        
        print(f"📊 Content Length:")
        print(f"  Without JS: {results['no_js']['html_length']:,} chars")
        print(f"  With JS: {results['with_js']['html_length']:,} chars")
        print(f"  Difference: {length_diff:+,} chars ({length_percent:+.1f}%)")
        
        print(f"\n⏱️ Execution Time:")
        print(f"  Without JS: {results['no_js']['execution_time']:.2f}s")
        print(f"  With JS: {results['with_js']['execution_time']:.2f}s")
        print(f"  Difference: {time_diff:+.2f}s ({time_percent:+.1f}%)")
        
        print(f"\n🏷️ HTML Elements:")
        print(f"  Script tags - No JS: {no_js_scripts}, With JS: {with_js_scripts}")
        print(f"  Div tags - No JS: {no_js_divs}, With JS: {with_js_divs}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if length_diff > 1000:
            print("  ✅ Heavy JS rendering captured significantly more content")
            print("  ✅ Use render_heavy_js=True for this website")
        elif length_diff > 0:
            print("  ⚠️ Heavy JS rendering captured some additional content")
            print("  ⚠️ Consider using render_heavy_js=True if you need dynamic content")
        else:
            print("  ℹ️ No significant difference in content")
            print("  ℹ️ render_heavy_js=False is sufficient for this website")
            
        if time_diff > 5:
            print("  ⚠️ Heavy JS rendering is significantly slower")
            print("  ⚠️ Consider cost vs. benefit for your use case")
    
    else:
        print("❌ Cannot compare - one or both requests failed")
        if not results["no_js"]["success"]:
            print(f"   No JS error: {results['no_js'].get('error', 'Unknown')}")
        if not results["with_js"]["success"]:
            print(f"   With JS error: {results['with_js'].get('error', 'Unknown')}")
    
    return analysis


def save_comparison_results(results: Dict[str, Any], analysis: Dict[str, Any], website_url: str):
    """
    Save the comparison results to files.
    
    Args:
        results: Scraping results
        analysis: Analysis results
        website_url: The scraped website URL
    """
    print(f"\n💾 Saving comparison results...")
    
    # Create output directory
    output_dir = Path("render_heavy_js_comparison")
    output_dir.mkdir(exist_ok=True)
    
    # Save HTML files
    if results["no_js"]["success"]:
        no_js_file = output_dir / "scrape_no_js.html"
        with open(no_js_file, "w", encoding="utf-8") as f:
            f.write(results["no_js"]["html_content"])
        print(f"📄 No JS HTML saved to: {no_js_file}")
    
    if results["with_js"]["success"]:
        with_js_file = output_dir / "scrape_with_js.html"
        with open(with_js_file, "w", encoding="utf-8") as f:
            f.write(results["with_js"]["html_content"])
        print(f"📄 With JS HTML saved to: {with_js_file}")
    
    # Save analysis report
    report = {
        "website_url": website_url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results_summary": {
            "no_js_success": results["no_js"]["success"],
            "with_js_success": results["with_js"]["success"],
            "no_js_html_length": results["no_js"].get("html_length", 0),
            "with_js_html_length": results["with_js"].get("html_length", 0),
            "no_js_time": results["no_js"].get("execution_time", 0),
            "with_js_time": results["with_js"].get("execution_time", 0),
        },
        "analysis": analysis
    }
    
    report_file = output_dir / "comparison_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"📊 Analysis report saved to: {report_file}")


def demonstrate_curl_equivalent():
    """
    Show the curl command equivalent for the scrape API calls.
    """
    print(f"\n🌐 CURL COMMAND EQUIVALENTS")
    print("=" * 50)
    
    print("1️⃣ Scrape WITHOUT heavy JS rendering:")
    print("curl -X POST https://api.scrapegraphai.com/v1/scrape \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -H \"SGAI-APIKEY: your-api-key-here\" \\")
    print("  -d '{")
    print("    \"website_url\": \"https://example.com\",")
    print("    \"render_heavy_js\": false")
    print("  }'")
    
    print("\n2️⃣ Scrape WITH heavy JS rendering:")
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
    print("    \"render_heavy_js\": true,")
    print("    \"headers\": {")
    print("      \"User-Agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\",")
    print("      \"Accept-Language\": \"en-US,en;q=0.9\"")
    print("    }")
    print("  }'")


def main():
    """
    Main function demonstrating render_heavy_js functionality.
    """
    print("🚀 Scrape API: render_heavy_js Comparison Example")
    print("=" * 60)
    
    # Test websites - mix of static and dynamic content
    test_websites = [
        {
            "url": "https://example.com",
            "name": "Example.com (Static)",
            "description": "Simple static website - minimal JS"
        },
        {
            "url": "https://httpbin.org/html", 
            "name": "HTTPBin HTML",
            "description": "HTTP testing service - static HTML"
        }
    ]
    
    # Show curl equivalents first
    demonstrate_curl_equivalent()
    
    # Initialize client
    try:
        client = Client.from_env()
        print(f"\n✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {str(e)}")
        print("Make sure you have SGAI_API_KEY in your .env file")
        return
    
    # Test each website
    for website in test_websites:
        print(f"\n{'='*80}")
        print(f"🧪 TESTING: {website['name']}")
        print(f"📝 Description: {website['description']}")
        print(f"🔗 URL: {website['url']}")
        print(f"{'='*80}")
        
        try:
            # Perform comparison
            results = scrape_with_comparison(client, website["url"])
            
            # Analyze differences
            analysis = analyze_differences(results)
            
            # Save results
            save_comparison_results(results, analysis, website["url"])
            
        except Exception as e:
            print(f"❌ Error testing {website['url']}: {str(e)}")
    
    # Close client
    client.close()
    print(f"\n🔒 Client closed successfully")
    
    # Final recommendations
    print(f"\n💡 GENERAL RECOMMENDATIONS")
    print("=" * 30)
    print("🔹 Use render_heavy_js=False (default) for:")
    print("   • Static websites")
    print("   • Simple content sites")
    print("   • When speed is priority")
    print("   • When cost optimization is important")
    
    print("\n🔹 Use render_heavy_js=True for:")
    print("   • Single Page Applications (SPAs)")
    print("   • React/Vue/Angular websites")
    print("   • Sites with dynamic content loading")
    print("   • When you need JavaScript-rendered content")
    
    print("\n🔹 Cost considerations:")
    print("   • render_heavy_js=True takes longer and uses more resources")
    print("   • Test both options to determine if the extra content is worth it")
    print("   • Consider caching results for frequently accessed pages")


if __name__ == "__main__":
    main()
