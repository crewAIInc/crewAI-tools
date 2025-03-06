# Cognee Tools

## Description

These tools enable integration with Cognee, an AI knowledge graph library. You can:
- Add text to the knowledge base
- Cognify the knowledge graph
- Search for insights

## Installation

```bash
uv pip install 'crewai[tools] cognee'
```

## Usage

```python
from crewai_tools import CogneeAddTool, CogneeCognifyTool, CogneeSearchTool

add_tool = CogneeAddTool()
cognify_tool = CogneeCognifyTool()
search_tool = CogneeSearchTool()

# Then in your Agent:
agent = Agent(
    name="cognee_agent",
    ...
    tools=[add_tool, cognify_tool, search_tool],
)

```

```
---

## 4. Expose Tools from `tools/__init__.py`

If you want them automatically importable from `crewai_tools` top-level, add lines to `crewai_tools/tools/__init__.py`:

```python
from .cognee_tool import (
    CogneeAddTool,
    CogneeCognifyTool,
    CogneeSearchTool,
)

```

And **optionally** from `crewai_tools/__init__.py`:

```python
# in crewai_tools/__init__.py
from .tools import (
    # ...
    CogneeAddTool,
    CogneeCognifyTool,
    CogneeSearchTool,
)

```

So users can do:
```python

from crewai_tools import CogneeAddTool, CogneeSearchTool

```