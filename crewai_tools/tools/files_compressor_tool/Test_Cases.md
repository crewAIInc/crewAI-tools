## Test Cases
```
import os
import shutil
import pytest
from tempfile import TemporaryDirectory
from file_compressor_tool import FileCompressorTool 


@pytest.fixture
def temp_test_dir():
    with TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "testfile.txt")
        with open(test_file, "w") as f:
            f.write("This is a test file.")
        yield tmpdir

def test_format_and_output_path_specified(temp_test_dir):
    tool = FileCompressorTool()
    input_file = os.path.join(temp_test_dir, "testfile.txt")
    output_zip = os.path.join(temp_test_dir, "output.zip")
    result = tool._run(input_path=input_file, output_path=output_zip, format="zip", overwrite=True)
    assert "Successfully compressed" in result
    assert os.path.exists(output_zip)

def test_format_specified_output_path_not_specified(temp_test_dir):
    tool = FileCompressorTool()
    input_file = os.path.join(temp_test_dir, "testfile.txt")
    result = tool._run(input_path=input_file, format="zip", overwrite=True)
    generated_output = os.path.join(os.getcwd(), "testfile.zip")
    assert "Successfully compressed" in result
    assert os.path.exists(generated_output)
    os.remove(generated_output)  # Cleanup

def test_format_specified_but_output_path_wrong_extension(temp_test_dir):
    tool = FileCompressorTool()
    input_file = os.path.join(temp_test_dir, "testfile.txt")
    output_wrong_ext = os.path.join(temp_test_dir, "wrong_output.tar")
    result = tool._run(input_path=input_file, output_path=output_wrong_ext, format="zip", overwrite=True)
    assert "output file must have a '.zip' extension" in result

def test_output_path_specified_but_format_unsupported(temp_test_dir):
    tool = FileCompressorTool()
    input_file = os.path.join(temp_test_dir, "testfile.txt")
    output_file = os.path.join(temp_test_dir, "archive.rar")  # Unsupported format
    result = tool._run(input_path=input_file, output_path=output_file, format="rar", overwrite=True)
    assert "Compression format 'rar' is not supported" in result


```
To tryout this run:
```pytest your_test_case_filename.py```
