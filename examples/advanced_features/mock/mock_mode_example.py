from scrapegraph_py import Client
from scrapegraph_py.logger import sgai_logger


sgai_logger.set_logging(level="INFO")


def basic_mock_usage():
    # Initialize the client with mock mode enabled
    client = Client.from_env(mock=True)

    print("\n-- get_credits (mock) --")
    print(client.get_credits())

    print("\n-- markdownify (mock) --")
    md = client.markdownify(website_url="https://example.com")
    print(md)

    print("\n-- get_markdownify (mock) --")
    md_status = client.get_markdownify("00000000-0000-0000-0000-000000000123")
    print(md_status)

    print("\n-- smartscraper (mock) --")
    ss = client.smartscraper(user_prompt="Extract title", website_url="https://example.com")
    print(ss)


def mock_with_path_overrides():
    # Initialize the client with mock mode and custom responses
    client = Client.from_env(
        mock=True,
        mock_responses={
            "/v1/credits": {"remaining_credits": 42, "total_credits_used": 58}
        },
    )

    print("\n-- get_credits with override (mock) --")
    print(client.get_credits())


def mock_with_custom_handler():
    def handler(method, url, kwargs):
        return {"handled_by": "custom_handler", "method": method, "url": url}

    # Initialize the client with mock mode and custom handler
    client = Client.from_env(mock=True, mock_handler=handler)

    print("\n-- searchscraper via custom handler (mock) --")
    resp = client.searchscraper(user_prompt="Search something")
    print(resp)


if __name__ == "__main__":
    basic_mock_usage()
    mock_with_path_overrides()
    mock_with_custom_handler()


