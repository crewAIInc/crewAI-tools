#!/usr/bin/env python3
"""
Comprehensive Agentic Scraper Example

This example demonstrates how to use the agentic scraper API endpoint
to perform automated browser actions and scrape content with both
AI extraction and non-AI extraction modes.

The agentic scraper can:
1. Navigate to a website
2. Perform a series of automated actions (like filling forms, clicking buttons)
3. Extract the resulting HTML content as markdown
4. Optionally use AI to extract structured data

Usage:
    python examples/sync/agenticscraper_comprehensive_example.py
"""

import json
import os
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv

from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

# Set logging level
sgai_logger.set_logging(level="INFO")


def example_basic_scraping_no_ai():
    """Example: Basic agentic scraping without AI extraction."""
    
    # Initialize the client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return None

    client = Client(api_key=api_key)

    # Define the steps to perform
    steps = [
        "Type email@gmail.com in email input box",
        "Type test-password@123 in password inputbox",
        "click on login",
    ]

    try:
        print("🚀 Starting basic agentic scraping (no AI extraction)...")
        print(f"URL: https://dashboard.scrapegraphai.com/")
        print(f"Steps: {steps}")

        # Perform the scraping without AI extraction
        result = client.agenticscraper(
            url="https://dashboard.scrapegraphai.com/",
            steps=steps,
            use_session=True,
            ai_extraction=False  # No AI extraction - just get raw markdown
        )

        print("✅ Basic scraping completed successfully!")
        print(f"Request ID: {result.get('request_id')}")

        # Save the markdown content to a file
        if result.get("markdown"):
            with open("basic_scraped_content.md", "w", encoding="utf-8") as f:
                f.write(result["markdown"])
            print("📄 Markdown content saved to 'basic_scraped_content.md'")

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
    finally:
        client.close()


def example_ai_extraction():
    """Example: Use AI extraction to get structured data from dashboard."""

    # Initialize the client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return None

    client = Client(api_key=api_key)

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
        print("🤖 Starting agentic scraping with AI extraction...")
        print(f"URL: https://dashboard.scrapegraphai.com/")
        print(f"Steps: {steps}")

        result = client.agenticscraper(
            url="https://dashboard.scrapegraphai.com/",
            steps=steps,
            use_session=True,
            user_prompt="Extract user information, available dashboard sections, account status, and remaining credits from the dashboard",
            output_schema=output_schema,
            ai_extraction=True
        )

        print("✅ AI extraction completed!")
        print(f"Request ID: {result.get('request_id')}")

        if result.get("result"):
            print("🎯 Extracted Structured Data:")
            print(json.dumps(result["result"], indent=2))
            
            # Save extracted data to JSON file
            with open("extracted_dashboard_data.json", "w", encoding="utf-8") as f:
                json.dump(result["result"], f, indent=2)
            print("💾 Structured data saved to 'extracted_dashboard_data.json'")

        # Also save the raw markdown if available
        if result.get("markdown"):
            with open("ai_scraped_content.md", "w", encoding="utf-8") as f:
                f.write(result["markdown"])
            print("📄 Raw markdown also saved to 'ai_scraped_content.md'")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    finally:
        client.close()


def example_ecommerce_product_scraping():
    """Example: Scraping an e-commerce site for product information."""

    # Initialize the client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return None

    client = Client(api_key=api_key)

    steps = [
        "click on search box",
        "type 'laptop' in search box",
        "press enter",
        "wait for search results to load",
        "scroll down 3 times to load more products",
    ]

    output_schema = {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "string"},
                    "rating": {"type": "number"},
                    "availability": {"type": "string"},
                    "description": {"type": "string"},
                    "image_url": {"type": "string"}
                },
                "required": ["name", "price"]
            }
        },
        "search_info": {
            "type": "object",
            "properties": {
                "total_results": {"type": "number"},
                "search_term": {"type": "string"},
                "page": {"type": "number"}
            }
        }
    }

    try:
        print("🛒 Scraping e-commerce products with AI extraction...")
        print(f"URL: https://example-ecommerce.com")
        print(f"Steps: {steps}")

        result = client.agenticscraper(
            url="https://example-ecommerce.com",
            steps=steps,
            use_session=True,
            user_prompt="Extract all visible product information including names, prices, ratings, availability status, descriptions, and image URLs. Also extract search metadata like total results and current page.",
            output_schema=output_schema,
            ai_extraction=True
        )

        print("✅ E-commerce scraping completed!")
        print(f"Request ID: {result.get('request_id')}")

        if result and result.get("result"):
            products = result["result"].get("products", [])
            search_info = result["result"].get("search_info", {})
            
            print(f"🔍 Search Results for '{search_info.get('search_term', 'laptop')}':")
            print(f"📊 Total Results: {search_info.get('total_results', 'Unknown')}")
            print(f"📄 Current Page: {search_info.get('page', 'Unknown')}")
            print(f"🛍️ Products Found: {len(products)}")
            
            print("\n📦 Product Details:")
            for i, product in enumerate(products[:5], 1):  # Show first 5 products
                print(f"\n{i}. {product.get('name', 'N/A')}")
                print(f"   💰 Price: {product.get('price', 'N/A')}")
                print(f"   ⭐ Rating: {product.get('rating', 'N/A')}")
                print(f"   📦 Availability: {product.get('availability', 'N/A')}")
                if product.get('description'):
                    desc = product['description'][:100] + "..." if len(product['description']) > 100 else product['description']
                    print(f"   📝 Description: {desc}")
            
            # Save extracted data
            with open("ecommerce_products.json", "w", encoding="utf-8") as f:
                json.dump(result["result"], f, indent=2)
            print("\n💾 Product data saved to 'ecommerce_products.json'")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    finally:
        client.close()


