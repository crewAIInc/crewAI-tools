import os
import json
from crewai_tools import BaseTool
from e2b_code_interpreter import CodeInterpreter

from typing import Type
from pydantic import BaseModel, Field

class E2BCodeInterpreterSchema(BaseModel):
    """Input schema for the CodeInterpreterTool, used by the agent."""

    code: str = Field(
        ...,
        description="Python3 code used to run in the Jupyter notebook cell. Non-standard packages are installed by appending !pip install [packagenames] and the Python code in one single code block.",
    )

class E2BCodeInterpreterTool(BaseTool):
    """
    This is a tool that runs arbitrary code in a Python Jupyter notebook.
    It uses E2B to run the notebook in a secure cloud sandbox.
    It requires an E2B_API_KEY to create a sandbox.
    """
    name: str = "code_interpreter"
    description: str = "Execute Python code in a Jupyter notebook cell and return any rich data (eg charts), stdout, stderr, and errors."
    args_schema: Type[BaseModel] = E2BCodeInterpreterSchema
    _code_interpreter_tool: CodeInterpreter | None = None

    def __init__(self, *args, **kwargs):
        # Call the superclass's init method
        super().__init__(*args, **kwargs)

        # Ensure that the E2B_API_KEY environment variable is set
        if "E2B_API_KEY" not in os.environ:
            raise Exception(
                "Code Interpreter tool called while E2B_API_KEY environment variable is not set. Please get your E2B API key here https://e2b.dev/docs and set the E2B_API_KEY environment variable."
            )

        # Initialize the code interpreter tool
        self._code_interpreter_tool = CodeInterpreter()

    def _run(self, code: str) -> str:
        # Execute the code using the code interpreter
        execution = self._code_interpreter_tool.notebook.exec_cell(code)
        
        # Extract relevant execution details
        result = {
            "results": [str(item) for item in execution.results],
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
            "error": str(execution.error),
        }
        
        # Convert the result dictionary to a JSON string since CrewAI expects a string output
        content = json.dumps(result, indent=2)
        
        return content

    def close(self):
        # Close the interpreter tool when done
        self._code_interpreter_tool.kill()