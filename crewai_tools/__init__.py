from .adapters.enterprise_adapter import EnterpriseActionTool
from .adapters.mcp_adapter import MCPServerAdapter
from .adapters.zapier_adapter import ZapierActionTool
from .aws import (
    BedrockInvokeAgentTool,
    BedrockKBRetrieverTool,
    S3ReaderTool,
    S3WriterTool,
)
from .tools import (
    AIMindTool,
    ApifyActorsTool,
    ArxivPaperTool,
    BraveSearchTool,
    BrightDataDatasetTool,
    BrightDataSearchTool,
    BrightDataWebUnlockerTool,
    BrowserbaseLoadTool,
    CodeDocsSearchTool,
    CodeInterpreterTool,
    ComposioTool,
    ContextualAICreateAgentTool,
    ContextualAIParseTool,
    ContextualAIQueryTool,
    ContextualAIRerankTool,
    CouchbaseFTSVectorSearchTool,
    CrewaiEnterpriseTools,
    CrewaiPlatformTools,
    CSVSearchTool,
    DallETool,
    DatabricksQueryTool,
    DirectoryReadTool,
    DirectorySearchTool,
    DOCXSearchTool,
    EXASearchTool,
    FileCompressorTool,
    FileReadTool,
    FileWriterTool,
    FirecrawlCrawlWebsiteTool,
    FirecrawlScrapeWebsiteTool,
    FirecrawlSearchTool,
    GenerateCrewaiAutomationTool,
    GithubSearchTool,
    HyperbrowserLoadTool,
    InvokeCrewAIAutomationTool,
    JSONSearchTool,
    LinkupSearchTool,
    LlamaIndexTool,
    MDXSearchTool,
    MongoDBVectorSearchConfig,
    MongoDBVectorSearchTool,
    MultiOnTool,
    MySQLSearchTool,
    NL2SQLTool,
    OCRTool,
    OxylabsAmazonProductScraperTool,
    OxylabsAmazonSearchScraperTool,
    OxylabsGoogleSearchScraperTool,
    OxylabsUniversalScraperTool,
    ParallelSearchTool,
    PatronusEvalTool,
    PatronusLocalEvaluatorTool,
    PatronusPredefinedCriteriaEvalTool,
    PDFSearchTool,
    PGSearchTool,
    QdrantVectorSearchTool,
    RagTool,
    ScrapeElementFromWebsiteTool,
    ScrapegraphScrapeTool,
    ScrapegraphScrapeToolSchema,
    ScrapeWebsiteTool,
    ScrapflyScrapeWebsiteTool,
    SeleniumScrapingTool,
    SerpApiGoogleSearchTool,
    SerpApiGoogleShoppingTool,
    SerperDevTool,
    SerperScrapeWebsiteTool,
    SerplyJobSearchTool,
    SerplyNewsSearchTool,
    SerplyScholarSearchTool,
    SerplyWebpageToMarkdownTool,
    SerplyWebSearchTool,
    SingleStoreSearchTool,
    SnowflakeConfig,
    SnowflakeSearchTool,
    SpiderTool,
    StagehandTool,
    TavilyExtractorTool,
    TavilySearchTool,
    TXTSearchTool,
    VisionTool,
    WeaviateVectorSearchTool,
    WebsiteSearchTool,
    XMLSearchTool,
    YoutubeChannelSearchTool,
    YoutubeVideoSearchTool,
    ZapierActionTools,
)


# Lazy import for BrowserUseTool with Python version check
def __getattr__(name):
    if name == "BrowserUseTool":
        from sys import version_info

        if version_info < (3, 11):
            raise RuntimeError(
                "BrowserUseTool requires Python >= 3.11. "
                "Please upgrade your Python version or avoid using BrowserUseTool."
            )
        from .tools.browser_use_tool.browser_use_tool import BrowserUseTool

        return BrowserUseTool
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
