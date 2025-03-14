from crewai.project import CrewBase, agent

from crewai_tools.tools.cognee_memory_tool import (
    CogneeAddTool,
    CogneeCognifyTool,
    CogneeSearchTool,
)


# Then, inside your Crew or agent definition:
@CrewBase
class AnalyzingApartmentHoodCrew:
    """AnalyzingApartmentHoodCrew crew"""

    # new Cognee tools
    cognee_add_tool = CogneeAddTool()
    cognee_cognify_tool = CogneeCognifyTool()
    cognee_search_tool = CogneeSearchTool()

    @agent
    def manager_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["manager_agent"],
            tools=[
                self.cognee_add_tool,
                self.cognee_cognify_tool,
                self.cognee_search_tool,
            ],
            allow_delegation=True,
        )
