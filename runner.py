from crewai import Agent, Task, Crew
from crewai_tools import PDFSearchTool

pdf_search_tool = PDFSearchTool(
    pdf="2305.14283.pdf",
)


agent = Agent(
    role="pdf extractor",
    goal="extract the pdf",
    backstory="you are a pdf extractor",
    tools=[pdf_search_tool],
)


task = Task(
    description="extract the pdf",
    expected_output="summary of the pdf",
    agent=agent,
)


crew = Crew(agents=[agent], tasks=[task], verbose=True)
result = crew.kickoff()
print(result)
