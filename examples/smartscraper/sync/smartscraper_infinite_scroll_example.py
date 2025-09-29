import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")


# Define the output schema
class Company(BaseModel):
    name: str
    category: str
    location: str


class CompaniesResponse(BaseModel):
    companies: List[Company]


# Initialize the client with API key from environment variable
# Make sure to set SGAI_API_KEY in your environment or .env file
api_key = os.getenv("SGAI_API_KEY")
if not api_key:
    print("❌ Error: SGAI_API_KEY environment variable not set")
    print("Please either:")
    print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
    print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
    exit(1)

sgai_client = Client(api_key=api_key)

try:
    # SmartScraper request with infinite scroll
    response = sgai_client.smartscraper(
        website_url="https://www.ycombinator.com/companies?batch=Spring%202025",
        user_prompt="Extract all company names and their categories from the page",
        output_schema=CompaniesResponse,
        number_of_scrolls=10,  # Scroll 10 times to load more companies
    )

    # Print the response
    print(f"Request ID: {response['request_id']}")

    # Parse and print the results in a structured way
    result = CompaniesResponse.model_validate(response["result"])
    print("\nExtracted Companies:")
    print("-" * 80)
    for company in result.companies:
        print(f"Name: {company.name}")
        print(f"Category: {company.category}")
        print(f"Location: {company.location}")
        print("-" * 80)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    sgai_client.close()
