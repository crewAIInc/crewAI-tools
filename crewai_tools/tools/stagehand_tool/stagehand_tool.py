import asyncio
import json
import logging
from typing import Any, Dict, Optional, Type, Union, List

from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig, StagehandPage
from stagehand.schemas import (
    AvailableModel,
    ActOptions, 
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult
)
from stagehand.utils import configure_logging

from ..base_tool import BaseTool

from dotenv import load_dotenv

load_dotenv()


class StagehandCommandType(str):
    ACT = "act"
    EXTRACT = "extract"
    OBSERVE = "observe"


class StagehandToolSchema(BaseModel):
    """Input for StagehandTool."""
    instruction: str = Field(
        ..., 
        description="The instruction for Stagehand to automate the web browser. Describe in natural language what you want to do on the website."
    )
    url: Optional[str] = Field(
        None,
        description="The URL to navigate to before executing the instruction. If not provided, Stagehand will use the current page."
    )
    command_type: Optional[str] = Field(
        "act",
        description="The type of command to execute: 'act' (perform an action), 'extract' (extract data), or 'observe' (identify elements). Default is 'act'."
    )
    selector: Optional[str] = Field(
        None,
        description="CSS selector to limit extraction or observation to a specific element. Only used with extract and observe commands."
    )


class StagehandTool(BaseTool):
    """
    A tool that uses Stagehand to automate web browser interactions using natural language.
    
    Stagehand allows AI agents to interact with websites through a browser, 
    performing actions like clicking buttons, filling forms, and extracting data.
    """
    
    name: str = "Web Automation Tool"
    description: str = "A tool that can automate web browser interactions using natural language. Use this to navigate websites, click buttons, fill forms, search, and extract information from web pages."
    args_schema: Type[BaseModel] = StagehandToolSchema
    
    # Stagehand configuration
    api_key: Optional[str] = None
    project_id: Optional[str] = None
    model_api_key: Optional[str] = None
    model_name: Optional[AvailableModel] = AvailableModel.CLAUDE_3_7_SONNET_LATEST
    server_url: Optional[str] = "http://api.stagehand.browserbase.com/v1"
    headless: bool = False
    dom_settle_timeout_ms: int = 3000
    self_heal: bool = True
    wait_for_captcha_solves: bool = True
    verbose: int = 1
    
    # Instance variables
    _stagehand: Optional[Stagehand] = None
    _page: Optional[StagehandPage] = None
    _session_id: Optional[str] = None
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        headless: Optional[bool] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        self_heal: Optional[bool] = None,
        wait_for_captcha_solves: Optional[bool] = None,
        verbose: Optional[int] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # For backward compatibility
        browserbase_api_key = kwargs.get("browserbase_api_key")
        browserbase_project_id = kwargs.get("browserbase_project_id")
        
        if api_key:
            self.api_key = api_key
        elif browserbase_api_key:
            self.api_key = browserbase_api_key
            
        if project_id:
            self.project_id = project_id
        elif browserbase_project_id:
            self.project_id = browserbase_project_id
            
        if model_api_key:
            self.model_api_key = model_api_key
        if model_name:
            self.model_name = model_name
        if server_url:
            self.server_url = server_url
        if headless is not None:
            self.headless = headless
        if dom_settle_timeout_ms is not None:
            self.dom_settle_timeout_ms = dom_settle_timeout_ms
        if self_heal is not None:
            self.self_heal = self_heal
        if wait_for_captcha_solves is not None:
            self.wait_for_captcha_solves = wait_for_captcha_solves
        if verbose is not None:
            self.verbose = verbose
            
        self._session_id = session_id
        
        # Configure logging based on verbosity level
        log_level = logging.ERROR
        if self.verbose == 1:
            log_level = logging.INFO
        elif self.verbose == 2:
            log_level = logging.WARNING
        elif self.verbose >= 3:
            log_level = logging.DEBUG
            
        configure_logging(
            level=log_level,
            remove_logger_name=True,
            quiet_dependencies=True
        )
        
        self._check_required_credentials()
        
    def _check_required_credentials(self):
        """Validate that required credentials are present."""
        if not self.api_key:
            raise ValueError("api_key is required (or set BROWSERBASE_API_KEY in env).")
        if not self.project_id:
            raise ValueError("project_id is required (or set BROWSERBASE_PROJECT_ID in env).")
        if not self.model_api_key:
            raise ValueError("model_api_key is required (or set OPENAI_API_KEY or ANTHROPIC_API_KEY in env).")
    
    async def _setup_stagehand(self):
        """Initialize Stagehand if not already set up."""
        if not self._stagehand:
            # Create model client options with the API key
            model_client_options = {"apiKey": self.model_api_key}
            
            # Build the StagehandConfig object
            config = StagehandConfig(
                env="BROWSERBASE",
                api_key=self.api_key,
                project_id=self.project_id,
                headless=self.headless,
                dom_settle_timeout_ms=self.dom_settle_timeout_ms,
                model_name=self.model_name,
                self_heal=self.self_heal,
                wait_for_captcha_solves=self.wait_for_captcha_solves,
                model_client_options=model_client_options,
                verbose=self.verbose,
                session_id=self._session_id,
            )
            
            # Initialize Stagehand with config and server_url
            self._stagehand = Stagehand(
                config=config,
                server_url=self.server_url
            )
            
            # Initialize the Stagehand instance
            await self._stagehand.init()
            self._page = self._stagehand.page
            self._session_id = self._stagehand.session_id
            print(f"Session ID: {self._stagehand.session_id}")
            print(f"Browser session: https://www.browserbase.com/sessions/{self._stagehand.session_id}")
    
    async def _async_run(
        self, 
        instruction: str, 
        url: Optional[str] = None,
        command_type: str = "act",
        selector: Optional[str] = None
    ) -> str:
        """Asynchronous implementation of the tool."""
        try:
            print("Setting up Stagehand...")
            await self._setup_stagehand()
 
            # Navigate to the URL if provided
            if url:
                print(f"Navigating to URL: {url}")
                await self._page.goto(url)
            
            print(f"Executing {command_type} with instruction: {instruction}")

            # Process according to command type
            if command_type.lower() == "act":
                # Create act options
                act_options = ActOptions(
                    action=instruction,
                    model_name=self.model_name,
                    dom_settle_timeout_ms=self.dom_settle_timeout_ms
                )
                
                # Execute the act command
                result = await self._page.act(act_options)
                return f"Action result: {result.message}"
                
            elif command_type.lower() == "extract":
                # Create extract options
                extract_options = ExtractOptions(
                    instruction=instruction,
                    model_name=self.model_name,
                    selector=selector,
                    dom_settle_timeout_ms=self.dom_settle_timeout_ms
                )
                
                # Execute the extract command
                result = await self._page.extract(extract_options)
                return f"Extracted data: {json.dumps(result.model_dump(), indent=2)}"
                
            elif command_type.lower() == "observe":
                # Create observe options
                observe_options = ObserveOptions(
                    instruction=instruction,
                    model_name=self.model_name,
                    only_visible=True,
                    dom_settle_timeout_ms=self.dom_settle_timeout_ms
                )
                
                # Execute the observe command
                results = await self._page.observe(observe_options)
                
                # Format the observation results
                formatted_results = []
                for i, result in enumerate(results):
                    formatted_results.append(f"Element {i+1}: {result.description}")
                    formatted_results.append(f"Selector: {result.selector}")
                    if result.method:
                        formatted_results.append(f"Suggested action: {result.method}")
                
                return "\n".join(formatted_results)
                
            else:
                return f"Unknown command type: {command_type}. Please use 'act', 'extract', or 'observe'."
            
        except Exception as e:
            return f"Error using Stagehand: {str(e)}"
        
    def _run(
        self, 
        instruction: str, 
        url: Optional[str] = None,
        command_type: str = "act",
        selector: Optional[str] = None
    ) -> str:
        """
        Run the Stagehand tool with the given instruction.
        
        Args:
            instruction: Natural language instruction for browser automation
            url: Optional URL to navigate to before executing the instruction
            command_type: Type of command to execute ('act', 'extract', or 'observe')
            selector: Optional CSS selector for extract and observe commands
        
        Returns:
            The result of the browser automation task
        """
        # Create an event loop if we're not already in one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an existing event loop, use it
                return asyncio.run_coroutine_threadsafe(
                    self._async_run(instruction, url, command_type, selector), loop
                ).result()
            else:
                # We have a loop but it's not running
                return loop.run_until_complete(self._async_run(instruction, url, command_type, selector))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._async_run(instruction, url, command_type, selector))
    
    def close(self):
        """Clean up resources when the tool is no longer needed."""
        # TODO improve this
        if self._stagehand:
            loop = asyncio.get_event_loop()
            try:
                if loop.is_running():
                    asyncio.create_task(self._stagehand.close())
                else:
                    loop.run_until_complete(self._stagehand.close())
            except RuntimeError:
                # Create a new event loop if needed
                asyncio.run(self._stagehand.close())
            
            self._stagehand = None
            self._page = None 