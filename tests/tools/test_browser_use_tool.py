import asyncio

from browser_use import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from crewai import Agent, Crew, Task

from crewai_tools.tools.browser_use_tool import BrowserUseTool
from langchain_openai.chat_models import ChatOpenAI


def main():

    browser = Browser(config=BrowserConfig(headless=False))

    browser_context = BrowserContext(browser=browser)

    browser_use_tool = BrowserUseTool(
        llm=ChatOpenAI(model="gpt-4o"),
        browser=browser,
        browser_context=browser_context,
    )

    agent = Agent(
        role="Browser Use Agent",
        goal="Use the browser",
        backstory=(
            "You are the best Browser Use Agent in the world. "
            "You have a browser that you can interact with using natural language instructions."
        ),
        tools=[browser_use_tool],
        verbose=True,
        # llm="gemini/gemini-2.0-flash-exp",
        llm="gpt-4o",
    )

    task = Task(
        name="Navigate to webpage and summarize article",
        description="Navigate to {webpage} and find the article about 'xAI (company)' and summarize it.",
        expected_output="A summary of the article",
        agent=agent,
    )

    crew = Crew(
        tasks=[task],
        agents=[agent],
        verbose=True,
    )

    crew_result = crew.kickoff(
        inputs={
            "webpage": "https://www.wikipedia.org/",
            # "webpage": "https://www.nytimes.com/",
        }
    )

    print(crew_result.raw)

    with asyncio.new_event_loop() as loop:
        loop: asyncio.AbstractEventLoop
        loop.run_until_complete(browser.close())


if __name__ == "__main__":
    main()
