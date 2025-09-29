#!/usr/bin/env python3
"""
Step-by-Step Pagination Example

This example demonstrates the pagination process step by step, showing each stage
of setting up and executing a paginated SmartScraper request.
"""

import json
import os
import time
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraph_py import Client
from scrapegraph_py.exceptions import APIError

# Load environment variables from .env file
load_dotenv()


class ProductInfo(BaseModel):
    """Schema for product information"""

    name: str = Field(description="Product name")
    price: Optional[str] = Field(description="Product price")
    rating: Optional[str] = Field(description="Product rating")
    image_url: Optional[str] = Field(description="Product image URL")
    description: Optional[str] = Field(description="Product description")


class ProductList(BaseModel):
    """Schema for list of products"""

    products: List[ProductInfo] = Field(description="List of products")


def step_1_environment_setup():
    """Step 1: Set up environment and API key"""
    print("STEP 1: Environment Setup")
    print("=" * 40)

    # Check if API key is available
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return None

    print("✅ API key found in environment")
    print(f"🔑 API Key: {api_key[:8]}...{api_key[-4:]}")
    return api_key


def step_2_client_initialization(api_key):
    """Step 2: Initialize the ScrapeGraph client"""
    print("\nSTEP 2: Client Initialization")
    print("=" * 40)

    try:
        client = Client(api_key=api_key)
        print("✅ Client initialized successfully")
        print(f"🔧 Client type: {type(client)}")
        return client
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return None


def step_3_define_schema():
    """Step 3: Define the output schema for structured data"""
    print("\nSTEP 3: Define Output Schema")
    print("=" * 40)

    print("📋 Defining Pydantic models for structured output:")
    print("   - ProductInfo: Individual product data")
    print("   - ProductList: Collection of products")

    # Show the schema structure
    schema_example = ProductList.model_json_schema()
    print(f"✅ Schema defined with {len(schema_example['properties'])} properties")

    return ProductList


def step_4_configure_request():
    """Step 4: Configure the pagination request parameters"""
    print("\nSTEP 4: Configure Request Parameters")
    print("=" * 40)

    # Configuration parameters
    website_url = "https://www.amazon.in/s?k=tv&crid=1TEF1ZFVLU8R8&sprefix=t%2Caps%2C390&ref=nb_sb_noss_2"
    user_prompt = "Extract all product info including name, price, rating, image_url, and description"
    total_pages = 3

    print("🌐 Website URL:")
    print(f"   {website_url}")
    print("\n📝 User Prompt:")
    print(f"   {user_prompt}")
    print(f"\n📄 Total Pages: {total_pages}")
    print(f"📊 Expected Products: ~{total_pages * 20} (estimated)")

    return {
        "website_url": website_url,
        "user_prompt": user_prompt,
        "total_pages": total_pages,
    }


def step_5_execute_request(client, config, output_schema):
    """Step 5: Execute the pagination request"""
    print("\nSTEP 5: Execute Pagination Request")
    print("=" * 40)

    print("🚀 Starting pagination request...")
    print("⏱️  This may take several minutes for multiple pages...")

    try:
        # Start timing
        start_time = time.time()

        # Make the request with pagination
        result = client.smartscraper(
            user_prompt=config["user_prompt"],
            website_url=config["website_url"],
            output_schema=output_schema,
            total_pages=config["total_pages"],
        )

        # Calculate duration
        duration = time.time() - start_time

        print(f"✅ Request completed in {duration:.2f} seconds")
        print(f"📊 Response type: {type(result)}")

        return result, duration

    except APIError as e:
        print(f"❌ API Error: {e}")
        print("This could be due to:")
        print("  - Invalid API key")
        print("  - Rate limiting")
        print("  - Server issues")
        return None, 0

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("This could be due to:")
        print("  - Network connectivity issues")
        print("  - Invalid website URL")
        print("  - Pagination limitations")
        return None, 0


def step_6_process_results(result, duration):
    """Step 6: Process and display the results"""
    print("\nSTEP 6: Process Results")
    print("=" * 40)

    if result is None:
        print("❌ No results to process")
        return

    print("📋 Processing pagination results...")

    # Display results based on type
    if isinstance(result, dict):
        print("\n🔍 Response Structure:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Check for pagination success indicators
        if "data" in result:
            print("\n✨ Pagination successful! Data extracted from multiple pages")

    elif isinstance(result, list):
        print(f"\n✅ Pagination successful! Extracted {len(result)} items")

        # Show first few items
        print("\n📦 Sample Results:")
        for i, item in enumerate(result[:3]):  # Show first 3 items
            print(f"  {i+1}. {item}")

        if len(result) > 3:
            print(f"  ... and {len(result) - 3} more items")

    else:
        print(f"\n📋 Result: {result}")

    print(f"\n⏱️  Total processing time: {duration:.2f} seconds")


def step_7_cleanup(client):
    """Step 7: Clean up resources"""
    print("\nSTEP 7: Cleanup")
    print("=" * 40)

    try:
        client.close()
        print("✅ Client session closed successfully")
        print("🔒 Resources freed")
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {e}")


def main():
    """Main function to run the step-by-step pagination example"""

    print("ScrapeGraph SDK - Step-by-Step Pagination Example")
    print("=" * 60)
    print("This example shows the complete process of setting up and")
    print("executing a pagination request with SmartScraper API")
    print("=" * 60)

    # Step 1: Environment setup
    api_key = step_1_environment_setup()
    if not api_key:
        return

    # Step 2: Client initialization
    client = step_2_client_initialization(api_key)
    if not client:
        return

    # Step 3: Define schema
    output_schema = step_3_define_schema()

    # Step 4: Configure request
    config = step_4_configure_request()

    # Step 5: Execute request
    result, duration = step_5_execute_request(client, config, output_schema)

    # Step 6: Process results
    step_6_process_results(result, duration)

    # Step 7: Cleanup
    step_7_cleanup(client)

    print("\n" + "=" * 60)
    print("Step-by-step pagination example completed!")
    print("\nKey takeaways:")
    print("1. Always validate your API key first")
    print("2. Define clear output schemas for structured data")
    print("3. Configure pagination parameters carefully")
    print("4. Handle errors gracefully")
    print("5. Clean up resources after use")
    print("\nNext steps:")
    print("- Try different websites and prompts")
    print("- Experiment with different page counts")
    print("- Add error handling for production use")
    print("- Consider rate limiting for large requests")


if __name__ == "__main__":
    main()
