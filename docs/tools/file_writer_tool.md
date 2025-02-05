# FileWriterTool

## Description
A secure, cross-platform compatible tool for writing content to files with built-in security features and progress tracking.

## Installation
```bash
pip install 'crewai[tools]'
```

## Features
- Cross-platform compatibility (Windows, Linux, macOS)
- Secure path handling to prevent directory traversal
- Permission validation before write operations
- Configurable file size limits
- Progress tracking for large files
- UTF-8 encoding support by default
- Automatic directory creation

## Usage

### Basic Usage
```python
from crewai_tools import FileWriterTool

# Simple text file
writer = FileWriterTool()
result = writer.run(
    filename="output.txt",
    content="Hello World",
    directory="./output"
)

# JSON data
result = writer.run(
    filename="data.json",
    content='{"key": "value"}',
    directory="./data"
)
```

### Advanced Options
```python
writer = FileWriterTool()
result = writer.run(
    filename="large_file.txt",
    content="Large content here...",
    directory="./data",
    overwrite="True",      # Allow overwriting existing files
    max_size=1_000_000,    # 1MB size limit
    encoding="utf-8"       # Specify encoding (default: utf-8)
)
```

## Error Handling
```python
try:
    writer = FileWriterTool()
    result = writer.run(
        filename="output.txt",
        content="Hello World",
        directory="./secure/data"
    )
    if "error" in result.lower():
        print(f"Failed: {result}")
    else:
        print("Success!")
except ValueError as e:
    # Handle validation errors (invalid paths, size limits)
    print(f"Validation error: {e}")
except Exception as e:
    # Handle other errors (permissions, disk space)
    print(f"Error: {e}")
```

## Best Practices
1. Path Handling
   - Use forward slashes (/) in paths for cross-platform compatibility
   - Avoid absolute paths and directory traversal
   - Keep paths relative to your project directory

2. File Size Management
   - Set appropriate max_size limits for your use case
   - Default limit is 10MB
   - Consider chunking large files into smaller pieces

3. Encoding
   - Default encoding is UTF-8
   - Explicitly specify encoding if working with special characters
   - Test with various character sets if handling international text

4. Error Handling
   - Always check the return value for error messages
   - Implement proper exception handling
   - Validate directory permissions before writing

## Security Considerations
- Path validation prevents directory traversal attacks
- Permission checks ensure secure file operations
- Size limits prevent disk space abuse
- Progress tracking helps monitor large file operations
- Proper encoding handling prevents data corruption

## Compatibility
- Windows: Full support with UTF-8 encoding
- Linux: Full support
- macOS: Full support
- Python versions: 3.7+

## Common Issues and Solutions

### Windows-Specific
```python
# Correct path handling on Windows
writer.run(
    filename="data.txt",
    directory="data/subfolder",  # Use forward slashes
    content="Hello"
)
```

### Permission Issues
```python
# Check directory permissions first
import os
from pathlib import Path

directory = Path("./secure/data")
if os.access(directory, os.W_OK):
    writer.run(
        filename="secure.txt",
        directory=str(directory),
        content="Sensitive data"
    )
```

### Large Files
```python
# Handle large files with size limit
writer.run(
    filename="large.dat",
    content=large_content,
    max_size=50_000_000,  # 50MB limit
    directory="data"
)
```
