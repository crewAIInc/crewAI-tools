from .ai_mind_tool.ai_mind_tool import AIMindTool
from .apify_actors_tool.apify_actors_tool import ApifyActorsTool
from .brave_search_tool.brave_search_tool import BraveSearchTool
from .browserbase_load_tool.browserbase_load_tool import BrowserbaseLoadTool

try:
    from .code_docs_search_tool.code_docs_search_tool import CodeDocsSearchTool
except ImportError:
    class CodeDocsSearchTool:
        """Placeholder for CodeDocsSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for CodeDocsSearchTool to function. Please install it with 'pip install embedchain'")
from .code_interpreter_tool.code_interpreter_tool import CodeInterpreterTool
from .composio_tool.composio_tool import ComposioTool

try:
    from .csv_search_tool.csv_search_tool import CSVSearchTool
except ImportError:
    class CSVSearchTool:
        """Placeholder for CSVSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for CSVSearchTool to function. Please install it with 'pip install embedchain'")
from .dalle_tool.dalle_tool import DallETool
from .databricks_query_tool.databricks_query_tool import DatabricksQueryTool
from .directory_read_tool.directory_read_tool import DirectoryReadTool

try:
    from .directory_search_tool.directory_search_tool import DirectorySearchTool
except ImportError:
    class DirectorySearchTool:
        """Placeholder for DirectorySearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for DirectorySearchTool to function. Please install it with 'pip install embedchain'")

try:
    from .docx_search_tool.docx_search_tool import DOCXSearchTool
except ImportError:
    class DOCXSearchTool:
        """Placeholder for DOCXSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for DOCXSearchTool to function. Please install it with 'pip install embedchain'")
from .exa_tools.exa_search_tool import EXASearchTool
from .file_read_tool.file_read_tool import FileReadTool
from .file_writer_tool.file_writer_tool import FileWriterTool
from .firecrawl_crawl_website_tool.firecrawl_crawl_website_tool import (
    FirecrawlCrawlWebsiteTool,
)
from .firecrawl_scrape_website_tool.firecrawl_scrape_website_tool import (
    FirecrawlScrapeWebsiteTool,
)
from .firecrawl_search_tool.firecrawl_search_tool import FirecrawlSearchTool

try:
    from .github_search_tool.github_search_tool import GithubSearchTool
except ImportError:
    class GithubSearchTool:
        """Placeholder for GithubSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for GithubSearchTool to function. Please install it with 'pip install embedchain'")

from .hyperbrowser_load_tool.hyperbrowser_load_tool import HyperbrowserLoadTool

try:
    from .json_search_tool.json_search_tool import JSONSearchTool
except ImportError:
    class JSONSearchTool:
        """Placeholder for JSONSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for JSONSearchTool to function. Please install it with 'pip install embedchain'")

from .linkup.linkup_search_tool import LinkupSearchTool
from .llamaindex_tool.llamaindex_tool import LlamaIndexTool

try:
    from .mdx_search_tool.mdx_search_tool import MDXSearchTool
except ImportError:
    class MDXSearchTool:
        """Placeholder for MDXSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for MDXSearchTool to function. Please install it with 'pip install embedchain'")
from .multion_tool.multion_tool import MultiOnTool

try:
    from .mysql_search_tool.mysql_search_tool import MySQLSearchTool
except ImportError:
    class MySQLSearchTool:
        """Placeholder for MySQLSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for MySQLSearchTool to function. Please install it with 'pip install embedchain'")

try:
    from .nl2sql.nl2sql_tool import NL2SQLTool
except ImportError:
    class NL2SQLTool:
        """Placeholder for NL2SQLTool when sqlalchemy is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("SQLAlchemy is required for NL2SQLTool to function. Please install it with 'pip install sqlalchemy'")
from .patronus_eval_tool import (
    PatronusEvalTool,
    PatronusLocalEvaluatorTool,
    PatronusPredefinedCriteriaEvalTool,
)
try:
    from .pdf_search_tool.pdf_search_tool import PDFSearchTool
except ImportError:
    class PDFSearchTool:
        """Placeholder for PDFSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for PDFSearchTool to function. Please install it with 'pip install embedchain'")
