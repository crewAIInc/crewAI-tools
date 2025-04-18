import asyncio
import json
from typing import Any, Optional, Type

from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig, StagehandPage

from ..base_tool import BaseTool


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
    browserbase_api_key: Optional[str] = None
    browserbase_project_id: Optional[str] = None
    model_api_key: Optional[str] = None
    model_name: Optional[str] = "anthropic/claude-3-opus-20240229"
    server_url: Optional[str] = "https://api.stagehand.dev"
    
    # Instance variables
    _stagehand: Optional[Stagehand] = None
    _page: Optional[StagehandPage] = None
    _session_id: Optional[str] = None
    
    def __init__(
        self, 
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        if browserbase_api_key:
            self.browserbase_api_key = browserbase_api_key
        if browserbase_project_id:
            self.browserbase_project_id = browserbase_project_id
        if model_api_key:
            self.model_api_key = model_api_key
        if model_name:
            self.model_name = model_name
        if server_url:
            self.server_url = server_url
        self._session_id = session_id
        
        self._check_required_credentials()
        
    def _check_required_credentials(self):
        """Validate that required credentials are present."""
        if not self.browserbase_api_key:
            raise ValueError("browserbase_api_key is required (or set BROWSERBASE_API_KEY in env).")
        if not self.browserbase_project_id:
            raise ValueError("browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env).")
        if not self.model_api_key:
            raise ValueError("model_api_key is required (or set OPENAI_API_KEY or ANTHROPIC_API_KEY in env).")
    
    async def _setup_stagehand(self):
        """Initialize Stagehand if not already set up."""
        if not self._stagehand:
            config = StagehandConfig(
                browserbase_api_key=self.browserbase_api_key,
                browserbase_project_id=self.browserbase_project_id,
                model_api_key=self.model_api_key,
                model_name=self.model_name,
                server_url=self.server_url,
                session_id=self._session_id,
            )
            
            self._stagehand = Stagehand(config=config)
            await self._stagehand.init()
            self._page = self._stagehand.page
            self._session_id = self._stagehand.session_id
    
    async def _async_run(self, instruction: str, url: Optional[str] = None) -> str:
        """Asynchronous implementation of the tool."""
        try:
            await self._setup_stagehand()
            
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