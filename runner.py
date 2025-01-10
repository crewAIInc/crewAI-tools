import os
from crewai import Agent, Task, Crew

# from crewai_tools.tools.weaviate_tool.vector_search import WeaviateVectorSearchTool
from crewai_tools.tools.firecrawl_search_tool.firecrawl_search_tool import (
    FirecrawlSearchTool,
)

# from crewai_tools.tools.firecrawl_scrape_website_tool.firecrawl_scrape_website_tool import (
#     FirecrawlScrapeWebsiteTool,
# )
# from crewai_tools.tools.firecrawl_crawl_website_tool.firecrawl_crawl_website_tool import (
#     FirecrawlCrawlWebsiteTool,
# )
from crewai_tools.tools.weaviate_tool.vector_search import WeaviateVectorSearchTool
from crewai_tools.tools.selenium_scraping_tool.selenium_scraping_tool import (
    SeleniumScrapingTool,
)
from crewai_tools.tools.serper_dev_tool.serper_dev_tool import SerperDevTool
from crewai_tools.tools.spider_tool.spider_tool import SpiderTool
from crewai_tools.tools.scrapegraph_scrape_tool.scrapegraph_scrape_tool import (
    ScrapegraphScrapeTool,
)
from crewai_tools.tools.linkup.linkup_search_tool import LinkupSearchTool


def main():
    # tool = WeaviateVectorSearchTool(collection_name="financial_docs", limit=3)
    # browser_tool = FirecrawlCrawlWebsiteTool(api_key=os.getenv("FIRECRAWL_API_KEY"))
    # browser_tool = FirecrawlSearchTool(api_key=os.getenv("FIRECRAWL_API_KEY"))
    # vector_tool = WeaviateVectorSearchTool(
    #     weaviate_cluster_url=os.getenv("WEAVIATE_URL"),
    #     weaviate_api_key=os.getenv("WEAVIATE_API_KEY"),
    # )
    serper_tool = SerperDevTool()
    spider_tool = SpiderTool(api_key=os.getenv("SPIDER_API_KEY"))
    # selenium_tool = SeleniumScrapingTool()
    scrapegraph_tool = ScrapegraphScrapeTool(
        website_url="https://docs.crewai.com/concepts/knowledge",
        api_key=os.getenv("SCRAPEGRAPH_API_KEY"),
    )
    linkup_tool = LinkupSearchTool(api_key=os.getenv("LINKUP_API_KEY"))
    agent = Agent(
        name="browser_agent",
        role="You are a helpful assistant that can use the browser to search for information. You can use this as the url: https://docs.crewai.com/concepts/knowledge. Don't include any crawler_options",
        goal="Use the browser to search for the given query: {query}",
        backstory="You have access to the BrowserUseTool to answer questions about the given query.",
        llm="gpt-4o",
        # tools=[serper_tool, scrapegraph_tool],
        tools=[linkup_tool],
    )
    task = Task(
        # name="weaviate_task",
        description="You are a helpful assistant that can answer questions about the given query. This is the query: {query}",
        expected_output="Use the browser to search for the given query. There is a url: https://docs.crewai.com/concepts/knowledge",
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
    )
    result = crew.kickoff(
        inputs={"query": "How does knowledge work in crewai."},
    )
    print("result", result)


if __name__ == "__main__":
    main()
