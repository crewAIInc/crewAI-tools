import os

import pytest

from crewai_tools.tools.pdf_table_extract_tool import PDFTableExtractTool


def test_pdf_table_extract_tool_initialization():
    tool = PDFTableExtractTool()
    assert tool.name == "pdf_table_extract_tool"
    assert isinstance(tool.description, str)


def test_pdf_table_extract_tool_invalid_file():
    tool = PDFTableExtractTool()
    result = tool._run(pdf_path="nonexistent.pdf", page_number=1)
    assert "Error" in result


def test_pdf_table_extract_tool_with_real_pdf():
    # Ensure the fixtures directory exists
    os.makedirs("tests/fixtures", exist_ok=True)

    # Create a test PDF with a table
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    # Sample data
    data = [
        ["Name", "Age", "Department", "Salary"],
        ["John Doe", "30", "Engineering", "$80,000"],
        ["Jane Smith", "25", "Marketing", "$70,000"],
        ["Bob Johnson", "35", "Sales", "$90,000"],
    ]

    pdf_path = "tests/fixtures/sample_table.pdf"
    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.axis("tight")
        ax.axis("off")
        table = ax.table(
            cellText=data[1:], colLabels=data[0], cellLoc="center", loc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        pdf.savefig(fig)
        plt.close()

    # Test the tool
    tool = PDFTableExtractTool()
    result = tool._run(pdf_path=pdf_path, page_number=1)
    print("\nExtracted table:")
    print(result)

    assert isinstance(result, str)
    assert "John" in result or "Name" in result
    assert "No table found" not in result


@pytest.mark.asyncio
async def test_pdf_table_extract_tool_async():
    tool = PDFTableExtractTool()
    result = await tool._arun(pdf_path="nonexistent.pdf", page_number=1)
    assert isinstance(result, str)
