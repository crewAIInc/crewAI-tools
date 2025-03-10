# Browser-Use Tool

## Description

This tool is used to give the Agent the ability to use a browser to interact with the environment.
It is useful when the Agent needs to interact with it.

The tool uses [browser-use/browser-use](https://github.com/browser-use/browser-use).

## Requirements

- [browser-use@0.1.16](https://github.com/browser-use/browser-use/tree/0.1.16) (will be installed automatically). Later versions do not work.

## Installation

Install the crewai_tools package

```shell
pip install 'crewai[tools]'
```

## Examples

Notes:

- browser-use requires multimodal models like gpt-4o, gpt-4o-mini, etc.
- Browser-use uses its own llm, which is different than the Agent's llm.
The only supported llms are from langchain.
- browser-use runs asynchronously. It creates a new event loop and runs the browser in that loop and deletes the loop after the tool is deleted. If you want to use your own event loop, you can pass it to the tool.
- browser-use uses a Browser and a BrowserContext to run the browser. If you don't specify them, the tool will create its own Browser and BrowserContext each time the tool is called. If you want to use a consistent browser throughout the Agent's lifecycle, you should specify your own Browser and BrowserContext and manage them yourself outside the tool.

### Short Examples

```python
from crewai_tools import BrowserUseTool
from langchain_openai.chat_models import ChatOpenAI

browser_use_tool = BrowserUseTool(llm=ChatOpenAI(model="gpt-4o"))

Agent(
    ...
    tools=[browser_use_tool],
)
```

To use a consistent browser throughout the Agent's lifecycle, you can do this

```python
import asyncio

from crewai_tools import BrowserUseTool
from langchain_openai.chat_models import ChatOpenAI

browser = Browser(config=BrowserConfig(headless=False))

browser_context = BrowserContext(browser=browser)

browser_use_tool = BrowserUseTool(
    llm=ChatOpenAI(model="gpt-4o"),
    browser=browser,
    browser_context=browser_context,
)

Agent(
    ...
    tools=[browser_use_tool],
)

with asyncio.new_event_loop() as loop:
    loop: asyncio.AbstractEventLoop
    loop.run_until_complete(browser.close())
```

### Full Working Example

Found in [tests/tools/test_browser_use_tool.py](/tests/tools/test_browser_use_tool.py)

```python
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
        }
    )

    print(crew_result.raw)

    with asyncio.new_event_loop() as loop:
        loop: asyncio.AbstractEventLoop
        loop.run_until_complete(browser.close())


if __name__ == "__main__":
    main()
```
