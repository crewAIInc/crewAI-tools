import os
import shutil
import tempfile
import pytest
from crewai_tools.tools.files_compressor_tool import FileCompressorTool

@pytest.fixture
def sample_dir():
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w") as f:
        f.write("This is a test file.")
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_zip_compression(sample_dir):
    tool = FileCompressorTool()
    output_path = os.path.join(tempfile.gettempdir(), "test_archive.zip")

    result = tool._run(
        input_path=sample_dir,
        output_path=output_path,
        overwrite=True,
        format="zip"
    )

    assert os.path.exists(output_path)
    assert "Successfully compressed" in result
    os.remove(output_path)

def test_tar_gz_compression(sample_dir):
    tool = FileCompressorTool()
    output_path = os.path.join(tempfile.gettempdir(), "test_archive.tar.gz")

    result = tool._run(
        input_path=sample_dir,
        output_path=output_path,
        overwrite=True,
        format="tar.gz"
    )

    assert os.path.exists(output_path)
    assert "Successfully compressed" in result
    os.remove(output_path)

def test_invalid_input_path():
    tool = FileCompressorTool()
    result = tool._run(input_path="invalid/path", output_path="dummy.zip")
    assert "does not exist" in result

def test_no_overwrite(sample_dir):
    tool = FileCompressorTool()
    output_path = os.path.join(tempfile.gettempdir(), "test_no_overwrite.zip")

    # Create a dummy file to simulate existing archive
    with open(output_path, "w") as f:
        f.write("Existing archive")

    result = tool._run(
        input_path=sample_dir,
        output_path=output_path,
        overwrite=False,
        format="zip"
    )

    assert "already exists and overwrite is set to False" in result
    os.remove(output_path)

def test_unsupported_format(sample_dir):
    tool = FileCompressorTool()
    result = tool._run(
        input_path=sample_dir,
        output_path="archive.rar",
        overwrite=True,
        format="rar"
    )
    assert "Compression format 'rar' is not supported" in result

def test_extension_mismatch(sample_dir):
    tool = FileCompressorTool()
    result = tool._run(
        input_path=sample_dir,
        output_path="archive.wrongext",
        overwrite=True,
        format="zip"
    )
    assert "output file must have a '.zip' extension" in result

def test_generate_output_path_for_file():
    tool = FileCompressorTool()
    file_path = tempfile.NamedTemporaryFile(delete=False)
    file_path.write(b"test")
    file_path.close()

    result = tool._generate_output_path(file_path.name, "zip")
    assert result.endswith(".zip")
    os.remove(file_path.name)

def test_generate_output_path_for_directory(sample_dir):
    tool = FileCompressorTool()
    result = tool._generate_output_path(sample_dir, "tar")
    assert result.endswith(".tar")

def test_prepare_output_creates_directory():
    tool = FileCompressorTool()
    temp_dir = tempfile.mkdtemp()
    new_dir = os.path.join(temp_dir, "subfolder")
    output_path = os.path.join(new_dir, "archive.zip")

    result = tool._prepare_output(output_path, overwrite=True)
    assert result
    assert os.path.exists(new_dir)
    shutil.rmtree(temp_dir)
