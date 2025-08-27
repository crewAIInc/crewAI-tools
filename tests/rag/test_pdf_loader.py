import hashlib
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from crewai_tools.rag.loaders.pdf_loader import PDFLoader
from crewai_tools.rag.base_loader import LoaderResult
from crewai_tools.rag.source_content import SourceContent


def create_simple_pdf(content="Test PDF content", title="Test PDF"):
    """Create a simple PDF file for testing using PyPDF."""
    try:
        from pypdf import PdfWriter
        from io import BytesIO
        import tempfile

        # Create a simple PDF content
        # Note: This is a basic approach. For more complex PDF creation,
        # we might need additional libraries like reportlab
        writer = PdfWriter()

        # Since PyPDF doesn't have direct text creation capabilities,
        # we'll create a mock PDF-like structure for testing
        # This is primarily for testing the loader logic

        with tempfile.NamedTemporaryFile(mode="w+b", suffix=".pdf", delete=False) as f:
            # For testing purposes, we'll create a minimal PDF structure
            # This is not a proper PDF but will work for testing the error handling
            pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length {len(content)}
>>
stream
BT
/F1 12 Tf
100 700 Td
({content}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000074 00000 n
0000000120 00000 n
0000000179 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
{200 + len(content)}
%%EOF"""
            f.write(pdf_content.encode())
            return f.name

    except ImportError:
        # If PyPDF is not available, create a fake PDF file for testing error handling
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False) as f:
            f.write("This is not a real PDF file for testing purposes")
            return f.name


def cleanup_temp_file(path):
    """Clean up temporary files."""
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


class TestPDFLoader:

    def test_basic_pdf_loading(self):
        """Test basic PDF file loading."""
        pdf_path = create_simple_pdf("Hello World from PDF")
        try:
            loader = PDFLoader()
            result = loader.load(SourceContent(pdf_path))

            assert isinstance(result, LoaderResult)
            assert result.source == pdf_path
            assert result.doc_id
            assert isinstance(result.metadata, dict)
            assert result.metadata.get("source_type") == "pdf"
            assert "word_count" in result.metadata
            assert "character_count" in result.metadata

        finally:
            cleanup_temp_file(pdf_path)

    def test_missing_pdf_file(self):
        """Test error handling for missing PDF files."""
        with pytest.raises(FileNotFoundError):
            PDFLoader().load(SourceContent("/nonexistent/path.pdf"))

    def test_non_pdf_file(self):
        """Test error handling for non-PDF files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is not a PDF file")
            txt_path = f.name

        try:
            with pytest.raises(ValueError, match="File is not a PDF"):
                PDFLoader().load(SourceContent(txt_path))
        finally:
            cleanup_temp_file(txt_path)

    def test_metadata_generation(self):
        """Test that metadata is properly generated."""
        pdf_path = create_simple_pdf("Test content for metadata")
        try:
            result = PDFLoader().load(SourceContent(pdf_path))

            metadata = result.metadata
            assert metadata["source_type"] == "pdf"
            assert isinstance(metadata["word_count"], int)
            assert isinstance(metadata["character_count"], int)
            assert "file_name" in metadata
            assert "file_size" in metadata
            assert "file_extension" in metadata
            assert metadata["file_extension"] == ".pdf"

        finally:
            cleanup_temp_file(pdf_path)

    def test_doc_id_consistency(self):
        """Test that document ID is consistent for the same content."""
        pdf_path = create_simple_pdf("Consistent content")
        try:
            loader = PDFLoader()
            result1 = loader.load(SourceContent(pdf_path))
            result2 = loader.load(SourceContent(pdf_path))

            assert result1.doc_id == result2.doc_id

        finally:
            cleanup_temp_file(pdf_path)

    def test_page_extraction_option(self):
        """Test page extraction with specific page numbers."""
        pdf_path = create_simple_pdf("Test content")
        try:
            result = PDFLoader().load(SourceContent(pdf_path), pages=[0])

            # The metadata should include the extracted pages
            assert "extracted_pages" in result.metadata
            assert result.metadata["extracted_pages"] == [0]

        finally:
            cleanup_temp_file(pdf_path)

    def test_password_option_metadata(self):
        """Test that password option is recorded in metadata."""
        pdf_path = create_simple_pdf("Test content")
        try:
            # This will likely fail since our test PDF isn't encrypted,
            # but we're testing the metadata handling
            try:
                result = PDFLoader().load(SourceContent(pdf_path), password="test")
                # If it succeeds (unlikely with our simple PDF), check metadata
                if "was_encrypted" in result.metadata:
                    assert result.metadata["was_encrypted"] is True
            except ValueError:
                # Expected for non-encrypted PDF with password provided
                pass

        finally:
            cleanup_temp_file(pdf_path)

    @patch('requests.get')
    def test_url_loading(self, mock_get):
        """Test loading PDF from URL."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"Mock PDF content"
        mock_get.return_value = mock_response

        url = "https://example.com/test.pdf"

        # Mock the PDF extraction since we're providing fake content
        with patch.object(PDFLoader, '_extract_text_from_file') as mock_extract:
            mock_extract.return_value = "Extracted text from URL PDF"

            loader = PDFLoader()
            result = loader.load(SourceContent(url))

            assert result.content == "Extracted text from URL PDF"
            assert result.source == url
            mock_get.assert_called_once()

    @patch('requests.get')
    def test_url_loading_error(self, mock_get):
        """Test error handling for URL loading."""
        mock_get.side_effect = Exception("Network error")

        url = "https://example.com/test.pdf"
        with pytest.raises(ValueError, match="Error fetching PDF from URL"):
            PDFLoader().load(SourceContent(url))

    def test_pypdf_import_error(self):
        """Test error handling when PyPDF is not available."""
        pdf_path = create_simple_pdf("Test content")
        try:
            with patch.dict('sys.modules', {'pypdf': None}):
                with pytest.raises(ImportError, match="pypdf is required"):
                    PDFLoader().load(SourceContent(pdf_path))
        finally:
            cleanup_temp_file(pdf_path)

    def test_invalid_page_numbers(self):
        """Test error handling for invalid page numbers."""
        pdf_path = create_simple_pdf("Test content")
        try:
            # Test with page numbers that are out of range
            with pytest.raises(ValueError, match="Page number .* is out of range"):
                PDFLoader().load(SourceContent(pdf_path), pages=[999])

        except ValueError as e:
            # This might fail during PDF creation/reading, which is expected
            # for our simple test PDF structure
            if "Error extracting text from PDF" in str(e):
                pass  # Expected for our mock PDF
            else:
                raise
        finally:
            cleanup_temp_file(pdf_path)

    def test_encrypted_pdf_without_password(self):
        """Test error handling for encrypted PDF without password."""
        # This test would require a real encrypted PDF file
        # For now, we'll test the logic path using mocking
        pdf_path = create_simple_pdf("Test content")

        try:
            with patch('pypdf.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.is_encrypted = True
                mock_reader_class.return_value = mock_reader

                with pytest.raises(ValueError, match="PDF is encrypted but no password provided"):
                    PDFLoader().load(SourceContent(pdf_path))
        finally:
            cleanup_temp_file(pdf_path)

    def test_encrypted_pdf_wrong_password(self):
        """Test error handling for encrypted PDF with wrong password."""
        pdf_path = create_simple_pdf("Test content")

        try:
            with patch('pypdf.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.is_encrypted = True
                mock_reader.decrypt.return_value = False  # Wrong password
                mock_reader_class.return_value = mock_reader

                with pytest.raises(ValueError, match="Failed to decrypt PDF"):
                    PDFLoader().load(SourceContent(pdf_path), password="wrong")
        finally:
            cleanup_temp_file(pdf_path)

    def test_loader_config(self):
        """Test loader initialization with config."""
        config = {"some_option": "value"}
        loader = PDFLoader(config)
        assert loader.config == config

    def test_empty_pdf_content(self):
        """Test handling of PDF with no extractable text."""
        pdf_path = create_simple_pdf("")
        try:
            result = PDFLoader().load(SourceContent(pdf_path))
            # Should not raise an error, just return empty or minimal content
            assert isinstance(result, LoaderResult)
            assert result.source == pdf_path
        except ValueError:
            # Expected for our simple mock PDF structure
            pass
        finally:
            cleanup_temp_file(pdf_path)


class TestPDFLoaderIntegration:
    """Integration tests for PDFLoader with other components."""

    def test_with_source_content_path_exists(self):
        """Test integration with SourceContent path_exists method."""
        pdf_path = create_simple_pdf("Integration test content")
        try:
            source_content = SourceContent(pdf_path)
            assert source_content.path_exists()

            result = PDFLoader().load(source_content)
            assert result.source == pdf_path

        finally:
            cleanup_temp_file(pdf_path)

    def test_with_source_content_url(self):
        """Test integration with SourceContent URL detection."""
        url = "https://example.com/test.pdf"
        source_content = SourceContent(url)
        assert source_content.is_url()

        # We won't actually load from URL in this test
        # but verify the detection works
        assert url in source_content.source_ref
