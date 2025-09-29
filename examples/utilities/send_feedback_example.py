from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger

sgai_logger.set_logging(level="INFO")

# Initialize the client
sgai_client = Client(api_key="your-api-key-here")

# Example request_id (replace with an actual request_id from a previous request)
request_id = "your-request-id-here"

# Check remaining credits
credits = sgai_client.get_credits()
print(f"Credits Info: {credits}")

# Submit feedback for a previous request
feedback_response = sgai_client.submit_feedback(
    request_id=request_id,
    rating=5,  # Rating from 1-5
    feedback_text="The extraction was accurate and exactly what I needed!",
)
print(f"\nFeedback Response: {feedback_response}")

# Get previous results using get_smartscraper
previous_result = sgai_client.get_smartscraper(request_id=request_id)
print(f"\nRetrieved Previous Result: {previous_result}")

sgai_client.close()
