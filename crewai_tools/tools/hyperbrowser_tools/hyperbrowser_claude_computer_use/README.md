# HyperbrowserClaudeComputerUseTool

## Description

[Hyperbrowser](https://hyperbrowser.ai) is a platform for running and scaling headless browsers. The Claude Computer Use tool enables AI agents to interact with websites through Anthropic's Claude model, allowing it to execute complex browser tasks with sophisticated reasoning capabilities.

Claude Computer Use allows Claude to directly interact with a browser to perform tasks much like a human. `HyperbrowserClaudeComputerUseTool` is a CrewAI tool that allows you to use Claude Computer Use in your CrewAI workflows with a hosted API that handles browser automation, CAPTCHA solving, proxy rotation, and more.

Some things you can do with `HyperbrowserClaudeComputerUseTool`:
- Complex multi-step web interactions
- Nuanced data extraction requiring reasoning
- Advanced web application interaction
- Research tasks requiring contextual understanding
- Automation of sophisticated web workflows

Key Features:
- Sophisticated Reasoning - Claude's advanced reasoning capabilities for complex web tasks
- Human-like Interaction - Enables AI to navigate and interact with websites with human-like understanding
- Multi-step Processing - Handles complex sequences of actions that require reasoning across pages
- Configurable Parameters - Fine-tune behavior with adjustable task parameters
- Session Integration - Use with Hyperbrowser sessions for enhanced capabilities

For more information about Hyperbrowser, please visit the [Hyperbrowser website](https://hyperbrowser.ai) or check out the [Hyperbrowser docs](https://docs.hyperbrowser.ai).

## Installation

- Head to [Hyperbrowser](https://app.hyperbrowser.ai/) to sign up and generate an API key for Free. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserClaudeComputerUseTool` constructor.
- Install the required packages:

```
pip install hyperbrowser 'crewai[tools]'
```

## Example

Utilize the HyperbrowserClaudeComputerUseTool as follows to allow your agent to interact with websites:

```python
from crewai_tools import HyperbrowserClaudeComputerUseTool

tool = HyperbrowserClaudeComputerUseTool()

# Basic usage
result = tool.run(
    task="Go to news.ycombinator.com and summarize the top 5 posts"
)

# Advanced usage with optional parameters
result = tool.run(
    task="Go to news.ycombinator.com and summarize the top 5 posts",
    max_steps=20,
    session_options={
        "accept_cookies": True
    }
)
```

## Arguments

`__init__` arguments:
- `api_key`: Optional. Specifies Hyperbrowser API key. Defaults to the `HYPERBROWSER_API_KEY` environment variable.

`run` arguments:
- `task`: Required. The instruction or goal to be accomplished by Claude Computer Use (e.g., "analyze the pricing page of example.com and summarize the subscription tiers").
- `session_id`: Optional. An existing browser session ID to connect to instead of creating a new one.
- `max_failures`: Optional. The maximum number of consecutive failures allowed before the task is aborted.
- `max_steps`: Optional. The maximum number of interaction steps the agent can take to complete the task.
- `keep_browser_open`: Optional. When enabled, keeps the browser session open after task completion.
- `session_options`: Optional. Configuration for the browser session, such as proxy settings or CAPTCHA solving capabilities.

For more detailed information about Claude Computer Use parameters, visit [Hyperbrowser Claude Computer Use Documentation](https://docs.hyperbrowser.ai/agents/claude-computer-use).

## Session Configurations

You can provide configurations for the browser session via the `session_options` parameter. These include:

- `accept_cookies`: When enabled, automatically handles cookie consent popups.
- `solve_captchas`: When enabled, attempts to solve CAPTCHAs (requires paid plan).
- `use_proxy`: When enabled, uses rotating proxies for requests (requires paid plan).
- `use_stealth`: When enabled, activates stealth mode to avoid detection.

Note: CAPTCHA solving and proxy usage features require being on a paid Hyperbrowser plan.

Feel free to reference this page as well: https://docs.hyperbrowser.ai/agents/claude-computer-use 