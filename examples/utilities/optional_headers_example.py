from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_logging(level="INFO")

# Initialize the client with explicit API key
sgai_client = Client(api_key="your-api-key-here")

# SmartScraper request
response = sgai_client.smartscraper(
    website_url="https://example.com",
    user_prompt="Extract the main heading, description, and summary of the webpage",
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
)


# Print the response
print(f"Request ID: {response['request_id']}")
print(f"Result: {response['result']}")

sgai_client.close()
