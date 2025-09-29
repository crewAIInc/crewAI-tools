"""
Example of using the searchscraper functionality to search for information.

This example demonstrates the configurable website limits feature:
- Default: 3 websites (30 credits)
- Enhanced: 5 websites (50 credits) - uncomment to try
- Maximum: 20 websites (200 credits) - for comprehensive research

Requirements:
- A .env file with your SGAI_API_KEY

Example .env file:
SGAI_API_KEY=your_api_key_here
"""

import os

from dotenv import load_dotenv

from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")

# Initialize the client with API key from environment
api_key = os.getenv("SGAI_API_KEY")
if not api_key:
    raise ValueError(
        "SGAI_API_KEY not found in environment variables. Please create a .env file with: SGAI_API_KEY=your_api_key_here"
    )

client = Client(api_key=api_key)

# Send a searchscraper request with configurable website limits
response = client.searchscraper(
    user_prompt="What is the latest version of Python and what are its main features?",
    num_results=3,  # Default: 3 websites (30 credits)
    # num_results=5  # Enhanced: 5 websites (50 credits) - uncomment for more comprehensive results
    # num_results=10  # Deep research: 10 websites (100 credits) - uncomment for extensive research
)

# Print the results
print("\nResults:")
print(f"Answer: {response['result']}")
print("\nReference URLs:")
for url in response["reference_urls"]:
    print(f"- {url}")

# Close the client
client.close()
