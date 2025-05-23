import os
from crewai import Agent, Task, Crew, LLM
from crewai.process import Process
import os
import re
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArxivToolInput(BaseModel):
    search_query: str = Field(..., description="Search query for Arxiv, e.g., 'transformer neural network'")
    max_results: int = Field(5, description="Maximum number of results to fetch from Arxiv")
    download_pdfs: Optional[bool] = Field(False, description="If True, download PDFs to local folder")
    save_dir: Optional[str] = Field("./arxiv_pdfs", description="Directory path to save downloaded PDFs")
    use_title_as_filename: Optional[bool] = Field(False, description="Use paper title as PDF filename instead of arXiv ID")


class ArxivPaperTool(BaseTool):
    name: str = "Arxiv Paper Fetcher and Downloader"
    description: str = "Fetches metadata from Arxiv based on a search query and optionally downloads PDFs."
    args_schema: Type[BaseModel] = ArxivToolInput

    def _run(self, **kwargs) -> str:
        try:
            # Unpack arguments from kwargs
            args = ArxivToolInput(**kwargs)
            
            logger.info(f"Running Arxiv tool: query='{args.search_query}', max_results={args.max_results}, "
                        f"download_pdfs={args.download_pdfs}, save_dir='{args.save_dir}', "
                        f"use_title_as_filename={args.use_title_as_filename}")

            papers = self.fetch_arxiv_data(args.search_query, args.max_results)

            if args.download_pdfs:
                os.makedirs(args.save_dir, exist_ok=True)
                for paper in papers:
                    if paper['pdf_url']:
                        if args.use_title_as_filename:
                            safe_title = re.sub(r'[\\/*?:"<>|]', "_", paper['title']).strip()
                            filename_base = safe_title or paper['arxiv_id']
                        else:
                            filename_base = paper['arxiv_id']
                        filename = f"{filename_base[:500]}.pdf"
                        save_path = os.path.join(args.save_dir, filename)
                        self.download_pdf(paper['pdf_url'], save_path)
                        time.sleep(1)  # Be polite to ArXiv

            results = []
            for p in papers:
                authors_str = ', '.join(p['authors'])
                summary_snippet = (p['summary'][:300] + "...") if len(p['summary']) > 300 else p['summary']
                results.append(
                    f"Title: {p['title']}\nAuthors: {authors_str}\nPublished: {p['published_date']}\nPDF: {p['pdf_url'] or 'N/A'}\n Summary: {summary_snippet}"
                )

            return "\n\n" + "-"*80 + "\n\n".join(results)

        except Exception as e:
            logger.error(f"ArxivTool Error: {str(e)}")
            return f"Failed to fetch or download Arxiv papers: {str(e)}"


    def fetch_arxiv_data(self, search_query: str, max_results: int) -> List[dict]:
        api_url = f"http://export.arxiv.org/api/query?search_query={urllib.parse.quote(search_query)}&start=0&max_results={max_results}"
        logger.info(f"Fetching data from Arxiv API: {api_url}")
        data = urllib.request.urlopen(api_url).read().decode('utf-8')
        root = ET.fromstring(data)
        papers = []

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            raw_id = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
            arxiv_id = raw_id.split('/')[-1].replace('.', '_')

            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            authors = [
                author.find('{http://www.w3.org/2005/Atom}name').text
                for author in entry.findall('{http://www.w3.org/2005/Atom}author')
            ]

            pdf_url = None
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.attrib.get('title') == 'pdf':
                    pdf_url = link.attrib.get('href')
                    break
            if not pdf_url:
                for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                    href = link.attrib.get('href')
                    if href and 'pdf' in href:
                        pdf_url = href
                        break

            papers.append({
                "arxiv_id": arxiv_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "published_date": published,
                "pdf_url": pdf_url
            })

        return papers

    def download_pdf(self, pdf_url: str, save_path: str):
        try:
            logger.info(f"Downloading PDF from {pdf_url} to {save_path}")
            urllib.request.urlretrieve(pdf_url, save_path)
            logger.info(f"PDF saved: {save_path}")
        except Exception as e:
            logger.error(f"Failed to download PDF from {pdf_url}: {e}")
            raise


