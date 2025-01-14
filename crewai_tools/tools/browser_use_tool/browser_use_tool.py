import asyncio
from typing import Optional, Type

from browser_use import Agent as BrowserUseAgent
from browser_use import Controller
from browser_use.agent.views import AgentHistoryList
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContext
from crewai.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field, field_validator


class BaseBrowserUseToolSchema(BaseModel):
    """Input for BrowserUseTool."""

    instruction: str = Field(
        ...,
        description=(
            "Instruction to interact with the browser in natural language. "
            "The instructions would be broken down into multiple steps and the browser will perform each step one by one."
        ),
    )
    max_steps: Optional[int] = Field(
        100, # Taken from browser_use/agent/service.py Agent.run method
        description=(
            "Optional parameter for maximum number of steps to run the browser for. "
            "Note that tool interactions are performed step-by-step, for example: 'Search for 'CrewAI' on Google' will be broken down into multiple steps like 'Navigate to google.com', 'Input 'CrewAI' into search bar', 'Click on search button', etc. so choose the max_steps accordingly. "
            "The tool may not complete the task if the max_steps are reached, in that case you can increase the max_steps."
        ),
    )


class BaseBrowserUseTool(BaseTool):
    """Base class for browser use tools."""

    llm: BaseChatModel = Field(
        ...,
        description="Language model to by browser_use agent when interacting with the browser",
    )
    browser: Optional[Browser] = Field(
        None,
        description="Browser to use, if None this creates a new browser",
    )
    browser_context: Optional[BrowserContext] = Field(
        None,
        description="Browser context to use",
    )
    controller: Controller = Field(
        Controller(),
        description="The controller to use for the browser use tools.",
    )
    validate_output: bool = Field(
        False, # Taken from browser_use/agent/service.py Agent.__init__ method
        description="Whether to validate the output of the browser_use agent once it is done",
    )
    upper_limit_max_steps: int = Field(
        100,
        description="The upper limit for the maximum number of steps to run the browser for, adjust if model gives too high max_steps to force a maximum",
    )
    lower_limit_max_steps: int = Field(
        1,
        description="The lower limit for the maximum number of steps to run the browser for, adjust if model gives too low max_steps to force a minimum",
    )
    max_failures: int = Field(
        3, # Taken from browser_use/agent/service.py Agent.__init__ method
        description="The maximum number of failures allowed for the browser use agent",
    )
    event_loop: asyncio.AbstractEventLoop = Field(
        asyncio.new_event_loop(),
        description="The event loop to use to run browser-use. Creates a new event loop if not provided.",
    )
    event_loop_close_on_del: bool = Field(
        True,
        description="Whether to close the event loop on deletion of the tool. If using your own event loop, set this to False to avoid closing it.",
    )


    # Enable arbitrary types to allow non-Pydantic types
    class Config:
        arbitrary_types_allowed = True

    args_schema: Type[BaseModel] = BaseBrowserUseToolSchema


    @field_validator("llm")
    @classmethod
    def validate_llm(cls, llm: BaseChatModel) -> BaseChatModel:
        if not llm:
            raise ValueError("llm must be specified.")
        return llm

    @field_validator("upper_limit_max_steps", "lower_limit_max_steps", "max_failures")
    @classmethod
    def validate_int(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Value must be greater than 0.")
        return value

    def _get_emoji(self, valuation_previous_goal: str) -> str:
        if "Success" in valuation_previous_goal:
            return "👍"
        elif "Failed" in valuation_previous_goal:
            return "⚠️"
        return "🤷"

    # This method is based on browser_use:0.1.16 prints
    def _parse_history(self, agent_history_list: AgentHistoryList, max_steps: int) -> str:
        if not agent_history_list or not agent_history_list.history:
            return "Browser did nothing."

        step_by_step_output = "\n".join(
            [
                f"📍 Step {step}:\n"
                f"{self._get_emoji(state.valuation_previous_goal)} Evaluation: {state.valuation_previous_goal}\n"
                f"{f"🧠 Memory: {state.memory}.\n" if state.memory else ""}"
                f"🎯 Next Goal: {state.next_goal}.\n"
                f"🛠️ Action: {model_output.action.model_dump_json(exclude_unset=True)}\n"
                f"{f"📄 Result: {extracted_content}\n" if extracted_content else ""}"
                for step, (state, extracted_content, model_output) in enumerate(
                    zip(
                        agent_history_list.model_thoughts(),
                        agent_history_list.extracted_content(),
                        agent_history_list.model_outputs(),
                    ),
                    start=1,
                )
            ]
        )

        history_status = "✅ successfully completed browser interaction.\n"
        if not agent_history_list.is_done():
            history_status = f"❌ Failed to complete browser interaction in {max_steps} maximum steps.\n"

        elif agent_history_list.has_errors():
            history_status = f"❌ Failed to complete browser interaction due to errors: {agent_history_list.errors()}\n"

        return (
            "Browser finished the interaction, following is the step-by-step interactions:\n\n"
            f"{step_by_step_output}\n"
            f"{history_status}"
        )

    def _run(self, **kwargs) -> str:
        args = BaseBrowserUseToolSchema(**kwargs)
        args.max_steps = min(
            max(args.max_steps, self.lower_limit_max_steps),
            self.upper_limit_max_steps,
        )
        if not args.instruction:
            return "No instruction provided."

        print(
            f"Running BrowserUseTool with instruction: {args.instruction} and max_steps: {args.max_steps}"
        )
        agent_history_list: (
            AgentHistoryList
        ) = self.event_loop.run_until_complete(
            BrowserUseAgent(
                task=args.instruction,
                llm=self.llm,
                browser=self.browser,
                browser_context=self.browser_context,
                controller=self.controller,
                validate_output=self.validate_output,
                max_failures=self.max_failures,
            ).run(max_steps=args.max_steps)
        )
        return self._parse_history(
            agent_history_list,
            args.max_steps,
        )

    def __del__(self):
        super().__del__()
        if self.event_loop_close_on_del:
            self.event_loop.close()


class BrowserUseTool(BaseBrowserUseTool):
    """Tool for interacting with a browser using natural language commands."""

    name: str = "Browser Use Tool"
    description: str = (
        "Interact with the browser using natural language commands.\n"
        "Features:\n"
        "  - Basic navigation actions: Search Google, Navigate to URL, Go back to previous page,\n"
        "  - Element interaction actions: click element, Input text, \n"
        "  - Tab management actions: switch tab, Open new tab\n"
        "  - Content actions: Extract page content to get the text or markdown, complete task, Scroll down the page by pixel amount, Scroll up the page by pixel amount\n"
        """Tool interactions are performed step-by-step, for example: "Search for 'CrewAI' on Google" will be broken down into multiple steps like "Navigate to google.com", "Input 'CrewAI' into search bar", "Click on search button", etc.\n\n"""
        "The tool returns the step-by-step interactions, what the browser did at each step and the result of each step."
    )

__all__ = [
    "BrowserUseTool",
    "BaseBrowserUseTool",
    "BaseBrowserUseToolSchema",
]
