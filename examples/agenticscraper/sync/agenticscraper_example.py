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

print("🤖 Example 1: Basic Agentic Scraping (No AI Extraction)")
print("=" * 60)

# AgenticScraper request - basic automated login example (no AI)
response = sgai_client.agenticscraper(
    url="https://dashboard.scrapegraphai.com/",
    use_session=True,
    steps=[
        "Type email@gmail.com in email input box",
        "Type test-password@123 in password inputbox", 
        "click on login"
    ],
    ai_extraction=False  # No AI extraction - just get raw content
)

# Print the response
print(f"Request ID: {response['request_id']}")
print(f"Result: {response.get('result', 'No result yet')}")
print(f"Status: {response.get('status', 'Unknown')}")

print("\n\n🧠 Example 2: Agentic Scraping with AI Extraction")
print("=" * 60)

# Define schema for AI extraction
output_schema = {
    "dashboard_info": {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "email": {"type": "string"},
            "dashboard_sections": {
                "type": "array",
                "items": {"type": "string"}
            },
            "credits_remaining": {"type": "number"}
        },
        "required": ["username", "dashboard_sections"]
    }
}

# AgenticScraper request with AI extraction
ai_response = sgai_client.agenticscraper(
    url="https://dashboard.scrapegraphai.com/",
    use_session=True,
    steps=[
        "Type email@gmail.com in email input box",
        "Type test-password@123 in password inputbox", 
        "click on login",
        "wait for dashboard to load completely"
    ],
    user_prompt="Extract user information, available dashboard sections, and remaining credits from the dashboard",
    output_schema=output_schema,
    ai_extraction=True
)

# Print the AI extraction response
print(f"AI Request ID: {ai_response['request_id']}")
print(f"AI Result: {ai_response.get('result', 'No result yet')}")
print(f"AI Status: {ai_response.get('status', 'Unknown')}")
print(f"User Prompt: Extract user information, available dashboard sections, and remaining credits")
print(f"Schema Provided: {'Yes' if output_schema else 'No'}")

sgai_client.close()
