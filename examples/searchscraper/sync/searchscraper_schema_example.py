"""
Example of using the searchscraper functionality with a custom output schema.

This example demonstrates both schema-based output and configurable website limits:
- Default: 3 websites (30 credits)
- Enhanced: 5 websites (50 credits) - provides more comprehensive data for schema
- Maximum: 20 websites (200 credits) - for highly detailed schema population
"""

from typing import List

from pydantic import BaseModel

from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_logging(level="INFO")


# Define a custom schema for the output
class PythonVersionInfo(BaseModel):
    version: str
    release_date: str
    major_features: List[str]
    is_latest: bool


# Initialize the client
client = Client(api_key="your-api-key-here")

# Send a searchscraper request with schema and configurable website limits
num_results = 5  # Enhanced search for better schema data (50 credits)
print(f"🔍 Searching {num_results} websites with custom schema")
print(f"💳 Credits required: {30 if num_results <= 3 else 30 + (num_results - 3) * 10}")

response = client.searchscraper(
    user_prompt="What is the latest version of Python? Include the release date and main features.",
    num_results=num_results,  # More websites for better schema population
    output_schema=PythonVersionInfo,
)

# The result will be structured according to our schema
print(f"Request ID: {response['request_id']}")
print(f"Result: {response['result']}")

print("\nReference URLs:")
for url in response["reference_urls"]:
    print(f"- {url}")

# Close the client
client.close()
