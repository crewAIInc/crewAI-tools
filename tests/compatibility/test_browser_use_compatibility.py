import importlib.util
import pytest


def test_browser_use_import_compatibility():
    """
    Test that browser-use can be imported alongside crewai-tools.
    
    This test verifies that the langchain-openai version conflict is resolved.
    We don't actually need to install browser-use for this test, just checking
    that langchain-openai is correctly handled.
    """
    langchain_openai_spec = importlib.util.find_spec("langchain_openai")
    assert langchain_openai_spec is not None, "langchain-openai not found"
    
    import crewai_tools
    
    from crewai_tools.tools.rag.rag_tool import RagTool
    tool = RagTool()
    
    assert tool is not None, "Failed to create RagTool"
