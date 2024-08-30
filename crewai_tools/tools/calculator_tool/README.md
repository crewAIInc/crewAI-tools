# WebsiteSearchTool

## Description
This tool is designed to perform calculations within the context of a given problem. It navigates through the information provided to execute operations representative of the given problem. 

## Installation
Install the crewai_tools package by executing the following command in your terminal:

```shell
pip install 'crewai[tools]'
```

## Example
To utilize the CalculatorTool for different use cases, follow these examples:

```python
from crewai_tools import CalculatorTool

# To enable the tool to calculate any problem/operation the agent comes across or learns about during its operation
tool = CalculatorTool()

# OR

# To restrict the tool to only calculate a specific mathematical operation.
tool = CalculatorTool(operation='500*17')
```

## Arguments
- `operation` : A required argument that specifies the mathematical operation to evaluate as a string. If the tool is initialized without this argument, it calculates any problem or operation it encounters.