def example_form_filling_and_data_extraction():
    """Example: Fill out a contact form and extract confirmation details."""

    # Initialize the client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        return None

    client = Client(api_key=api_key)

    steps = [
        "find and click on contact form",
        "type 'John Doe' in name field",
        "type 'john.doe@example.com' in email field",
        "type 'Product Inquiry' in subject field",
        "type 'I am interested in your premium plan. Could you provide more details about pricing and features?' in message field",
        "click submit button",
        "wait for confirmation message to appear",
    ]

    output_schema = {
        "form_submission": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "confirmation_message": {"type": "string"},
                "reference_number": {"type": "string"},
                "estimated_response_time": {"type": "string"},
                "submitted_data": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "subject": {"type": "string"}
                    }
                }
            },
            "required": ["status", "confirmation_message"]
        }
    }

    try:
        print("📝 Filling contact form and extracting confirmation...")
        print(f"URL: https://example-company.com/contact")
        print(f"Steps: {steps}")

        result = client.agenticscraper(
            url="https://example-company.com/contact",
            steps=steps,
            use_session=True,
            user_prompt="Extract the form submission status, confirmation message, any reference numbers, estimated response time, and echo back the submitted form data",
            output_schema=output_schema,
            ai_extraction=True
        )

        print("✅ Form submission and extraction completed!")
        print(f"Request ID: {result.get('request_id')}")

        if result and result.get("result"):
            form_data = result["result"].get("form_submission", {})
            
            print(f"📋 Form Submission Results:")
            print(f"   ✅ Status: {form_data.get('status', 'Unknown')}")
            print(f"   💬 Message: {form_data.get('confirmation_message', 'No message')}")
            
            if form_data.get('reference_number'):
                print(f"   🔢 Reference: {form_data['reference_number']}")
            
            if form_data.get('estimated_response_time'):
                print(f"   ⏰ Response Time: {form_data['estimated_response_time']}")
            
            submitted_data = form_data.get('submitted_data', {})
            if submitted_data:
                print(f"\n📤 Submitted Data:")
                for key, value in submitted_data.items():
                    print(f"   {key.title()}: {value}")
            
            # Save form results
            with open("form_submission_results.json", "w", encoding="utf-8") as f:
                json.dump(result["result"], f, indent=2)
            print("\n💾 Form results saved to 'form_submission_results.json'")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    finally:
        client.close()


if __name__ == "__main__":
    print("🔧 Comprehensive Agentic Scraper Examples")
    print("=" * 60)

    # Check if API key is set
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("⚠️ Please set your SGAI_API_KEY environment variable before running!")
        print("You can either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        exit(1)

    print("\n1. Basic Scraping (No AI Extraction)")
    print("-" * 40)
    example_basic_scraping_no_ai()

    print("\n\n2. AI Extraction Example - Dashboard Data")
    print("-" * 40)
    example_ai_extraction()

    print("\n\n3. E-commerce Product Scraping with AI")
    print("-" * 40)
    # Uncomment to run e-commerce example
    # example_ecommerce_product_scraping()

    print("\n\n4. Form Filling and Confirmation Extraction")
    print("-" * 40)
    # Uncomment to run form filling example
    # example_form_filling_and_data_extraction()

    print("\n✨ Examples completed!")
    print("\nℹ️ Note: Some examples are commented out by default.")
    print("   Uncomment them in the main section to run additional examples.")
