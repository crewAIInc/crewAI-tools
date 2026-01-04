# PDF Table Extract Tool

Extracting complex formatted tables from PDFs is a very difficult task and it has been observed that data is not retrieved properly and thereby it is difficult to query on that. Here's a specialized
tool for extracting tables from PDF documents and converting them to markdown format.

## Features
- Extracts tables from specified pages of PDF documents
- Converts tables to markdown format for easy integration
- Handles multiple tables per page
- Supports large tables
- Provides both synchronous and asynchronous interfaces

## Installation

```bash
pip install crewai-tools

Dependencies

PyMuPDF (fitz)
pandas
tabulate

Usage
With CrewAI

from crewai import Agent
from crewai_tools.tools.pdf_table_extract_tool import PDFTableExtractTool

# Initialize the tool
pdf_tool = PDFTableExtractTool()

# Create an agent with the tool
agent = Agent(
    role='Data Analyst',
    goal='Extract and analyze tables from PDF reports',
    backstory="You are an expert at extracting and analyzing tabular data.",
    tools=[pdf_tool]
)

Direct Usage

from crewai_tools.tools.pdf_table_extract_tool import PDFTableExtractTool

tool = PDFTableExtractTool()

# Extract table from first page
result = tool.run("document.pdf, 1")
print(result)

Input Format
The tool accepts input in the format: "pdf_path, page_number"

pdf_path: Path to the PDF file (required)
page_number: Page number to extract table from (optional, defaults to 1)

Output
Returns a string containing the extracted table in markdown format.
Error Handling

Returns error message if PDF file not found
Returns error message if page number is invalid
Returns error message if no table is found on the specified page

Testing
Run the test suite:

python -m pytest tests/tools/test_pdf_table_extract_tool.py -v
