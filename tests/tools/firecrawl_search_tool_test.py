from crewai_tools import FirecrawlSearchTool

def test_firecrawl_search_tool():
    tool = FirecrawlSearchTool()
    result = tool.run(query='what is firecrawl?')
    assert result is not None
    

if __name__ == '__main__':
    tool = FirecrawlSearchTool()

    print(tool.run(query='what is firecrawl?'))
