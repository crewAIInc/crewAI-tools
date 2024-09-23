# E2BCodeInterpreterTool

## Description
This tool is used to give an agent the ability to run arbitrary Python code. The code is executed in a secure cloud sandbox via E2B. After the code is run, the agent recieves the result of the code as well as any errors that occured during execution, which gives the agent debugging ability.

## Installation

- Get an API key from [e2b.dev](https://e2b.dev) and set it in the environment variables `E2B_API_KEY`.
- Install the [Code Interpreter Beta SDK](https://e2b.dev/docs/guide/beta-migration) along with the `crewai[tools]` package:

```
pip install e2b-code-interpreter>=0.0.11b32 'crewai[tools]'
```

## Example

Utilize the code interpreter tool to allow your agent to run Python code:

```python
from crewai import Agent
from crewai_tools import E2BCodeInterpreterTool

code_interpreter = E2BCodeInterpreterTool()

Agent(
    ...
    tools=[E2BCodeInterpreterTool()],
)

# ... Use the agent ...
    
code_interpreter.close()
```

Futher examples are provided in the [E2B Cookbook](https://github.com/e2b-dev/e2b-cookbook).
