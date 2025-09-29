from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_logging(level="INFO")

# Initialize the client
sgai_client = Client(api_key="your-api-key-here")

# Markdownify request
response = sgai_client.markdownify(
    website_url="https://example.com",
)

# Print the response
print(f"Request ID: {response['request_id']}")
print(f"Result: {response['result']}")
