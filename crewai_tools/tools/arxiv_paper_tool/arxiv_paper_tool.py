import os
import re
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import ClassVar
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivToolInput(BaseModel):
    search_query: str = Field(..., description="Search query for Arxiv, e.g., 'transformer neural network'")
    max_results: int = Field(5, ge=1, le=100, description="Max results to fetch; must be between 1 and 100")
    download_pdfs: Optional[bool] = Field(False, description="If True, download PDFs to local folder")
    save_dir: Optional[str] = Field("./arxiv_pdfs", description="Directory path to save downloaded PDFs")
    use_title_as_filename: Optional[bool] = Field(False, description="Use paper title as PDF filename instead of arXiv ID")

class ArxivPaperTool(BaseTool):
    BASE_API_URL: ClassVar[str] = "http://export.arxiv.org/api/query"
    SLEEP_DURATION: ClassVar[int] = 1
    SUMMARY_TRUNCATE_LENGTH: ClassVar[int] = 300
    ATOM_NAMESPACE: ClassVar[str] = "{http://www.w3.org/2005/Atom}"
    name: str = "Arxiv Paper Fetcher and Downloader"
    description: str = "Fetches metadata from Arxiv based on a search query and optionally downloads PDFs."
    args_schema: Type[BaseModel] = ArxivToolInput

    def _run(self, **kwargs) -> str:
        try:
            args = ArxivToolInput(**kwargs)
            logger.info(f"Running Arxiv tool: query='{args.search_query}', max_results={args.max_results}, "
                        f"download_pdfs={args.download_pdfs}, save_dir='{args.save_dir}', "
                        f"use_title_as_filename={args.use_title_as_filename}")

            papers = self.fetch_arxiv_data(args.search_query, args.max_results)

            if args.download_pdfs:
                save_dir = self._validate_save_path(args.save_dir)
                for paper in papers:
                    if paper['pdf_url']:
                        if args.use_title_as_filename:
                            safe_title = re.sub(r'[\\/*?:"<>|]', "_", paper['title']).strip()
                            filename_base = safe_title or paper['arxiv_id']
                        else:
                            filename_base = paper['arxiv_id']
                        filename = f"{filename_base[:500]}.pdf"
                        save_path = os.path.join(save_dir, filename)
                        self.download_pdf(paper['pdf_url'], save_path)
                        time.sleep(self.SLEEP_DURATION)

            results = [self._format_paper_result(p) for p in papers]
            return "\n\n" + "-" * 80 + "\n\n".join(results)

        except Exception as e:
            logger.error(f"ArxivTool Error: {str(e)}")
            return f"Failed to fetch or download Arxiv papers: {str(e)}"

    def fetch_arxiv_data(self, search_query: str, max_results: int) -> List[dict]:
        api_url = f"{self.BASE_API_URL}?search_query={urllib.parse.quote(search_query)}&start=0&max_results={max_results}"
        logger.info(f"Fetching data from Arxiv API: {api_url}")
        data = urllib.request.urlopen(api_url).read().decode('utf-8')
        root = ET.fromstring(data)
        papers = []

        for entry in root.findall(self.ATOM_NAMESPACE + "entry"):
            raw_id = self._get_element_text(entry, "id")
            arxiv_id = raw_id.split('/')[-1].replace('.', '_') if raw_id else "unknown"

            title = self._get_element_text(entry, "title") or "No Title"
            summary = self._get_element_text(entry, "summary") or "No Summary"
            published = self._get_element_text(entry, "published") or "No Publish Date"
            authors = [
                self._get_element_text(author, "name") or "Unknown"
                for author in entry.findall(self.ATOM_NAMESPACE + "author")
            ]

            pdf_url = self._extract_pdf_url(entry)

            papers.append({
                "arxiv_id": arxiv_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "published_date": published,
                "pdf_url": pdf_url
            })

        return papers

    @staticmethod
    def _get_element_text(entry: ET.Element, element_name: str) -> Optional[str]:
        elem = entry.find(f'{ArxivPaperTool.ATOM_NAMESPACE}{element_name}')

        return elem.text.strip() if elem is not None and elem.text else None

    def _extract_pdf_url(self, entry: ET.Element) -> Optional[str]:
        for link in entry.findall(self.ATOM_NAMESPACE + "link"):
            if link.attrib.get('title', '').lower() == 'pdf':
                return link.attrib.get('href')
        for link in entry.findall(self.ATOM_NAMESPACE + "link"):
            href = link.attrib.get('href')
            if href and 'pdf' in href:
                return href
        return None

    def _format_paper_result(self, paper: dict) -> str:
        summary = (paper['summary'][:self.SUMMARY_TRUNCATE_LENGTH] + '...') \
            if len(paper['summary']) > self.SUMMARY_TRUNCATE_LENGTH else paper['summary']
        authors_str = ', '.join(paper['authors'])
        return (f"Title: {paper['title']}\n"
                f"Authors: {authors_str}\n"
                f"Published: {paper['published_date']}\n"
                f"PDF: {paper['pdf_url'] or 'N/A'}\n"
                f"Summary: {summary}")

    @staticmethod
    def _validate_save_path(path: str) -> str:
        abs_path = os.path.abspath(path)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    def download_pdf(self, pdf_url: str, save_path: str):
        try:
            logger.info(f"Downloading PDF from {pdf_url} to {save_path}")
            urllib.request.urlretrieve(pdf_url, save_path)
            logger.info(f"PDF saved: {save_path}")
        except urllib.error.URLError as e:
            logger.error(f"Network error occurred while downloading {pdf_url}: {e}")
            raise
        except OSError as e:
            logger.error(f"File save error for {save_path}: {e}")
            raise
