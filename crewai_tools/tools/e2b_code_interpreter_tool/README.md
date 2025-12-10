# E2BCodeInterpreterTool

## Description
This tool is used to give an agent the ability to run arbitrary Python code. The code is executed in a secure cloud sandbox via E2B. After the code is run, the agent recieves the result of the code as well as any errors that occured during execution, which gives the agent debugging ability.

## Installation

- Get an API key from [e2b.dev](https://e2b.dev) and set it in the environment variables `E2B_API_KEY`.
- Install the [Code Interpreter Beta SDK](https://e2b.dev/docs/guide/beta-migration) along with the `crewai[tools]` package:

```
pip install e2b-code-interpreter==0.0.11b32 'crewai[tools]'
```

## Example

Utilize the code interpreter tool to allow your agent to run Python code:

```python
from crewai import Agent
from crewai_tools import E2BCodeInterpreterTool

# The cloud sandbox will shut down after 300 seconds, or whatever value is passed to the timeout argument.
code_interpreter = E2BCodeInterpreterTool()

Agent(
    ...
    tools=[code_interpreter],
)

# ... Use the agent ...
    
# To shut down the sandbox immediately, use:
code_interpreter.close()
```

If the `close()` method is not used, the sandbox will continue to exist until it times out, consuming additional cloud credits.

Futher examples are provided in the [E2B Cookbook](https://github.com/e2b-dev/e2b-cookbook).

## Arguments

All of the below arguments are optional:

- `api_key`: E2B [API key](https://e2b.dev/docs/getting-started/api-key) used for authentication. Defaults to `E2B_API_KEY` environment variable.
- `template`: A pre-defined template to spawn a [custom sandbox](https://e2b.dev/docs/sandbox/custom). Defaults to the standard sandbox.
- `timeout`: Specifies the timeout in seconds for the sandbox to open or execute. Defaults to 300s.
- `request_timeout`: Timeout for the creation of the sandbox itself. Defaults to 30s.
- `metadata`: Optional [metadata](https://e2b.dev/docs/sandbox/api/metadata) to be associated with the sandbox.
- `envs`: A dictionary containing [environment variables](https://e2b.dev/docs/sandbox/api/envs) to be passed to the sandbox.