# Environment Variables

This document describes all environment variables used in the crewAI-tools project.

## Required Environment Variables

### API Keys

| Variable | Description | Required | Min Length |
|----------|-------------|----------|------------|
| OPENAI_API_KEY | OpenAI API key for language model access | Yes | 20 |
| SERPLY_API_KEY | Serply API key for web search and content extraction | Yes | 32 |
| MULTION_API_KEY | MultiOn API key for browser automation | Yes | 32 |
| BRAVE_API_KEY | Brave Search API key for web search | Yes | 32 |
| EXA_API_KEY | EXA API key for search functionality | Yes | 32 |

## Security Notes

- All API keys should be kept secure and never committed to version control
- Use environment variables or secure key management systems to store API keys
- Consider using a `.env` file for local development (but don't commit it)
- For production, use secure environment variable management appropriate for your deployment platform

## Example Usage

```python
from crewai_tools import MultiOnTool

# Make sure to set environment variables before running
# export OPENAI_API_KEY=your_openai_key
# export MULTION_API_KEY=your_multion_key

# The tool will automatically validate and use the API key from environment
tool = MultiOnTool()
```

## Setting Environment Variables

### Local Development

Create a `.env` file in your project root (don't commit this file):

```bash
OPENAI_API_KEY=your_openai_key
SERPLY_API_KEY=your_serply_key
MULTION_API_KEY=your_multion_key
BRAVE_API_KEY=your_brave_key
EXA_API_KEY=your_exa_key
```

### Command Line

```bash
export OPENAI_API_KEY=your_openai_key
export SERPLY_API_KEY=your_serply_key
export MULTION_API_KEY=your_multion_key
export BRAVE_API_KEY=your_brave_key
export EXA_API_KEY=your_exa_key
```

## Validation

The project includes automatic validation of environment variables:
- Checks for required variables
- Validates minimum length requirements
- Provides clear error messages when variables are missing or invalid

If you encounter environment variable related errors, check:
1. That all required variables are set
2. That API keys meet minimum length requirements
3. That there are no typos in variable names
