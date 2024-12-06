from crewai import Agent, Crew, Task

from crewai_tools.tools.opengraphio_get_opengraph_tags_tool.opengraphio_get_opengraph_tags_tool import (
    GetOpengraphTagsTool,
)


def test_opengraph_tool():
    # Create an instance of the OpenGraphTool
    opengraph_tags_tool = GetOpengraphTagsTool()

    # Create the agent with the OpenGraphTool
    opengraph_specialist = Agent(
        role="Open Graph Metadata Specialist",
        goal="Suggest most relevant Open Graph metadata tags for a website",
        backstory="A skilled SEO / SEM consultant with 20 years of experience.",
        tools=[opengraph_tags_tool],
        verbose=True,
        cache=False,
    )

    # Define the tasks for the agent
    suggest_opengraph_tags = Task(
        description="Review the OpenGraph metadata and the tags suggested from the Opengraph.io API for "
        "https://www.wunderground.com/ and suggest the most relevant Open Graph metadata tags.  "
        "The Opengraph.io API will return the following important properties:"
        "- hybridGraph - The tags that the Opengraph.io API suggests for the page"
        "- openGraph - The tags that are currently on the page",
        expected_output="Provide the tags that are currently on the page ('openGraph' property) and suggest HTML to be "
        "inserted into the <HEAD> tag to provide more effective tags for sharing on social websites. "
        "The response should look like this:"
        "## Current Tags"
        "You're assessment of the current tags"
        "## Suggested Tags"
        "You're suggested HTML content to add to the <HEAD> tag"
        "### Explanation"
        "Explain why you suggest these tags",
        agent=opengraph_specialist,
    )

    # Create a crew with the agent and tasks
    crew = Crew(
        agents=[opengraph_specialist], tasks=[suggest_opengraph_tags], verbose=True
    )

    # Kick off the crew to execute the tasks
    crew.kickoff()


if __name__ == "__main__":
    test_opengraph_tool()
