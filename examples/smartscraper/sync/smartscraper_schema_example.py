import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraph_py import Client

# Load environment variables from .env file
load_dotenv()


# Define a Pydantic model for the output schema
class WebpageSchema(BaseModel):
    title: str = Field(description="The title of the webpage")
    description: str = Field(description="The description of the webpage")
    summary: str = Field(description="A brief summary of the webpage")


# Initialize the client with API key from environment variable
api_key = os.getenv("SGAI_API_KEY")
if not api_key:
    print("❌ Error: SGAI_API_KEY environment variable not set")
    print("Please either:")
    print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
    print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
    exit(1)

sgai_client = Client(api_key=api_key)

# SmartScraper request with output schema
response = sgai_client.smartscraper(
    website_url="https://example.com",
    # website_html="...", # Optional, if you want to pass in HTML content instead of a URL
    user_prompt="Extract webpage information",
    output_schema=WebpageSchema,
)

# Print the response
print(f"Request ID: {response['request_id']}")
print(f"Result: {response['result']}")

sgai_client.close()
