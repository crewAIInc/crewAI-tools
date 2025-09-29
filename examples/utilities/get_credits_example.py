from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_level("DEBUG")

# Initialize the client
sgai_client = Client(api_key="your-api-key-here")

# Check remaining credits
credits = sgai_client.get_credits()
print(f"Credits Info: {credits}")

sgai_client.close()
