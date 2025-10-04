from crewai_tools import BaseTool
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools.semanticscholar.tool import SemanticScholarQueryRun

class ScholarResearchTool(BaseTool):
    name: str = "ScholarResearchTool"
    description: str = "Tool to find and summarize important papers by a specific researcher on a given subject."

    def _run(self, researcher: str, research_subject: str) -> str:
        instructions = "You are an expert researcher."
        base_prompt = hub.pull("langchain-ai/openai-functions-template")
        prompt = base_prompt.partial(instructions=instructions)
        llm = ChatOpenAI(temperature=0)
        tools = [SemanticScholarQueryRun()]
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        response = agent_executor.invoke(
            {
                "input": f"What are the most important papers written by {researcher} on {research_subject}? "
                f"Show me a list of papers that {researcher} is an author on. Do not show me papers that {researcher} is not an author on. "
                f"Return the summaries of the most important papers written by {researcher} on {research_subject}. "
                f"Finally include a single paragraph in markdown format that summarizes the scholar's work in this field, along with html links to important papers found."
            }
        )
        return response['output']
    
class ScholarStatusTool(BaseTool):
    name: str = "ScholarStatusTool"
    description: str = "Tool to find the last time a specific researcher published on a given subject."

    def _run(self, researcher: str, research_subject: str) -> str:
        instructions = "You are an expert researcher."
        base_prompt = hub.pull("langchain-ai/openai-functions-template")
        prompt = base_prompt.partial(instructions=instructions)
        llm = ChatOpenAI(temperature=0)
        tools = [SemanticScholarQueryRun()]
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        response = agent_executor.invoke(
            {
                "input": f"When was the last time {researcher} published a paper on {research_subject}? "
                f"Return a single sentence that summarizes the scholar's most recent work in this field.  Include a link to the most recent paper."
            }
        )
        return response['output']