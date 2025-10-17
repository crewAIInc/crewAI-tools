import pytest
from crewai_tools.tools.firecrawl_extract_tool.firecrawl_extract_tool import FirecrawlExtractTool

class DummyFirecrawlApp:
    def extract(self, **options):
        return {"status": "success", "options": options}

@pytest.fixture(autouse=True)
def patch_firecrawl(monkeypatch):
    # Patch FirecrawlApp in the tool to use DummyFirecrawlApp
    import crewai_tools.tools.firecrawl_extract_tool.firecrawl_extract_tool as mod
    monkeypatch.setattr(mod, "FirecrawlApp", DummyFirecrawlApp)
    yield

def test_firecrawl_extract_tool_init():
    tool = FirecrawlExtractTool(api_key="dummy", config={"prompt": "test"})
    assert tool.api_key == "dummy"
    assert tool.config["prompt"] == "test"

def test_firecrawl_extract_tool_run():
    tool = FirecrawlExtractTool(api_key="dummy", config={"prompt": "test"})
    # Patch the _firecrawl attribute directly for safety
    tool._firecrawl = DummyFirecrawlApp()
    urls = ["https://example.com/page1", "https://example.com/page2"]
    result = tool._run(urls)
    assert result["status"] == "success"
    assert result["options"]["urls"] == urls
    assert result["options"]["prompt"] == "test" 