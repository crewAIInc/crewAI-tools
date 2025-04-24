import os
from unittest import mock

import pytest
from crewai import Agent, LLM, Task, Crew, Process
from pytest import fixture

from crewai_tools.tools.rag.rag_tool import RagTool
from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter


@fixture(autouse=True)
def mock_env_vars():
    with mock.patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_key",
        "GOOGLE_API_KEY": "test_key",
        "EMBEDCHAIN_DB_URI": "sqlite:///test.db"
    }):
        yield


def test_rag_tool_run_method():
    """Test that the RagTool._run method works correctly without **kwargs."""
    mock_adapter = mock.MagicMock(spec=EmbedchainAdapter)
    mock_adapter.query.return_value = "Test content relevant to the query"
    
    rag_tool = RagTool()
    rag_tool.adapter = mock_adapter
    
    result = rag_tool._run(query="How to rerank?")
    assert "Relevant Content:" in result
    mock_adapter.query.assert_called_once_with("How to rerank?")
    
    result = rag_tool.run(query="How to rerank?")
    assert "Relevant Content:" in result
    assert mock_adapter.query.call_count == 2


def test_rag_tool_schema_generation():
    """Test that the RagTool's schema is correctly generated without **kwargs."""
    mock_adapter = mock.MagicMock(spec=EmbedchainAdapter)
    
    rag_tool = RagTool()
    rag_tool.adapter = mock_adapter
    
    assert hasattr(rag_tool, "args_schema")
    assert "query" in rag_tool.args_schema.model_fields
    
    assert len(rag_tool.args_schema.model_fields) == 1
    
    assert rag_tool.args_schema.model_fields["query"].annotation == str


def test_rag_tool_with_agent():
    """Test that an agent can successfully use the RagTool."""
    mock_adapter = mock.MagicMock(spec=EmbedchainAdapter)
    mock_adapter.query.return_value = "Test content relevant to the query"
    
    rag_tool = RagTool()
    rag_tool.adapter = mock_adapter
    
    with mock.patch("crewai.llm.LLM.call") as mock_llm_call:
        mock_llm_call.return_value = """I'll use the Knowledge base tool to find information.

<tool>Knowledge base</tool>
<tool_input>
{"query": "How to rerank?"}
</tool_input>

Based on the information I found from the knowledge base: Test content relevant to the query

Final answer: Test content relevant to the query
"""
        
        llm = LLM(
            model="gemini/gemini-2.5-flash-preview-04-17",
            temperature=0.1
        )
        
        knowledge_assistant = Agent(
            role="Knowledge Assistant",
            goal="Answer questions accurately using only the provided knowledge tools",
            backstory="I am a dedicated knowledge assistant who always consults reliable sources",
            llm=llm,
            tools=[rag_tool],
            verbose=True
        )
        
        answer_task = Task(
            description="Answer the following question: 'How to rerank?'",
            expected_output="A complete and accurate response based solely on RAG tool data",
            agent=knowledge_assistant
        )
        
        knowledge_crew = Crew(
            agents=[knowledge_assistant],
            tasks=[answer_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = knowledge_crew.kickoff()
        
        mock_adapter.query.assert_called_with("How to rerank?")
        
        assert "Test content relevant to the query" in result.raw
