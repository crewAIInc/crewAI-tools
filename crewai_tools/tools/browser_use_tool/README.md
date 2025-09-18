# Browser-Use Tool

## Description

The Browser-Use Tool enables agents to interact with web browsers using natural language commands.
This tool wraps the [browser-use](https://github.com/browser-use/browser-use) library, providing seamless browser automation capabilities within CrewAI agents.

## Key Features

- **Natural Language Control**: Interact with browsers using plain English instructions
- **Comprehensive Actions**: Support for navigation, clicking, typing, scrolling, tab management, and more
- **Persistent Browser Sessions**: Maintain browser state across multiple interactions
- **Multimodal Support**: Works with vision-capable LLMs like GPT-4o as well as text-only models
- **Async Operation**: Efficient asynchronous browser operations with customizable event loops

## Requirements

- Python 3.11+
- browser-use>=0.5.6
- Playwright (for browser automation)

## Installation

Install the crewai_tools package:

```bash
pip install 'crewai[tools]'
```

Install Playwright and required browsers:

```bash
playwright install
```

## Usage

### Basic Usage

```python
from crewai_tools import BrowserUseTool
from browser_use.llm import ChatOpenAI as BrowserUseChatOpenAI
from crewai import Agent

# Create the browser tool
browser_use_tool = BrowserUseTool(
    llm=BrowserUseChatOpenAI(model="gpt-4o")
)

# Use in an agent
agent = Agent(
    role="Web Researcher",
    goal="Navigate and extract information from websites",
    tools=[browser_use_tool],
    llm="gpt-4o"  # Agent's LLM can be different from browser's LLM
)
```

### Persistent Browser Session

For maintaining browser state across multiple interactions:

```python
import asyncio
import threading
from browser_use import BrowserProfile, BrowserSession
from playwright.async_api import async_playwright
from concurrent.futures import Future

def using_persistent_browser():
    # Create a separate event loop for browser operations
    browser_loop = asyncio.new_event_loop()
    browser_future = Future()

    async def setup_and_run():
        """Setup browser and return resources."""
        browser_profile = BrowserProfile(headless=False)
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=browser_profile.headless,
            args=browser_profile.get_args(),
        )
        browser_session = BrowserSession(
            browser_profile=browser_profile,
            browser=browser,
        )
        return browser_session, playwright

    def browser_loop_thread():
        """Run the browser event loop in a separate thread."""
        asyncio.set_event_loop(browser_loop)

        # Setup browser and store result
        browser_session, playwright = browser_loop.run_until_complete(setup_and_run())
        browser_future.set_result((browser_session, playwright))

        # Keep the loop running for async operations
        browser_loop.run_forever()

    # Start browser thread
    threading.Thread(target=browser_loop_thread, daemon=True).start()

    # Wait for browser setup
    browser_session, playwright = browser_future.result()

    # Create the browser tool with persistent session
    browser_tool = BrowserUseTool(
        llm=BrowserUseChatOpenAI(model="gpt-4o"),
        browser_loop=browser_loop,
        agent_kwargs={"browser_session": browser_session}
    )

    # Use the tool with your agents...
    # ...

    # Cleanup when done
    async def cleanup():
        await browser_session.stop()
        await playwright.stop()

    asyncio.run_coroutine_threadsafe(cleanup(), browser_loop).result()
    browser_loop.call_soon_threadsafe(browser_loop.stop)
```

### Complete Working Example

```python
import asyncio
from browser_use import BrowserProfile, BrowserSession
from browser_use.llm import ChatOpenAI as BrowserUseChatOpenAI
from playwright.async_api import async_playwright
from crewai import Agent, Crew, Task
from crewai_tools import BrowserUseTool

async def simple_browser_interaction():
    """Simple browser interaction example."""
    browser_tool = BrowserUseTool(
        llm=BrowserUseChatOpenAI(model="gpt-4o")
    )

    agent = Agent(
        role="Browser Agent",
        goal="Navigate and extract information",
        backstory="Expert at web navigation and data extraction",
        tools=[browser_tool],
        llm="gpt-4o"
    )

    task = Task(
        description="Navigate to Wikipedia and find information about Python programming language",
        expected_output="A summary of the Python article",
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )

    result = crew.kickoff()
    print(result.raw)

# Run the example
if __name__ == "__main__":
    asyncio.run(simple_browser_interaction())
```

## Tool Schema

The BrowserUseTool accepts the following parameters:

- **instruction** (required): Natural language instruction for the browser action
- **max_steps** (optional, default=100): Maximum number of steps the browser can take

## Supported Actions

The tool supports a wide range of browser actions:

### Basic Navigation

- Navigate to URLs
- Go back/forward in history
- Refresh pages

### Element Interaction

- Click on elements (buttons, links, etc.)
- Type text into input fields
- Select from dropdowns
- Submit forms

### Tab Management

- Open new tabs
- Switch between tabs
- Close tabs

### Content Actions

- Scroll (up, down, to element)
- Take screenshots
- Extract text content
- Wait for elements

### Advanced Features

- Handle popups and alerts
- Execute JavaScript
- Interact with Google Sheets
- Download files

## Important Notes

1. **LLM Requirements**: The browser-use library requires multimodal LLMs (e.g., GPT-4o, GPT-4o-mini)
2. **Separate LLMs**: The browser tool's LLM is independent from the agent's LLM
3. **Async Operations**: Browser operations run asynchronously for better performance
4. **Event Loop Management**: The tool manages its own event loop by default, or you can provide your own
5. **Resource Cleanup**: Always clean up browser resources when using persistent sessions

## Testing

The tool includes comprehensive tests covering:

- Schema validation
- Browser task execution
- Error handling
- History parsing
- Multiple action support

Run tests with:

```bash
pytest tests/tools/browser_use_tool_test.py
```

## Troubleshooting

- **Browser not closing**: Ensure proper cleanup in persistent browser sessions
- **Timeout errors**: Increase `max_steps` parameter for complex tasks
- **Element not found**: The browser might need more specific instructions or wait conditions
- **LLM errors**: Verify you're using a multimodal model (GPT-4o recommended)

## Links

- [Browser Use Documentation](https://github.com/browser-use/browser-use)
- [CrewAI Documentation](https://docs.crewai.com)
- [Example Implementation](example.py)
- [Test Suite](../../../tests/tools/browser_use_tool_test.py)