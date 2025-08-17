import asyncio
from typing import Any, Optional, Type

from browser_use import Agent as BrowserUseAgent
from browser_use.agent.views import AgentHistoryList as BrowserUseAgentHistoryList
from browser_use.llm import BaseChatModel as BrowserUseBaseChatModel

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, field_validator

class BrowserUseToolSchema(BaseModel):
    """Input schema for BrowserUseTool.

    Defines the parameters required for browser interaction tasks.
    """

    instruction: str = Field(
        ...,
        description=(
            "Instruction to interact with the browser in natural language. "
            "The instructions will be broken down into multiple steps."
        ),
    )
    max_steps: Optional[int] = Field(
        100, # Taken from browser_use/agent/service.py Agent.run method
        description=(
            "Optional parameter for maximum number of steps to run the browser for. "
            "Note that tool interactions are performed step-by-step, for example: "
            "'Search for 'CrewAI' on Google' will be broken down into multiple steps like 'Navigate to google.com', "
            "'Input 'CrewAI' into search bar',"
            "'Click on search button', etc. so choose the max_steps accordingly. "
            "The tool may not complete the task if the max_steps are reached, in that case you can increase the max_steps."
        ),
    )


class BrowserUseTool(BaseTool):
    """Tool for interacting with a browser using natural language commands.

    Provides comprehensive browser automation capabilities including navigation,
    element interaction, content extraction, and file operations.
    """

    name: str = "Browser Use Tool"
    description: str = (
        "Interact with the browser using natural language commands.\n"
        "Features:\n"
        "  - Basic navigation actions: Search in Google, Navigate to URL, Go back to previous page\n"
        "  - Element interaction actions: click on element, Click and input text into a input interactive element, Upload file to interactive element with file path, Press keyboard keys (e.g. Escape, Backspace, Insert, PageDown, Delete, Enter, or Shortcuts such as `Control+o`, `Control+Shift+T`), Get all options from a native dropdown or ARIA menu, Select dropdown option or ARIA menu item for interactive element index by the text of the option you want to select, Wait for x seconds (can be used to wait until the page is fully loaded)\n"
        "  - Tab management actions: Switch tab, Close an existing tab\n"
        "  - Content actions: Scroll the page by specified number of pages (set down=True to scroll down, down=False to scroll up, num_pages=number of pages to scroll like 0.5 for half page, 1.0 for one page, etc.), Scroll to a text in the current page\n"
        "  - Google Sheets actions: Get the contents of the entire sheet, Get the contents of a cell or range of cells, Update the content of a cell or range of cells, Select a specific cell or range of cells, Fallback method to type text into (only one) currently selected cell\n"
        "  - Other actions: Write or append content to file_name in file system (Allowed extensions are .md, .txt, .json, .csv, .pdf. For .pdf files), Read file_name from file system, Extract structured semantic data (e.g. product description, price, all information about XYZ) from the current webpage based on a textual query\n\n"
        "Tool interactions are performed step-by-step, for example: 'Search for 'CrewAI' on Google' will be broken down into multiple steps like 'Navigate to google.com', 'Input 'CrewAI' into search bar', 'Click on search button', etc.\n\n"
        "When the task is completed, it returns the full history of the browser iterations, including the steps performed, the evaluation of each step, and the final result.\n"
        "If the task is successfully completed, it returns the string '✅ Successfully completed browser interaction.' as the last line.\n"
        "If the task failed, it returns the string '❌ Failed to complete browser interaction' and provides the reason (either maximum steps reached, or other errors)."
    )

    llm: BrowserUseBaseChatModel = Field(
        ...,
        description="Language model to be used by the browser_use agent when interacting with the browser",
    )
    agent_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional keyword arguments to pass to the browser_use agent (see browser_use agent params for more details).",
    )
    browser_loop: Optional[asyncio.AbstractEventLoop] = Field(
        None,
        description="Optional event loop to use for the browser_use agent (e.g., for persistent browser between tool calls).",
    )

    args_schema: Type[BaseModel] = BrowserUseToolSchema

    @field_validator("llm")
    @classmethod
    def validate_llm(cls, llm: BrowserUseBaseChatModel) -> BrowserUseBaseChatModel:
        if not llm:
            raise ValueError("llm must be specified.")
        return llm

    @staticmethod
    def _get_emoji(evaluation_previous_goal: str) -> str:
        """Return an emoji based on the evaluation result.

        Args:
            evaluation_previous_goal: The evaluation string to check.

        Returns:
            An emoji representing the evaluation status.
        """
        if "Success" in evaluation_previous_goal:
            return "👍"
        if "Failed" in evaluation_previous_goal:
            return "⚠️"
        return "🤷"

    @staticmethod
    def _parse_history(
        instruction: str,
        agent_history_list: BrowserUseAgentHistoryList,
        max_steps: int,
    ) -> str:
        """Parse browser agent history into a formatted string.

        Args:
            instruction: The original instruction for the browser task.
            agent_history_list: The history list from the browser agent.
            max_steps: The maximum number of steps allowed.

        Returns:
            A formatted string representation of the browser interaction history.
        """
        if agent_history_list is None or not agent_history_list.history:
            return "Browser did not do anything."

        step_by_step_output = "Following are the steps performed by the browser:\n"

        for step, (state, extracted_content, model_output) in enumerate(
            zip(
                agent_history_list.model_thoughts(),
                agent_history_list.extracted_content(),
                agent_history_list.model_outputs(),
            ),
            start=1,
        ):
            actions = '\n'.join(
                f'\t\t⚒️ Action {i+1}: {action.model_dump_json(exclude_unset=True)}'
                for i, action in enumerate(model_output.action)
            )
            memory = f'\t🧠 Memory: {state.memory}' if state.memory else ''
            results = f'\t📄 Result: {extracted_content}' if extracted_content else ''

            step_by_step_output += (
                f"📍 Step {step}:\n"
                f"\t{BrowserUseTool._get_emoji(state.evaluation_previous_goal)} Evaluation: {state.evaluation_previous_goal}\n"
                f"{memory}\n"
                f"\t🎯 Next Goal: {state.next_goal}\n"
                f"\t🛠️ Actions: \n{actions}\n"
                f"{results}\n"
            )

        history_status = "✅ Successfully completed browser interaction."
        if not agent_history_list.is_done():
            history_status = f"\t❌ Failed to complete browser interaction in {max_steps} maximum steps.\n"

        elif agent_history_list.has_errors():
            history_status = f"\t❌ Failed to complete browser interaction due to errors: {agent_history_list.errors()}\n"

        return (
            f"🚀 Starting task: {instruction}\n"
            f"{step_by_step_output}\n"
            f"{history_status}"
        )

    async def _create_browser_task(
        self, browser_agent: BrowserUseAgent, max_steps: int
    ) -> BrowserUseAgentHistoryList:
        """Create a browser task based on the event loop configuration.

        Args:
            browser_agent: The browser agent to run.
            max_steps: Maximum number of steps to execute.

        Returns:
            The browser agent's history list after execution.
        """
        if self.browser_loop:
            future = asyncio.run_coroutine_threadsafe(
                coro=browser_agent.run(max_steps=max_steps),
                loop=self.browser_loop,
            )
            return await asyncio.wrap_future(future)
        return await browser_agent.run(max_steps=max_steps)

    async def _async_run(self, **kwargs: Any) -> str:
        """Execute the browser automation task.

        Args:
            **kwargs: Arguments for the browser task.

        Returns:
            A string describing the result of the browser interaction.
        """
        args = BrowserUseToolSchema(**kwargs)
        if not args.instruction:
            return "No instruction provided."

        browser_agent = BrowserUseAgent(
            task=args.instruction,
            llm=self.llm,
            **self.agent_kwargs,
        )

        try:
            agent_history_list = await self._create_browser_task(browser_agent, args.max_steps)

            return BrowserUseTool._parse_history(
                instruction=args.instruction,
                agent_history_list=agent_history_list,
                max_steps=args.max_steps,
            )

        except asyncio.CancelledError:
            browser_agent.stop()
            return (
                "Browser agent was interrupted.\n"
                "You MUST stop now and return a result!"
            )
        except Exception as e:
            browser_agent.stop()
            return (
                f"Error during execution: {e}\n\n"
                "Browser agent was interrupted. You MUST stop now and return a result!"
            )

    def _run(self, **kwargs: Any) -> str:
        """Run the browser tool synchronously.

        Args:
            **kwargs: Arguments for the browser task.

        Returns:
            A string describing the result of the browser interaction.
        """
        # If we have a specific browser_loop, always use it
        if self.browser_loop:
            return asyncio.run_coroutine_threadsafe(
                self._async_run(**kwargs),
                loop=self.browser_loop,
            ).result()

        # Otherwise, handle different event loop scenarios
        try:
            # Check if there's an event loop running
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # We're in an existing event loop context, run in thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self._async_run(**kwargs)
                    )
                    return future.result()
            else:
                # We have a loop but it's not running
                return loop.run_until_complete(self._async_run(**kwargs))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._async_run(**kwargs))


__all__ = [
    "BrowserUseTool",
    "BrowserUseToolSchema",
]
