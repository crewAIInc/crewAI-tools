from crewai_tools import BaseTool
import contextlib
import io
import subprocess
import sys

class PythonREPLTool(BaseTool):
    name: str = "Python_REPL"
    description: str = "A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`."

    def _run(self, command: str) -> str:
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                exec(command)
            return buffer.getvalue()
        except Exception as e:
            return str(e)
    
    def check_and_install_package(self, package: str) -> str:
        try:
            import importlib
            importlib.import_module(package)
            return f"Package '{package}' is already installed."
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                return f"Package '{package}' installed successfully."
            except subprocess.CalledProcessError as e:
                return f"Error installing package '{package}': {str(e)}"
