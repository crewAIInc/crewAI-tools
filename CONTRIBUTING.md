# Contributing to CrewAI Tools

Thank you for your interest in contributing to CrewAI Tools! This guide will help you create and submit new tools to the official repository.

## 🚀 Quick Start

1. **Fork** this repository
2. **Clone** your fork locally
3. **Set up** the development environment
4. **Create** your tool following our patterns
5. **Test** thoroughly
6. **Submit** a pull request

## 📋 Prerequisites

- Python 3.10+ (supports up to 3.13)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Git for version control
- Basic understanding of Python and Pydantic

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/crewAI-tools.git
cd crewAI-tools

# Install dependencies
uv sync

# Set up pre-commit hooks
pre-commit install

# Run tests to ensure everything works
uv run pytest
```

## 🏗️ Creating a New Tool

### Step 1: Plan Your Tool

Before coding, consider:
- **Purpose**: What specific problem does your tool solve?
- **Uniqueness**: Does similar functionality already exist?
- **Dependencies**: What external services/APIs are needed?
- **Naming**: Follow the pattern `{Service/Function}Tool`

### Step 2: Create Tool Structure

```bash
# Create tool directory
mkdir crewai_tools/tools/my_awesome_tool
touch crewai_tools/tools/my_awesome_tool/__init__.py
touch crewai_tools/tools/my_awesome_tool/my_awesome_tool.py
```

### Step 3: Implement Your Tool

Create `my_awesome_tool.py` following this template:

```python
from typing import Any, List, Optional, Type
from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, Field


class MyAwesomeToolSchema(BaseModel):
    """Input schema for MyAwesome Tool."""
    
    query: str = Field(
        ..., 
        description="The main input parameter"
    )
    optional_param: Optional[str] = Field(
        None, 
        description="Optional parameter"
    )


class MyAwesomeTool(BaseTool):
    """
    Brief description of what the tool does.
    
    Longer description explaining functionality, use cases,
    and any important details about the tool.
    
    Dependencies:
        - requests>=2.31.0
        - your-api-sdk>=1.0.0
    """
    
    name: str = "My Awesome Tool"
    description: str = "Brief description for agents"
    args_schema: Type[BaseModel] = MyAwesomeToolSchema
    
    # Configuration
    api_endpoint: str = "https://api.example.com"
    timeout: int = 30
    
    # Environment variables
    env_vars: List[EnvVar] = [
        EnvVar(
            name="MY_API_KEY", 
            description="API key for My Awesome Service",
            required=True
        ),
    ]
    
    def _run(self, **kwargs) -> str:
        """Execute the tool's functionality."""
        query = kwargs.get("query")
        optional_param = kwargs.get("optional_param")
        
        try:
            # Your implementation here
            result = self._perform_operation(query, optional_param)
            return result
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _perform_operation(self, query: str, optional_param: Optional[str]) -> str:
        """Core tool logic."""
        # Implement your functionality
        return "Tool result"
```

### Step 4: Add Exports

**Update `crewai_tools/tools/my_awesome_tool/__init__.py`:**
```python
from .my_awesome_tool import MyAwesomeTool

__all__ = ["MyAwesomeTool"]
```

**Update `crewai_tools/tools/__init__.py`** (add alphabetically):
```python
from .my_awesome_tool.my_awesome_tool import MyAwesomeTool
```

**Update `crewai_tools/__init__.py`** (add alphabetically):
```python
MyAwesomeTool,
```

### Step 5: Handle Dependencies

If your tool needs external packages, add them to `pyproject.toml`:

```toml
[project.optional-dependencies]
my-awesome-service = [
    "awesome-sdk>=1.0.0",
    "requests>=2.31.0",
]
```

### Step 6: Write Tests

Create `tests/tools/test_my_awesome_tool.py`:

```python
import pytest
from unittest.mock import patch
from crewai_tools import MyAwesomeTool


class TestMyAwesomeTool:
    def test_tool_initialization(self):
        tool = MyAwesomeTool()
        assert tool.name == "My Awesome Tool"
        assert tool.description is not None
    
    @patch.dict('os.environ', {'MY_API_KEY': 'test-key'})
    def test_successful_execution(self):
        tool = MyAwesomeTool()
        result = tool._run(query="test query")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_error_handling(self):
        tool = MyAwesomeTool()
        # Test with invalid input
        result = tool._run(query="")
        assert "Error" in result or result != ""
