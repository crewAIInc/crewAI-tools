from crewai.tools import BaseTool
import subprocess


class CurlCommandoTool(BaseTool):
    name: str = "Execute a curl commando"
    description: str = "Mandatory full arguments and the full target url for a curl commando"

    def _run(self, argument: str) -> str:
        # Implementation goes here
        base_cmd = ['curl', '--silent', '--show-error']
        full_cmd = base_cmd + argument.split()
        try:
            result = subprocess.run(full_cmd, stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8')
        except Exception as e:
         return f"Error: Failed to execute the curl commando with the the content curl {argument}. {str(e)}"
