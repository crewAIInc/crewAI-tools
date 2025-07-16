from typing import Any

async def aget_current_page(browser: Any) -> Any:
    """Get the current page from a browser, or create one if none exists (async).

    Args:
        browser: The Playwright browser instance

    Returns:
        The current (or newly created) page
    """
    # Get existing pages
    pages = await browser.pages()
    
    # Return existing page or create new one
    if pages:
        return pages[0]
    else:
        return await browser.new_page()


def get_current_page(browser: Any) -> Any:
    """Get the current page from a browser, or create one if none exists (sync).

    Args:
        browser: The Playwright browser instance

    Returns:
        The current (or newly created) page
    """
    # Get existing pages
    pages = browser.pages
    
    # Return existing page or create new one
    if pages:
        return pages[0]
    else:
        return browser.new_page()