from crewai import Agent, Crew, Task

from crewai_tools.tools.opengraphio_scrape_website_tool.opengraphio_scrape_website_tool import (
    OpenGraphScrapeWebsiteTool,
)


def test_opengraph_tool():
    # Create an instance of the OpenGraphTool
    opengraph_tool = OpenGraphScrapeWebsiteTool()

    # Create the agent with the OpenGraphTool
    scraper_agent = Agent(
        role="Web Scraping Specialist",
        goal="Extract Summarize Website Content",
        backstory="A skilled data miner proficient in scraping raw HTML content and extracting useful information.",
        tools=[opengraph_tool],
        verbose=True,
        cache=False,
    )

    # Define the tasks for the agent
    summarize_site = Task(
        description="Scrape the OpenGraph metadata of https://securecoders.com and return a summary of its content",
        expected_output="A 1-2 sentence summary of the site that would be useful for someone interested in the site.",
        agent=scraper_agent,
    )

    # Create a crew with the agent and tasks
    crew = Crew(agents=[scraper_agent], tasks=[summarize_site], verbose=True)

    # Kick off the crew to execute the tasks
    crew.kickoff()


if __name__ == "__main__":
    test_opengraph_tool()
