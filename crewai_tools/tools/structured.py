from typing import Any, Callable, Optional, Type
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel as PydanticBaseModel
from textwrap import dedent

class StructuredTool(BaseTool):
    """A tool that executes functions with structured inputs using a schema."""

    func: Callable[..., Any]
    """The callable function that implements the tool's functionality."""

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool's function with the provided arguments."""
        return self.func(*args, **kwargs)

    @classmethod
    def from_function(
        cls,
        func: Callable,
        args_schema: Type[PydanticBaseModel],
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> "StructuredTool":
        """Create a new StructuredTool instance from a function.

        Args:
            func: Function to wrap as a tool
            name: Custom name for the tool
            description: Custom description of the tool's functionality
            args_schema: Pydantic model defining the expected argument structure
            **kwargs: Additional tool configuration parameters, like cache_function

        Returns:
            StructuredTool: A new tool instance wrapping the provided function
        """
        name = name or func.__name__

        if description is None:
            description = func.__doc__
            if description is None:
                raise ValueError("Function must have a docstring if description not provided.")
            # Clean up docstring
            description = dedent(description).strip()
        
        return cls(
            func=func,
            args_schema=args_schema,
            name=name,
            description=description,
            **kwargs,
        )
