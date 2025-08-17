import asyncio

from browser_use import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI as BrowserUseChatOpenAI
from playwright.async_api import Browser as PlaywrightBrowser
from playwright.async_api import async_playwright

from crewai import Agent, Crew, CrewOutput, Task

from crewai_tools.tools.browser_use_tool import BrowserUseTool


def run_crew(browser_use_tool: BrowserUseTool, query: str = "Python programming language") -> CrewOutput:
    """
    Run a simple crew with the BrowserUseTool.
    This function is used to demonstrate how to use the BrowserUseTool in a crew.
    """
    agent = Agent(
        role="Browser Use Agent",
        goal="Use the browser",
        backstory=(
            "You are the best Browser Use Agent in the world. "
            "You have a browser that you can interact with using natural language instructions."
        ),
        tools=[browser_use_tool],
        # verbose=True,
        # llm="gemini/gemini-2.0-flash-exp",
        llm="gpt-4o",
    )

    task = Task(
        name="Navigate to webpage and summarize article",
        description="Navigate to https://www.wikipedia.org/ and find the article about {query} and summarize it.",
        expected_output="A summary of the article",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )

    return crew.kickoff(
        inputs={
            "query": query,
        }
    )

async def simple_browser_interaction():
    browser_use_tool = BrowserUseTool(llm=BrowserUseChatOpenAI(model="gpt-4o"))
    crew_output = run_crew(browser_use_tool)
    print(crew_output.raw)

def using_persistent_browser():
    import threading

    # Create a separate event loop for browser operations
    browser_loop = asyncio.new_event_loop()

    # Variables to store browser resources
    browser_session = None
    playwright = None
    setup_complete = threading.Event()

    async def setup_browser():
        nonlocal browser_session, playwright

        browser_profile=BrowserProfile(
            headless=False,
        )
        browser_args = browser_profile.get_args()
        playwright = await async_playwright().start()
        bu_playwright_browser: PlaywrightBrowser = await playwright.chromium.launch(
                headless=browser_profile.headless,
                args=browser_args,
            )

        browser_session = BrowserSession(
            browser_profile=browser_profile,
            browser=bu_playwright_browser,
        )

        return browser_session, playwright

    def run_browser_loop():
        nonlocal browser_session, playwright
        asyncio.set_event_loop(browser_loop)

        # Setup browser
        browser_session, playwright = browser_loop.run_until_complete(setup_browser())
        setup_complete.set()

        # Keep the loop running for async operations
        browser_loop.run_forever()

    # Start the browser loop in a separate thread
    browser_thread = threading.Thread(target=run_browser_loop, daemon=True)
    browser_thread.start()

    # Wait for browser setup to complete
    setup_complete.wait()

    # Create the browser tool with the separate event loop
    browser_use_tool = BrowserUseTool(
        llm=BrowserUseChatOpenAI(model="gpt-4o"),
        browser_loop=browser_loop,
        agent_kwargs = {
            "browser_session": browser_session,
            # "validate_output": False,
        }
    )

    # Run crews (this runs in the main thread)
    crew_result = run_crew(browser_use_tool)
    print(crew_result.raw)

    crew_result = run_crew(browser_use_tool, query="XAI (company)")
    print(crew_result.raw)

    # Cleanup
    async def cleanup():
        nonlocal browser_session, playwright
        await browser_session.stop()
        await playwright.stop()

    # Schedule cleanup in the browser loop
    asyncio.run_coroutine_threadsafe(cleanup(), browser_loop).result()

    # Stop the browser loop
    browser_loop.call_soon_threadsafe(browser_loop.stop)



if __name__ == "__main__":
    asyncio.run(simple_browser_interaction())

    # Now using_persistent_browser is synchronous and handles its own event loop
    using_persistent_browser()
