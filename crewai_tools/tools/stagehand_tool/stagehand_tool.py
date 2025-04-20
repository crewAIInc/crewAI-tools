import asyncio
import json
import logging
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig, StagehandPage
from stagehand.utils import configure_logging

from ..base_tool import BaseTool

from dotenv import load_dotenv

load_dotenv()


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
    model_name: Optional[str] = "claude-3-7-sonnet-20250219"
    server_url: Optional[str] = "http://api.stagehand.browserbase.com/v1"
    headless: bool = False
    dom_settle_timeout_ms: int = 3000
    self_heal: bool = True
    wait_for_captcha_solves: bool = True
    verbose: int = 1
    system_prompt: Optional[str] = "You are a browser automation assistant that helps users navigate websites effectively."
    
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
        system_prompt: Optional[str] = None,
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
        if system_prompt:
            self.system_prompt = system_prompt
            
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
                system_prompt=self.system_prompt,
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
    
    async def _async_run(self, instruction: str, url: Optional[str] = None) -> str:
        """Asynchronous implementation of the tool."""
        try:
            print("Setting up Stagehand...")
            await self._setup_stagehand()

            print(f"Navigating to URL: {url}")
            
            # Navigate to the URL if provided
            if url:
                await self._page.goto(url)
            
            # Execute the instruction using the agent
            result = await self._stagehand.agent.execute(instruction)
            
            # Return the agent's response message
            return result.message
            
        except Exception as e:
            return f"Error using Stagehand: {str(e)}"
        
    def _run(self, instruction: str, url: Optional[str] = None) -> str:
        """
        Run the Stagehand tool with the given instruction.
        
        Args:
            instruction: Natural language instruction for browser automation
            url: Optional URL to navigate to before executing the instruction
        
        Returns:
            The result of the browser automation task
        """
        # Create an event loop if we're not already in one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an existing event loop, use it
                return asyncio.run_coroutine_threadsafe(
                    self._async_run(instruction, url), loop
                ).result()
            else:
                # We have a loop but it's not running
                return loop.run_until_complete(self._async_run(instruction, url))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._async_run(instruction, url))
    
    def close(self):
        """Clean up resources when the tool is no longer needed."""
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