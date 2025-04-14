from io import StringIO

import fitz  # PyMuPDF
import pandas as pd
from langchain.tools import BaseTool


class PDFTableExtractTool(BaseTool):
    """Tool for extracting table from PDF files and convert to markdown format"""

    name: str = "pdf_table_extract_tool"
    description: str = (
        "Extracts tables from a specific page of a PDF file and converts them to "
        "markdown format. Useful when you need to extract tabular data from PDF "
        "documents for analysis or presentation. Returns the table in markdown "
        "format as a string."
    )

    def _run(self, pdf_path: str, page_number: int, table_number: int = 0) -> str:
        """Extract a table from a PDF file and convert it to markdown format"""
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)

            # Check page number
            if page_number < 1 or page_number > len(doc):
                return f"Invalid page number. PDF has {len(doc)} pages."

            # Get the specified page (convert to 0-based index)
            page = doc[page_number - 1]

            # Extract text and split into lines
            text = page.get_text("text")
            lines = [line.strip() for line in text.split("\n") if line.strip()]

            # Simple table detection - look for consistent delimiters or spacing
            table_data = []
            for line in lines:
                # Split by multiple spaces or tabs
                cells = [cell.strip() for cell in line.split("  ") if cell.strip()]
                if cells:  # Only add non-empty rows
                    table_data.append(cells)

            if not table_data:
                return "No table found on the specified page"

            # Ensure all rows have the same number of columns
            max_cols = max(len(row) for row in table_data)
            table_data = [row + [""] * (max_cols - len(row)) for row in table_data]

            # Convert to DataFrame
            df = pd.DataFrame(table_data[1:], columns=table_data[0])

            # Convert to markdown
            buffer = StringIO()
            df.to_markdown(buf=buffer, index=False)
            return buffer.getvalue()

        except Exception as e:
            return f"Error extracting table: {str(e)}"

    async def _arun(
        self, pdf_path: str, page_number: int, table_number: int = 0
    ) -> str:
        """Async version of the tool"""
        return self._run(pdf_path, page_number, table_number)
