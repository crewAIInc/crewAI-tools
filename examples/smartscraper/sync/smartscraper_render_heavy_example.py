import os

from dotenv import load_dotenv

from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")

# Initialize the client with API key from environment variable
api_key = os.getenv("SGAI_API_KEY")
if not api_key:
    print("❌ Error: SGAI_API_KEY environment variable not set")
    print("Please either:")
    print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
    print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
    exit(1)

sgai_client = Client(api_key=api_key)

# SmartScraper request with render_heavy_js enabled
response = sgai_client.smartscraper(
    website_url="https://example.com",
    user_prompt="Find the CEO of company X and their contact details",
    render_heavy_js=True,  # Enable heavy JavaScript rendering
)

# Print the response
print(f"Request ID: {response['request_id']}")
print(f"Result: {response['result']}")

sgai_client.close()