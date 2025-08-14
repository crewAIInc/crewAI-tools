import asyncio

from browser_use.llm import ChatOpenAI as BrowserUseChatOpenAI

from crewai import Agent, Crew, CrewOutput, Task

from crewai_tools.tools.browser_use_tool import BrowserUseTool


def run_crew(browser_use_tool: BrowserUseTool) -> CrewOutput:
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
        description="Navigate to {webpage} and find the article about 'xAI (company)' and summarize it.",
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
            "webpage": "https://www.wikipedia.org/",
            # "webpage": "https://www.nytimes.com/",
        }
    )

async def simple_browser_interaction():
    browser_use_tool = BrowserUseTool(llm=BrowserUseChatOpenAI(model="gpt-4o"))
    crew_output = run_crew(browser_use_tool)
    print(crew_output.raw)

if __name__ == "__main__":
    asyncio.run(simple_browser_interaction())
