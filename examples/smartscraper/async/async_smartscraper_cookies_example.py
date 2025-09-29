"""
Example demonstrating how to use the SmartScraper API with cookies (Async).

This example shows how to:
1. Set up the API request with cookies for authentication
2. Use cookies with infinite scrolling
3. Define a Pydantic model for structured output
4. Make the API call and handle the response
5. Process the extracted data

Requirements:
- Python 3.7+
- scrapegraph-py
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import asyncio
import json
import os
from typing import Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraph_py import AsyncClient

# Load environment variables from .env file
load_dotenv()


# Define the data models for structured output
class CookieInfo(BaseModel):
    """Model representing cookie information."""

    cookies: Dict[str, str] = Field(description="Dictionary of cookie key-value pairs")


async def main():
    """Example usage of the cookies scraper."""
    # Check if API key is available
    if not os.getenv("SGAI_API_KEY"):
        print("Error: SGAI_API_KEY not found in .env file")
        print("Please create a .env file with your API key:")
        print("SGAI_API_KEY=your_api_key_here")
        return

    # Initialize the async client
    async with AsyncClient.from_env() as client:
        # Example 1: Basic cookies example (httpbin.org/cookies)
        print("=" * 60)
        print("EXAMPLE 1: Basic Cookies Example")
        print("=" * 60)

        website_url = "https://httpbin.org/cookies"
        user_prompt = "Extract all cookies info"
        cookies = {"cookies_key": "cookies_value"}

        try:
            # Perform the scraping with cookies
            response = await client.smartscraper(
                website_url=website_url,
                user_prompt=user_prompt,
                cookies=cookies,
                output_schema=CookieInfo,
            )

            # Print the results
            print("\nExtracted Cookie Information:")
            print(json.dumps(response, indent=2))

        except Exception as e:
            print(f"Error occurred: {str(e)}")

        # Example 2: Cookies with infinite scrolling
        print("\n" + "=" * 60)
        print("EXAMPLE 2: Cookies with Infinite Scrolling")
        print("=" * 60)

        website_url = "https://httpbin.org/cookies"
        user_prompt = "Extract all cookies and scroll information"
        cookies = {"session_id": "abc123", "user_token": "xyz789"}

        try:
            # Perform the scraping with cookies and infinite scrolling
            response = await client.smartscraper(
                website_url=website_url,
                user_prompt=user_prompt,
                cookies=cookies,
                number_of_scrolls=3,
                output_schema=CookieInfo,
            )

            # Print the results
            print("\nExtracted Cookie Information with Scrolling:")
            print(json.dumps(response, indent=2))

        except Exception as e:
            print(f"Error occurred: {str(e)}")

        # Example 3: Cookies with pagination
        print("\n" + "=" * 60)
        print("EXAMPLE 3: Cookies with Pagination")
        print("=" * 60)

        website_url = "https://httpbin.org/cookies"
        user_prompt = "Extract all cookies from multiple pages"
        cookies = {"auth_token": "secret123", "preferences": "dark_mode"}

        try:
            # Perform the scraping with cookies and pagination
            response = await client.smartscraper(
                website_url=website_url,
                user_prompt=user_prompt,
                cookies=cookies,
                total_pages=3,
                output_schema=CookieInfo,
            )

            # Print the results
            print("\nExtracted Cookie Information with Pagination:")
            print(json.dumps(response, indent=2))

        except Exception as e:
            print(f"Error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
