import asyncio

from pydantic import BaseModel, Field

from scrapegraph_py import AsyncClient


# Define a Pydantic model for the output schema
class WebpageSchema(BaseModel):
    title: str = Field(description="The title of the webpage")
    description: str = Field(description="The description of the webpage")
    summary: str = Field(description="A brief summary of the webpage")


async def main():
    # Initialize the async client
    sgai_client = AsyncClient(api_key="your-api-key-here")

    # SmartScraper request with output schema
    response = await sgai_client.smartscraper(
        website_url="https://example.com",
        user_prompt="Extract webpage information",
        output_schema=WebpageSchema,
    )

    # Print the response
    print(f"Request ID: {response['request_id']}")
    print(f"Result: {response['result']}")

    await sgai_client.close()


if __name__ == "__main__":
    asyncio.run(main())
