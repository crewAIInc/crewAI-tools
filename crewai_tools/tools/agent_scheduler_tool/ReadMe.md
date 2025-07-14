# agent-scheduler tool
## Description
This tool uses a Reinforcement Learning (RL) environment to help optimize how agents collaborate in CrewAI. It uses a custom RL environment built using OpenAI Gym where we simulate the agents working together. The goal is to improve task completion time and efficiency by adjusting how agents communicate and collaborate, based on the task at hand.

## Installation
Install the crewai_tools package
```shell
pip install 'crewai[tools]'
```

## Example
For example, when agents are given a task, they dynamically adjust how they interact based on previous performance, like avoiding overlapping efforts or optimizing resource allocation.

```python
from crewai_tools import AgentSchedulerTool
from crewai import LLM

Agent(
    ...
    tools=[AgentSchedulerTool()],
)
tool = AgentSchedulerTool(agent_ids=["agent_alpha", "agent_beta", "agent_gamma"])
llm = LLM(model="azure/gpt-4o", api_version="2023-05-15")

agent = Agent(
            name="Scheduler Agent",
            role="Agent Performance Monitor",
            goal="Optimize agent retraining schedules based on recent outcomes",
            backstory="This agent reviews logs and adjusts how frequently agents should be retrained.",
            tools=[tool],
            llm=llm
        )

task = Task(
            description="Use the agent_scheduler tool to analyze agent_alpha performance with 'True,False,True,True,False,False,True' and suggest a retraining interval.",
            expected_output="Suggest how often agent_alpha should be retrained",
            agent=agent
        )

crew = Crew(agents=[agent], tasks=[task], verbose=False)
```