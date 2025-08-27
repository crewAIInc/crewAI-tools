from typing import Optional
import os
from pathlib import Path

from crewai_tools.rag.base_loader import BaseLoader, LoaderResult
from crewai_tools.rag.source_content import SourceContent


class PDFLoader(BaseLoader):
    """
    A loader for PDF files that extracts text content using PyPDF2.
    Supports both local PDF files and PDF files from URLs.
    """

    def load(self, source_content: SourceContent, **kwargs) -> LoaderResult:
        """
        Load and extract text from a PDF file.

        Args:
            source_content: SourceContent object containing PDF path or URL
            **kwargs: Additional options:
                - pages: list of page numbers to extract (0-indexed), if None extracts all pages
                - password: str - Password for encrypted PDFs

        Returns:
            LoaderResult containing extracted text, source reference, and metadata
        """
        source_ref = source_content.source_ref

        if source_content.is_url():
            content = self._load_from_url(source_ref, kwargs)
        elif source_content.path_exists():
            content = self._load_from_file(source_ref, kwargs)
        else:
            raise FileNotFoundError(f"PDF file not found: {source_ref}")

        return self._create_result(content, source_ref, kwargs)

    def _load_from_url(self, url: str, kwargs: dict) -> str:
        """Load PDF from URL and extract text."""
        import requests
        import tempfile

        headers = kwargs.get("headers", {
            "Accept": "application/pdf",
            "User-Agent": "Mozilla/5.0 (compatible; crewai-tools PDFLoader)"
        })

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Save to temporary file and extract text
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()

                try:
                    content = self._extract_text_from_file(tmp_file.name, kwargs)
                finally:
                    # Clean up temporary file
                    os.unlink(tmp_file.name)

            return content

        except Exception as e:
            raise ValueError(f"Error fetching PDF from URL {url}: {str(e)}")

    def _load_from_file(self, path: str, kwargs: dict) -> str:
        """Load PDF from local file and extract text."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"PDF file not found: {path}")

        if not path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {path}")

        return self._extract_text_from_file(path, kwargs)

    def _extract_text_from_file(self, path: str, kwargs: dict) -> str:
        """Extract text from PDF file using PyPDF."""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf is required for PDF loading. Please install it with: pip install pypdf")

        try:
            # Get configuration options
            pages_to_extract = kwargs.get("pages", None)  # List of page numbers (0-indexed)
            password = kwargs.get("password", None)

            reader = PdfReader(path)

            # Handle encrypted PDFs
            if reader.is_encrypted:
                if password is None:
                    raise ValueError("PDF is encrypted but no password provided")
                if not reader.decrypt(password):
                    raise ValueError("Failed to decrypt PDF with provided password")

            text_content = []
            total_pages = len(reader.pages)

            # Determine which pages to extract
            if pages_to_extract is None:
                pages_to_process = range(total_pages)
            else:
                # Validate page numbers
                for page_num in pages_to_extract:
                    if page_num < 0 or page_num >= total_pages:
                        raise ValueError(f"Page number {page_num} is out of range. PDF has {total_pages} pages.")
                pages_to_process = pages_to_extract

            # Extract text from specified pages
            for page_num in pages_to_process:
                try:
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    # Continue processing other pages even if one fails
                    text_content.append(f"--- Page {page_num + 1} ---\n[Error extracting text: {str(e)}]")

            return "\n\n".join(text_content)

        except Exception as e:
            raise ValueError(f"Error extracting text from PDF {path}: {str(e)}")

    def _create_result(self, content: str, source_ref: str, kwargs: dict) -> LoaderResult:
        """Create LoaderResult with extracted content and metadata."""
        # Calculate basic statistics
        word_count = len(content.split()) if content else 0
        char_count = len(content) if content else 0

        metadata = {
            "source_type": "pdf",
            "word_count": word_count,
            "character_count": char_count,
        }

        # Add file-specific metadata if it's a local file
        if not source_ref.startswith(('http://', 'https://')):
            if os.path.exists(source_ref):
                file_path = Path(source_ref)
                metadata.update({
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "file_extension": file_path.suffix,
                })

        # Add extraction options to metadata
        if "pages" in kwargs:
            metadata["extracted_pages"] = kwargs["pages"]
        if "password" in kwargs:
            metadata["was_encrypted"] = True

        doc_id = self.generate_doc_id(source_ref, content)

        return LoaderResult(
            content=content,
            source=source_ref,
            metadata=metadata,
            doc_id=doc_id
        )
