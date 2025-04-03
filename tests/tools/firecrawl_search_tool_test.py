import pytest
from crewai_tools import FirecrawlSearchTool

def test_firecrawl_search_tool_initialization():
    tool = FirecrawlSearchTool()
    assert tool is not None
    assert hasattr(tool, '_firecrawl')

def test_no_query():
    with pytest.raises(ValueError):
        tool = FirecrawlSearchTool()
        tool.run()

# Free Plan API key is limited to 5 requests per minute
# def test_query_in_initialization():
#     tool = FirecrawlSearchTool(query='what is firecrawl?')
#     result = tool.run()
#     assert result is not None
#     assert result['success'] is True
#     assert result['data'] is not None


# def test_query_in_run():
#     tool = FirecrawlSearchTool()
#     result = tool.run(query='what is firecrawl?')
#     assert result is not None
#     assert result['success'] is True
#     assert result['data'] is not None

def test_query_in_initialization_with_limit():
    tool = FirecrawlSearchTool(query='what is firecrawl?', limit=1)
    result = tool.run()
    assert result is not None
    assert result['success'] is True
    assert len(result['data']) == 1

def test_query_in_run_with_limit():
    tool = FirecrawlSearchTool()
    result = tool.run(query='what is firecrawl?', limit=1)
    assert result is not None
    assert result['success'] is True
    assert len(result['data']) == 1
    
def test_query_in_initialization_with_scrape_options():
    tool = FirecrawlSearchTool(
        query='what is firecrawl?', 
        limit=1, 
        scrapeOptions={
            'formats': 
                ['markdown']
                }
        )
    result = tool.run()
    assert result is not None
    assert result['success'] is True
    assert result['data'] is not None
    assert result['data'][0]['markdown'] is not None

def test_query_in_run_with_scrape_options():
    tool = FirecrawlSearchTool()
    result = tool.run(
        query='what is firecrawl?', 
        limit=1, 
        scrapeOptions={
            'formats': 
                ['html']
                }
        )
    assert result is not None
    assert result['success'] is True
    assert result['data'] is not None
    assert result['data'][0]['html'] is not None

if __name__ == '__main__':
    tool = FirecrawlSearchTool()

    print(tool.run(query='what is firecrawl?', limit=1, scrapeOptions={'formats': ['markdown', 'html']}))
