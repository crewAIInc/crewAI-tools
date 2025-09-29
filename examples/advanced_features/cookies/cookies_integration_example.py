"""
Comprehensive example demonstrating cookies integration for web scraping.

This example shows various real-world scenarios where cookies are essential:
1. E-commerce site scraping with authentication
2. Social media scraping with session cookies
3. Banking/financial site scraping with secure cookies
4. News site scraping with user preferences
5. API endpoint scraping with authentication tokens

Requirements:
- Python 3.7+
- scrapegraph-py
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraph_py import Client

# Load environment variables from .env file
load_dotenv()


# Define data models for different scenarios
class ProductInfo(BaseModel):
    """Model for e-commerce product information."""

    name: str = Field(description="Product name")
    price: str = Field(description="Product price")
    availability: str = Field(description="Product availability status")
    rating: Optional[str] = Field(description="Product rating", default=None)


class SocialMediaPost(BaseModel):
    """Model for social media post information."""

    author: str = Field(description="Post author")
    content: str = Field(description="Post content")
    likes: Optional[str] = Field(description="Number of likes", default=None)
    comments: Optional[str] = Field(description="Number of comments", default=None)
    timestamp: Optional[str] = Field(description="Post timestamp", default=None)


class NewsArticle(BaseModel):
    """Model for news article information."""

    title: str = Field(description="Article title")
    summary: str = Field(description="Article summary")
    author: Optional[str] = Field(description="Article author", default=None)
    publish_date: Optional[str] = Field(description="Publish date", default=None)


class BankTransaction(BaseModel):
    """Model for banking transaction information."""

    date: str = Field(description="Transaction date")
    description: str = Field(description="Transaction description")
    amount: str = Field(description="Transaction amount")
    type: str = Field(description="Transaction type (credit/debit)")


def scrape_ecommerce_with_auth():
    """Example: Scrape e-commerce site with authentication cookies."""
    print("=" * 60)
    print("E-COMMERCE SITE SCRAPING WITH AUTHENTICATION")
    print("=" * 60)

    # Example cookies for an e-commerce site
    cookies = {
        "session_id": "abc123def456",
        "user_id": "user789",
        "cart_id": "cart101112",
        "preferences": "dark_mode,usd",
        "auth_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    }

    website_url = "https://example-ecommerce.com/products"
    user_prompt = (
        "Extract product information including name, price, availability, and rating"
    )

    try:
        client = Client.from_env()
        response = client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt,
            cookies=cookies,
            output_schema=ProductInfo,
            number_of_scrolls=5,  # Scroll to load more products
        )

        print("✅ E-commerce scraping completed successfully")
        print(json.dumps(response, indent=2))
        client.close()

    except Exception as e:
        print(f"❌ Error in e-commerce scraping: {str(e)}")


def scrape_social_media_with_session():
    """Example: Scrape social media with session cookies."""
    print("\n" + "=" * 60)
    print("SOCIAL MEDIA SCRAPING WITH SESSION COOKIES")
    print("=" * 60)

    # Example cookies for a social media site
    cookies = {
        "session_token": "xyz789abc123",
        "user_session": "def456ghi789",
        "csrf_token": "jkl012mno345",
        "remember_me": "true",
        "language": "en_US",
    }

    website_url = "https://example-social.com/feed"
    user_prompt = (
        "Extract posts from the feed including author, content, likes, and comments"
    )

    try:
        client = Client.from_env()
        response = client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt,
            cookies=cookies,
            output_schema=SocialMediaPost,
            number_of_scrolls=10,  # Scroll to load more posts
        )

        print("✅ Social media scraping completed successfully")
        print(json.dumps(response, indent=2))
        client.close()

    except Exception as e:
        print(f"❌ Error in social media scraping: {str(e)}")


def scrape_news_with_preferences():
    """Example: Scrape news site with user preference cookies."""
    print("\n" + "=" * 60)
    print("NEWS SITE SCRAPING WITH USER PREFERENCES")
    print("=" * 60)

    # Example cookies for a news site
    cookies = {
        "user_preferences": "technology,science,ai",
        "reading_level": "advanced",
        "region": "US",
        "subscription_tier": "premium",
        "theme": "dark",
    }

    website_url = "https://example-news.com/technology"
    user_prompt = (
        "Extract news articles including title, summary, author, and publish date"
    )

    try:
        client = Client.from_env()
        response = client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt,
            cookies=cookies,
            output_schema=NewsArticle,
            total_pages=3,  # Scrape multiple pages
        )

        print("✅ News scraping completed successfully")
        print(json.dumps(response, indent=2))
        client.close()

    except Exception as e:
        print(f"❌ Error in news scraping: {str(e)}")


def scrape_banking_with_secure_cookies():
    """Example: Scrape banking site with secure authentication cookies."""
    print("\n" + "=" * 60)
    print("BANKING SITE SCRAPING WITH SECURE COOKIES")
    print("=" * 60)

    # Example secure cookies for a banking site
    cookies = {
        "secure_session": "pqr678stu901",
        "auth_token": "vwx234yz567",
        "mfa_verified": "true",
        "device_id": "device_abc123",
        "last_activity": "2024-01-15T10:30:00Z",
    }

    website_url = "https://example-bank.com/transactions"
    user_prompt = (
        "Extract recent transactions including date, description, amount, and type"
    )

    try:
        client = Client.from_env()
        response = client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt,
            cookies=cookies,
            output_schema=BankTransaction,
            total_pages=5,  # Scrape multiple pages of transactions
        )

        print("✅ Banking scraping completed successfully")
        print(json.dumps(response, indent=2))
        client.close()

    except Exception as e:
        print(f"❌ Error in banking scraping: {str(e)}")


def scrape_api_with_auth_tokens():
    """Example: Scrape API endpoint with authentication tokens."""
    print("\n" + "=" * 60)
    print("API ENDPOINT SCRAPING WITH AUTH TOKENS")
    print("=" * 60)

    # Example API authentication cookies
    cookies = {
        "api_token": "api_abc123def456",
        "client_id": "client_789",
        "access_token": "access_xyz789",
        "refresh_token": "refresh_abc123",
        "scope": "read:all",
    }

    website_url = "https://api.example.com/data"
    user_prompt = "Extract data from the API response"

    try:
        client = Client.from_env()
        response = client.smartscraper(
            website_url=website_url,
            user_prompt=user_prompt,
            cookies=cookies,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

        print("✅ API scraping completed successfully")
        print(json.dumps(response, indent=2))
        client.close()

    except Exception as e:
        print(f"❌ Error in API scraping: {str(e)}")


def main():
    """Run all cookies integration examples."""
    # Check if API key is available
    if not os.getenv("SGAI_API_KEY"):
        print("Error: SGAI_API_KEY not found in .env file")
        print("Please create a .env file with your API key:")
        print("SGAI_API_KEY=your_api_key_here")
        return

    print("🍪 COOKIES INTEGRATION EXAMPLES")
    print(
        "This demonstrates various real-world scenarios where cookies are essential for web scraping."
    )

    # Run all examples
    scrape_ecommerce_with_auth()
    scrape_social_media_with_session()
    scrape_news_with_preferences()
    scrape_banking_with_secure_cookies()
    scrape_api_with_auth_tokens()

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
