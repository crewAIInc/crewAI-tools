from crewai_tools import AgentQLQueryDataTool

# Initialize the tool
query_tool = AgentQLQueryDataTool()

# Example with a simple query
# Note: Make sure you have set your AGENTQL_API_KEY in your environment variables
test_url = "https://scrapeme.live/?s=fish&post_type=product"
test_query = """
{
  products[] {
    product_name
    price
  }
}
"""

try:
    result = query_tool._run(url=test_url, query=test_query)
    print("Result:", result)
except Exception as e:
    print("An error occurred:", str(e))
