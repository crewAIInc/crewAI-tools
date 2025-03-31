from typing import Any, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel


class HumanInputToolSchema(BaseModel):
    """Input schema for HumanInputTool.
    
    This schema doesn't require any specific fields since the tool
    will prompt for human input directly via CLI.
    """
    pass


class HumanInputTool(BaseTool):
    """A tool for requesting input directly from a human via CLI.
    
    This tool inherits from BaseTool and provides functionality to request
    input from a human through the command line interface. It doesn't require
    any specific parameters, as it will directly prompt for input when run.
    
    Args:
        prompt (Optional[str]): Optional custom prompt to display when requesting input.
        **kwargs: Additional keyword arguments passed to BaseTool.
        
    Example:
        >>> tool = HumanInputTool(prompt="Please provide additional information: ")
        >>> user_input = tool.run()  # Displays prompt and returns user input
        >>> user_input = tool.run(prompt="Enter a different prompt: ")  # Uses provided prompt
    """
    
    name: str = "Get input from human"
    description: str = "A tool that requests direct input from a human via the command line interface. No parameters are required as it will prompt for input when run."
    args_schema: Type[BaseModel] = HumanInputToolSchema
    prompt: Optional[str] = None
    
    def __init__(self, prompt: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the HumanInputTool.
        
        Args:
            prompt (Optional[str]): Optional custom prompt to display when requesting input.
                If not provided, a default prompt will be used.
            **kwargs: Additional keyword arguments passed to BaseTool.
        """
        if prompt is not None:
            kwargs['description'] = f"A tool that requests human input via CLI with the prompt: '{prompt}'. You can also provide a different 'prompt' parameter to use a different message."
            
        super().__init__(**kwargs)
        self.prompt = prompt
    
    def _run(
        self,
        **kwargs: Any,
    ) -> str:
        # Get the prompt from kwargs or use the default one
        prompt = kwargs.get("prompt", self.prompt)
        
        # Use a default prompt if none was provided
        if prompt is None:
            prompt = "Human input required: "
            
        try:
            # Request input from the user
            user_input = input(prompt)
            return user_input
        except EOFError:
            return "Error: End of input stream reached."
        except KeyboardInterrupt:
            return "Error: Input interrupted by user."
        except Exception as e:
            return f"Error: Failed to get human input. {str(e)}"