```

### Step 7: Generate Tool Specifications

```bash
python generate_tool_specs.py
```

This updates `tool.specs.json` with your tool's metadata.

## ✅ Quality Assurance

### Run Tests
```bash
# Run your specific tests
uv run pytest tests/tools/test_my_awesome_tool.py -v

# Run all tests
uv run pytest
```

### Type Checking
```bash
uv run pyright
```

### Pre-commit Checks
```bash
pre-commit run --all-files
```

## 📝 Best Practices

### Code Quality
- **Follow existing patterns** - study similar tools
- **Use type hints** throughout your code
- **Add comprehensive docstrings** with examples
- **Handle errors gracefully** with descriptive messages
- **Implement rate limiting** for API tools when needed

### Security
- **Never hardcode secrets** - use environment variables
- **Validate all inputs** using Pydantic schemas
- **Sanitize outputs** to prevent data leakage
- **Use HTTPS** for all external API calls

### Documentation
- **Clear descriptions** of purpose and functionality
- **Document all parameters** with examples
- **List dependencies** and requirements
- **Provide usage examples** in docstrings

### Testing
- **Test happy path** scenarios
- **Test error conditions** and edge cases
- **Mock external APIs** to avoid test dependencies
- **Test input validation** with invalid data

## 🚀 Submission Process

### 1. Create Feature Branch
```bash
git checkout -b feature/add-my-awesome-tool
```

### 2. Commit Your Changes
```bash
git add .
git commit -m "feat: add MyAwesome tool for [functionality]

- Implements [specific feature]
- Adds support for [service/API]
- Includes comprehensive tests and documentation"
```

### 3. Push and Create PR
```bash
git push origin feature/add-my-awesome-tool
```

Create a pull request with:
- **Clear title**: `feat: add MyAwesome tool for [functionality]`
- **Detailed description** of the tool's purpose
- **Usage examples** showing how to use the tool
- **Testing information** and coverage details
- **Dependencies** added (if any)

### 4. Review Process
- Automated checks will run (tests, linting, type checking)
- Maintainers will review for code quality and consistency
- Address feedback promptly and professionally
- Update documentation if requested

## 🎯 Tool Categories

Consider which category your tool fits into:

- **File Management**: Reading, writing, processing files
- **Web Scraping**: Extracting data from websites
- **Database Integration**: Connecting to various databases
- **API Integration**: Interfacing with external services
- **AI Services**: Leveraging AI/ML capabilities
- **Search Tools**: Finding and retrieving information
- **Document Processing**: Working with PDFs, docs, etc.

## ⚠️ Common Pitfalls

- **Forgetting to update `__init__.py` files** - your tool won't be importable
- **Skipping tool specification generation** - breaks the automated tooling
- **Hardcoding configuration** - makes tools inflexible
- **Poor error handling** - leads to cryptic failures
- **Missing tests** - reduces confidence in your tool
- **Breaking existing functionality** - always run full test suite

## 🆘 Getting Help

- **Study existing tools** for patterns and inspiration
- **Check our [community forum](https://community.crewai.com/)** for questions
- **Open a GitHub discussion** before starting complex tools
- **Ask for early feedback** on your approach

## 📋 Checklist Before Submitting

- [ ] Tool follows the established patterns
- [ ] All `__init__.py` files updated
- [ ] Dependencies added to `pyproject.toml` (if needed)
- [ ] Comprehensive tests written and passing
- [ ] Tool specifications generated
- [ ] Documentation is clear and complete
- [ ] Error handling is robust
- [ ] No hardcoded secrets or configuration
- [ ] Pre-commit checks pass
- [ ] PR description is detailed and helpful

## 🎉 After Your PR is Merged

- Your tool will be available in the next release
- Consider writing a blog post or tutorial about your tool
- Help maintain your tool by responding to issues
- Consider contributing more tools or improvements

---

Thank you for contributing to CrewAI Tools! Your contributions help make AI agents more capable and useful for everyone. 🚀
