# 📦 FileCompressorTool

The **FileCompressorTool** is a utility for compressing individual files or entire directories (including nested subdirectories) into a `.zip` archive. This is useful for archiving logs, documents, datasets, or backups in a compact format.

---

## Description

This tool:
- Accepts a **file or directory** as input.
- Supports **recursive compression** of subdirectories.
- Lets you define a **custom output zip path** or defaults to the current directory.
- Handles **overwrite protection** to avoid unintentional data loss.

---

## Arguments

| Argument      | Type      | Required | Description                                                                 |
|---------------|-----------|----------|-----------------------------------------------------------------------------|
| `input_path`  | `str`     | ✅       | Path to the file or directory you want to compress.                         |
| `output_zip`  | `str`     | ❌       | Optional path for the resulting `.zip` file. Defaults to `./<name>.zip`.    |
| `overwrite`   | `bool`    | ❌       | Whether to overwrite an existing zip file. Defaults to `False`.            |

---

## Usage Example

```python
from crewai_tools import FileCompressorTool

# Initialize the tool
tool = FileCompressorTool()

# Compress a directory with subdirectories and files
result = tool._run(
    input_path="./data/project_docs",           # Folder containing subfolders & files
    output_zip="./output/project_docs.zip",     # Optional output path
    overwrite=True                              # Allow overwriting if file exists
)
print(result)
# Example output: Successfully compressed './data/project_docs' into './output/project_docs.zip'
```

---

## Example Scenarios

### Compress a single file:
```python
# Compress a single file into a zip archive
result = tool._run(input_path="report.pdf")
# Example output: Successfully compressed 'report.pdf' into './report.zip'
```

### Compress a directory with nested folders:
```python
# Compress a directory containing nested subdirectories and files
result = tool._run(input_path="./my_data", overwrite=True)
# Example output: Successfully compressed 'my_data' into './my_data.zip'
```

### Use a custom output path:
```python
# Compress a directory and specify a custom zip output location
result = tool._run(input_path="./my_data", output_zip="./backups/my_data_backup.zip", overwrite=True)
# Example output: Successfully compressed 'my_data' into './backups/my_data_backup.zip'
```

### Prevent overwriting an existing zip file:
```python
# Try to compress a directory without overwriting an existing zip file
result = tool._run(input_path="./my_data", output_zip="./backups/my_data_backup.zip", overwrite=False)
# Example output: Output zip './backups/my_data_backup.zip' already exists and overwrite is set to False.
```
