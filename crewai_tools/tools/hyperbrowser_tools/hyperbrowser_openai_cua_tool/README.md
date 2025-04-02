# HyperbrowserOpenAICuaTool

## Description

[Hyperbrowser](https://hyperbrowser.ai) provides access to OpenAI's Computer-Using Agent (CUA), an advanced AI model designed to interact with web interfaces much like a human user. The CUA agent can navigate graphical user interfaces, perform tasks such as clicking buttons, typing text, and managing multi-step processes.

Key Features:
- Human-like Browser Interaction - CUA can navigate websites, click buttons, fill forms, and perform complex sequences of actions
- No API Integration Required - Automate workflows without relying on specialized APIs
- Multi-Step Task Execution - Complete tasks requiring sequential steps and decision making
- Session Management - Option to reuse browser sessions or create new ones for each task
- Configuration Options - Customize behavior with options for proxy usage, CAPTCHA solving, and more

For more information about Hyperbrowser, please visit the [Hyperbrowser website](https://hyperbrowser.ai) or check out the [Hyperbrowser docs](https://docs.hyperbrowser.ai).

## Installation

- Head to [Hyperbrowser](https://app.hyperbrowser.ai/) to sign up and generate an API key. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserOpenAICuaTool` constructor.
- Install the [Hyperbrowser SDK](https://github.com/hyperbrowserai/python-sdk):

```
pip install hyperbrowser 'crewai[tools]'
```

or with uv:

```
uv add hyperbrowser 'crewai[tools]'
```

## Example

Utilize the HyperbrowserOpenAICuaTool as follows to allow your agent to interact with websites:

```python
from crewai_tools import HyperbrowserOpenAICuaTool

tool = HyperbrowserOpenAICuaTool()

# Basic usage
result = tool.run(task="What are the top 5 posts on Hacker News?")

# Advanced usage with session options
from hyperbrowser.models import CreateSessionParams

result = tool.run(
    task="Find and extract the current Bitcoin price from CoinMarketCap",
    max_steps=20,
    keep_browser_open=False,
    session_options=CreateSessionParams(
        accept_cookies=True,
        use_proxy=True  # Requires paid plan
    )
)
```

## Arguments

`__init__` arguments:
- `api_key`: Optional. Specifies Hyperbrowser API key. Defaults to the `HYPERBROWSER_API_KEY` environment variable.

`run` arguments:
- `task`: Required. The instruction or goal to be accomplished by the CUA.
- `session_id`: Optional. An existing browser session ID to connect to instead of creating a new one.
- `max_failures`: Optional. The maximum number of consecutive failures allowed before the task is aborted.
- `max_steps`: Optional. The maximum number of interaction steps CUA can take to complete the task.
- `keep_browser_open`: Optional. When enabled, keeps the browser session open after task completion.
- `session_options`: Optional. Configuration options for the browser session, such as using proxies or solving CAPTCHAs (requires paid plan).

For detailed usage and configuration options, check out the [OpenAI CUA API Reference](https://docs.hyperbrowser.ai/reference/api-reference/agents/openai-cua). 