try:
    from .pg_search_tool.pg_search_tool import PGSearchTool
except ImportError:
    class PGSearchTool:
        """Placeholder for PGSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for PGSearchTool to function. Please install it with 'pip install embedchain'")
from .qdrant_vector_search_tool.qdrant_search_tool import QdrantVectorSearchTool
from .rag.rag_tool import RagTool
try:
    from .scrape_element_from_website.scrape_element_from_website import (
        ScrapeElementFromWebsiteTool,
    )
except ImportError:
    class ScrapeElementFromWebsiteTool:
        """Placeholder for ScrapeElementFromWebsiteTool when bs4 is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("BeautifulSoup is required for ScrapeElementFromWebsiteTool to function. Please install it with 'pip install beautifulsoup4'")
try:
    from .scrape_website_tool.scrape_website_tool import ScrapeWebsiteTool
except ImportError:
    class ScrapeWebsiteTool:
        """Placeholder for ScrapeWebsiteTool when bs4 is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("BeautifulSoup is required for ScrapeWebsiteTool to function. Please install it with 'pip install beautifulsoup4'")
from .scrapegraph_scrape_tool.scrapegraph_scrape_tool import (
    ScrapegraphScrapeTool,
    ScrapegraphScrapeToolSchema,
)
from .scrapfly_scrape_website_tool.scrapfly_scrape_website_tool import (
    ScrapflyScrapeWebsiteTool,
)
from .selenium_scraping_tool.selenium_scraping_tool import SeleniumScrapingTool
from .serpapi_tool.serpapi_google_search_tool import SerpApiGoogleSearchTool
from .serpapi_tool.serpapi_google_shopping_tool import SerpApiGoogleShoppingTool
from .serper_dev_tool.serper_dev_tool import SerperDevTool
from .serply_api_tool.serply_job_search_tool import SerplyJobSearchTool
from .serply_api_tool.serply_news_search_tool import SerplyNewsSearchTool
from .serply_api_tool.serply_scholar_search_tool import SerplyScholarSearchTool
from .serply_api_tool.serply_web_search_tool import SerplyWebSearchTool
from .serply_api_tool.serply_webpage_to_markdown_tool import SerplyWebpageToMarkdownTool
from .snowflake_search_tool import (
    SnowflakeConfig,
    SnowflakeSearchTool,
    SnowflakeSearchToolInput,
)
from .spider_tool.spider_tool import SpiderTool
try:
    from .txt_search_tool.txt_search_tool import TXTSearchTool
except ImportError:
    class TXTSearchTool:
        """Placeholder for TXTSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for TXTSearchTool to function. Please install it with 'pip install embedchain'")
from .vision_tool.vision_tool import VisionTool
from .weaviate_tool.vector_search import WeaviateVectorSearchTool
try:
    from .website_search.website_search_tool import WebsiteSearchTool
except ImportError:
    class WebsiteSearchTool:
        """Placeholder for WebsiteSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for WebsiteSearchTool to function. Please install it with 'pip install embedchain'")
try:
    from .xml_search_tool.xml_search_tool import XMLSearchTool
except ImportError:
    class XMLSearchTool:
        """Placeholder for XMLSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for XMLSearchTool to function. Please install it with 'pip install embedchain'")
try:
    from .youtube_channel_search_tool.youtube_channel_search_tool import (
        YoutubeChannelSearchTool,
    )
except ImportError:
    class YoutubeChannelSearchTool:
        """Placeholder for YoutubeChannelSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for YoutubeChannelSearchTool to function. Please install it with 'pip install embedchain'")
try:
    from .youtube_video_search_tool.youtube_video_search_tool import YoutubeVideoSearchTool
except ImportError:
    class YoutubeVideoSearchTool:
        """Placeholder for YoutubeVideoSearchTool when embedchain is not available."""
        def __init__(self, *args, **kwargs):
            raise ImportError("Embedchain is required for YoutubeVideoSearchTool to function. Please install it with 'pip install embedchain'")
