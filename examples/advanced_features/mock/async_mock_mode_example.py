import asyncio

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger


sgai_logger.set_logging(level="INFO")


async def basic_mock_usage():
    # Initialize the client with mock mode enabled
    async with AsyncClient.from_env(mock=True) as client:
        print("\n-- get_credits (mock) --")
        print(await client.get_credits())

        print("\n-- markdownify (mock) --")
        md = await client.markdownify(website_url="https://example.com")
        print(md)

        print("\n-- get_markdownify (mock) --")
        md_status = await client.get_markdownify("00000000-0000-0000-0000-000000000123")
        print(md_status)

        print("\n-- smartscraper (mock) --")
        ss = await client.smartscraper(user_prompt="Extract title", website_url="https://example.com")
        print(ss)


async def mock_with_path_overrides():
    # Initialize the client with mock mode and custom responses
    async with AsyncClient.from_env(
        mock=True,
        mock_responses={
            "/v1/credits": {"remaining_credits": 42, "total_credits_used": 58}
        },
    ) as client:
        print("\n-- get_credits with override (mock) --")
        print(await client.get_credits())


async def mock_with_custom_handler():
    def handler(method, url, kwargs):
        return {"handled_by": "custom_handler", "method": method, "url": url}

    # Initialize the client with mock mode and custom handler
    async with AsyncClient.from_env(mock=True, mock_handler=handler) as client:
        print("\n-- searchscraper via custom handler (mock) --")
        resp = await client.searchscraper(user_prompt="Search something")
        print(resp)


async def main():
    await basic_mock_usage()
    await mock_with_path_overrides()
    await mock_with_custom_handler()


if __name__ == "__main__":
    asyncio.run(main())


