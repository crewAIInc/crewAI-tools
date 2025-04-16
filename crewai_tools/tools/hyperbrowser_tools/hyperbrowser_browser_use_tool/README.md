# HyperbrowserBrowserUseTool

## Description

[Hyperbrowser](https://hyperbrowser.ai) is a platform for running and scaling headless browsers. The Browser Use tool enables AI agents to interact with websites through a browser interface, performing human-like interactions and tasks.

Browser Use is an MIT-licensed Open Source AI Agent designed to interact with web pages as a human user would. `HyperbrowserBrowserUseTool` is a CrewAI tool that allows you to use Browser Use in your CrewAI workflows with a hosted API that handles everything from stealth mode to CAPTCHA solving, proxy rotation, and more.

Some things you can do with `HyperbrowserBrowserUseTool`:
- Web automation and task execution
- Data extraction from interactive websites  
- Interaction with web applications
- Testing and validation of web interfaces
- Browsing and summarizing web content

Key Features:
- Human-like Browser Interaction - Enables AI to navigate and interact with websites like a human user
- Vision Capabilities - Optionally use vision to analyze webpage screenshots for better context understanding
- Planning System - Advanced planning for complex multi-step tasks
- Configurable Parameters - Fine-tune behavior with adjustable parameters
- Session Integration - Use with Hyperbrowser sessions for enhanced capabilities

For more information about Hyperbrowser, please visit the [Hyperbrowser website](https://hyperbrowser.ai) or check out the [Hyperbrowser docs](https://docs.hyperbrowser.ai).

## Installation

- Head to [Hyperbrowser](https://app.hyperbrowser.ai/) to sign up and generate an API key for Free. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserBrowserUseTool` constructor.
- Install the required packages:

```
pip install hyperbrowser 'crewai[tools]'
```

## Example

Utilize the `HyperbrowserBrowserUseTool` as follows to allow your agent to interact with websites:

```python
from crewai_tools import HyperbrowserBrowserUseTool

tool = HyperbrowserBrowserUseTool()

# Basic usage
result = tool.run(
    task="Go to news.ycombinator.com and summarize the top 5 posts"
)

# Advanced usage with optional parameters
result = tool.run(
    task="Go to news.ycombinator.com and summarize the top 5 posts",
    use_vision=True,
    max_steps=20,
)
```

## Arguments

`__init__` arguments:
- `api_key`: Optional. Specifies Hyperbrowser API key. Defaults to the `HYPERBROWSER_API_KEY` environment variable.

`run` arguments:
- `task`: Required. The task to perform in natural language (e.g., "go to example.com and click the login button").
- `use_vision`: Optional. When enabled, allows the agent to analyze screenshots of the webpage for better context understanding.
- `use_vision_for_planner`: Optional. When enabled, provides screenshots to the planning component of the agent.
- `max_actions_per_step`: Optional. The maximum number of actions the agent can perform in a single step before reassessing.
- `max_input_tokens`: Optional. Maximum token limit for inputs sent to the language model.
- `planner_interval`: Optional. How often the planner runs (measured in agent steps) to reassess the overall strategy.
- `max_steps`: Optional. The maximum number of steps the agent can take before concluding the task.
- `session_options`: Optional. Configuration for the browser session, such as proxy settings or CAPTCHA solving capabilities.

For more detailed information about Browser Use parameters, visit [Hyperbrowser Browser Use Documentation](https://docs.hyperbrowser.ai/agents/browser-use).

## Session Configurations

You can provide configurations for the browser session via the `session_options` parameter. These include:

- `accept_cookies`: When enabled, automatically handles cookie consent popups.
- `solve_captchas`: When enabled, attempts to solve CAPTCHAs (requires paid plan).
- `use_proxy`: When enabled, uses rotating proxies for requests (requires paid plan).
- `use_stealth`: When enabled, activates stealth mode to avoid detection.

Note: CAPTCHA solving and proxy usage features require being on a paid Hyperbrowser plan.
