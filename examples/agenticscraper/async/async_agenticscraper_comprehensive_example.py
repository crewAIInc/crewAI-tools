#!/usr/bin/env python3
"""
Comprehensive Async Agentic Scraper Example

This example demonstrates how to use the agentic scraper API endpoint
asynchronously to perform automated browser actions and scrape content 
with both AI extraction and non-AI extraction modes.

The agentic scraper can:
1. Navigate to a website
2. Perform a series of automated actions (like filling forms, clicking buttons)
3. Extract the resulting HTML content as markdown
4. Optionally use AI to extract structured data

Usage:
    python examples/async/async_agenticscraper_comprehensive_example.py
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

# Set logging level
sgai_logger.set_logging(level="INFO")


async def example_basic_scraping_no_ai():
    """Example: Basic agentic scraping without AI extraction."""
    
    # Initialize the async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return None

    async with AsyncClient(api_key=api_key) as client:
        # Define the steps to perform
        steps = [
            "Type email@gmail.com in email input box",
            "Type test-password@123 in password inputbox",
            "click on login",
        ]

        try:
            print("🚀 Starting basic async agentic scraping (no AI extraction)...")
            print(f"URL: https://dashboard.scrapegraphai.com/")
            print(f"Steps: {steps}")

            # Perform the scraping without AI extraction
            result = await client.agenticscraper(
                url="https://dashboard.scrapegraphai.com/",
                steps=steps,
                use_session=True,
                ai_extraction=False  # No AI extraction - just get raw markdown
            )

            print("✅ Basic async scraping completed successfully!")
            print(f"Request ID: {result.get('request_id')}")

            # Save the markdown content to a file
            if result.get("markdown"):
                with open("async_basic_scraped_content.md", "w", encoding="utf-8") as f:
                    f.write(result["markdown"])
                print("📄 Markdown content saved to 'async_basic_scraped_content.md'")

            # Print a preview of the content
            if result.get("markdown"):
                preview = (
                    result["markdown"][:500] + "..."
                    if len(result["markdown"]) > 500
                    else result["markdown"]
                )
                print(f"\n📝 Content Preview:\n{preview}")

            if result.get("error"):
                print(f"⚠️ Warning: {result['error']}")

            return result

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


async def example_ai_extraction():
    """Example: Use AI extraction to get structured data from dashboard."""

    # Initialize the async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return None

    async with AsyncClient(api_key=api_key) as client:
        # Define extraction schema for user dashboard information
        output_schema = {
            "user_info": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "dashboard_sections": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "account_status": {"type": "string"},
                    "credits_remaining": {"type": "number"}
                },
                "required": ["username", "dashboard_sections"]
            }
        }

        steps = [
            "Type email@gmail.com in email input box",
            "Type test-password@123 in password inputbox",
            "click on login",
            "wait for dashboard to load completely",
        ]

        try:
            print("🤖 Starting async agentic scraping with AI extraction...")
            print(f"URL: https://dashboard.scrapegraphai.com/")
            print(f"Steps: {steps}")

            result = await client.agenticscraper(
                url="https://dashboard.scrapegraphai.com/",
                steps=steps,
                use_session=True,
                user_prompt="Extract user information, available dashboard sections, account status, and remaining credits from the dashboard",
                output_schema=output_schema,
                ai_extraction=True
            )

            print("✅ Async AI extraction completed!")
            print(f"Request ID: {result.get('request_id')}")

            if result.get("result"):
                print("🎯 Extracted Structured Data:")
                print(json.dumps(result["result"], indent=2))
                
                # Save extracted data to JSON file
                with open("async_extracted_dashboard_data.json", "w", encoding="utf-8") as f:
                    json.dump(result["result"], f, indent=2)
                print("💾 Structured data saved to 'async_extracted_dashboard_data.json'")

            # Also save the raw markdown if available
            if result.get("markdown"):
                with open("async_ai_scraped_content.md", "w", encoding="utf-8") as f:
                    f.write(result["markdown"])
                print("📄 Raw markdown also saved to 'async_ai_scraped_content.md'")

            return result

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


async def example_multiple_sites_concurrently():
    """Example: Scrape multiple sites concurrently with different extraction modes."""

    # Initialize the async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return None

    async with AsyncClient(api_key=api_key) as client:
        # Define different scraping tasks
        tasks = [
            {
                "name": "Dashboard Login (No AI)",
                "url": "https://dashboard.scrapegraphai.com/",
                "steps": [
                    "Type email@gmail.com in email input box",
                    "Type test-password@123 in password inputbox",
                    "click on login"
                ],
                "ai_extraction": False
            },
            {
                "name": "Product Page (With AI)",
                "url": "https://example-store.com/products/laptop",
                "steps": [
                    "scroll down to product details",
                    "click on specifications tab",
                    "scroll down to reviews section"
                ],
                "ai_extraction": True,
                "user_prompt": "Extract product name, price, specifications, and customer review summary",
                "output_schema": {
                    "product": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "price": {"type": "string"},
                            "specifications": {"type": "object"},
                            "review_summary": {
                                "type": "object",
                                "properties": {
                                    "average_rating": {"type": "number"},
                                    "total_reviews": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            },
            {
                "name": "News Article (With AI)",
                "url": "https://example-news.com/tech-article",
                "steps": [
                    "scroll down to read full article",
                    "click on related articles section"
                ],
                "ai_extraction": True,
                "user_prompt": "Extract article title, author, publication date, main content summary, and related article titles",
                "output_schema": {
                    "article": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "author": {"type": "string"},
                            "publication_date": {"type": "string"},
                            "summary": {"type": "string"},
                            "related_articles": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        ]

        async def scrape_site(task):
            """Helper function to scrape a single site."""
            try:
                print(f"🚀 Starting: {task['name']}")
                
                kwargs = {
                    "url": task["url"],
                    "steps": task["steps"],
                    "use_session": True,
                    "ai_extraction": task["ai_extraction"]
                }
                
                if task["ai_extraction"]:
                    kwargs["user_prompt"] = task["user_prompt"]
                    kwargs["output_schema"] = task["output_schema"]
                
                result = await client.agenticscraper(**kwargs)
                
                print(f"✅ Completed: {task['name']} (Request ID: {result.get('request_id')})")
                return {
                    "task_name": task["name"],
                    "result": result,
                    "success": True
                }
                
            except Exception as e:
                print(f"❌ Failed: {task['name']} - {str(e)}")
                return {
                    "task_name": task["name"],
                    "error": str(e),
                    "success": False
                }

        try:
            print("🔄 Starting concurrent scraping of multiple sites...")
            print(f"📊 Total tasks: {len(tasks)}")
            
            # Run all scraping tasks concurrently
            results = await asyncio.gather(
                *[scrape_site(task) for task in tasks],
                return_exceptions=True
            )
            
            print("\n📋 Concurrent Scraping Results:")
            print("=" * 50)
            
            successful_results = []
            failed_results = []
            
            for result in results:
                if isinstance(result, Exception):
                    print(f"❌ Exception occurred: {str(result)}")
                    failed_results.append({"error": str(result)})
                elif result["success"]:
                    print(f"✅ {result['task_name']}: Success")
                    successful_results.append(result)
                    
                    # Save individual results
                    filename = f"concurrent_{result['task_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}_result.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(result["result"], f, indent=2)
                    print(f"   💾 Saved to: {filename}")
                else:
                    print(f"❌ {result['task_name']}: Failed - {result['error']}")
                    failed_results.append(result)
            
            # Save summary
            summary = {
                "total_tasks": len(tasks),
                "successful": len(successful_results),
                "failed": len(failed_results),
                "success_rate": f"{(len(successful_results) / len(tasks)) * 100:.1f}%",
                "results": results
            }
            
            with open("concurrent_scraping_summary.json", "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            print(f"\n📊 Summary saved to: concurrent_scraping_summary.json")
            print(f"   Success Rate: {summary['success_rate']}")
            
            return results

        except Exception as e:
            print(f"❌ Concurrent scraping error: {str(e)}")
            return None


async def example_step_by_step_with_ai():
    """Example: Step-by-step form interaction with AI extraction."""

    # Initialize the async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return None

    async with AsyncClient(api_key=api_key) as client:
        steps = [
            "navigate to contact page",
            "fill in name field with 'Jane Smith'",
            "fill in email field with 'jane.smith@company.com'",
            "select 'Business Inquiry' from dropdown",
            "fill in message: 'I would like to discuss enterprise pricing options for 100+ users'",
            "click on terms and conditions checkbox",
            "click submit button",
            "wait for success message and capture any reference number"
        ]

        output_schema = {
            "contact_form_result": {
                "type": "object",
                "properties": {
                    "submission_status": {"type": "string"},
                    "success_message": {"type": "string"},
                    "reference_number": {"type": "string"},
                    "next_steps": {"type": "string"},
                    "contact_info": {"type": "string"},
                    "estimated_response_time": {"type": "string"}
                },
                "required": ["submission_status", "success_message"]
            }
        }

        try:
            print("📝 Starting step-by-step form interaction with AI extraction...")
            print(f"URL: https://example-business.com/contact")
            print(f"Steps: {len(steps)} steps defined")

            result = await client.agenticscraper(
                url="https://example-business.com/contact",
                steps=steps,
                use_session=True,
                user_prompt="Extract the form submission result including status, success message, any reference number provided, next steps mentioned, contact information for follow-up, and estimated response time",
                output_schema=output_schema,
                ai_extraction=True
            )

            print("✅ Step-by-step form interaction completed!")
            print(f"Request ID: {result.get('request_id')}")

            if result and result.get("result"):
                form_result = result["result"].get("contact_form_result", {})
                
                print("\n📋 Form Submission Analysis:")
                print(f"   📊 Status: {form_result.get('submission_status', 'Unknown')}")
                print(f"   ✅ Message: {form_result.get('success_message', 'No message')}")
                
                if form_result.get('reference_number'):
                    print(f"   🔢 Reference: {form_result['reference_number']}")
                
                if form_result.get('next_steps'):
                    print(f"   👉 Next Steps: {form_result['next_steps']}")
                
                if form_result.get('contact_info'):
                    print(f"   📞 Contact Info: {form_result['contact_info']}")
                
                if form_result.get('estimated_response_time'):
                    print(f"   ⏰ Response Time: {form_result['estimated_response_time']}")
                
                # Save detailed results
                with open("async_step_by_step_form_result.json", "w", encoding="utf-8") as f:
                    json.dump(result["result"], f, indent=2)
                print("\n💾 Detailed results saved to 'async_step_by_step_form_result.json'")

            return result

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


async def main():
    """Main async function to run all examples."""
    print("🔧 Comprehensive Async Agentic Scraper Examples")
    print("=" * 60)

    # Check if API key is set
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("⚠️ Please set your SGAI_API_KEY environment variable before running!")
        print("You can either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return

    print("\n1. Basic Async Scraping (No AI Extraction)")
    print("-" * 50)
    await example_basic_scraping_no_ai()

    print("\n\n2. Async AI Extraction Example - Dashboard Data")
    print("-" * 50)
    await example_ai_extraction()

    print("\n\n3. Concurrent Multi-Site Scraping")
    print("-" * 50)
    # Uncomment to run concurrent scraping example
    # await example_multiple_sites_concurrently()

    print("\n\n4. Step-by-Step Form Interaction with AI")
    print("-" * 50)
    # Uncomment to run step-by-step form example
    # await example_step_by_step_with_ai()

    print("\n✨ Async examples completed!")
    print("\nℹ️ Note: Some examples are commented out by default.")
    print("   Uncomment them in the main function to run additional examples.")


if __name__ == "__main__":
    asyncio.run(main())
