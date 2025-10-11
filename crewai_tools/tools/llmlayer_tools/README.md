# LLMLayer Tools

Five production-ready tools that give CrewAI agents real-time web search, content extraction, and AI-powered answers using 20+ language models.

## Features

- **AI-Powered Search** - Combine web search with LLM responses (citations, sources, images)
- **Multi-Type Search** - General, news, shopping, videos, images, scholarly content
- **Content Extraction** - Scrape any webpage as markdown, HTML, PDF, or screenshot
- **PDF Processing** - Extract text from PDF documents
- **YouTube Transcripts** - Get video transcripts in multiple languages
- **Zero New Dependencies** - Uses standard `requests` library

## Installation

```bash
pip install 'crewai[tools]'
```

Get your free API key at [llmlayer.dev](https://llmlayer.ai)

## Quick Start

```python
import os
from crewai import Agent, Task, Crew
from crewai_tools import LLMLayerSearchTool

os.environ["LLMLAYER_API_KEY"] = "your_api_key_here"

# Create agent with search capability
researcher = Agent(
    role='Research Analyst',
    goal='Find and analyze current information',
    tools=[LLMLayerSearchTool()],
    verbose=True
)

# Define task
task = Task(
    description='What are the latest developments in quantum computing? Use model: openai/gpt-4o-mini',
    agent=researcher,
    expected_output='Summary with sources'
)

# Run
crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
print(result)
```

## Available Tools

| Tool | Use Case | Key Parameters |
|------|----------|----------------|
| **LLMLayerSearchTool** | AI answers with web search | `query`, `model`, `citations`, `return_sources` |
| **LLMLayerWebSearchTool** | Raw search results | `query`, `search_type` (general/news/videos/images/scholar) |
| **LLMLayerScraperTool** | Extract webpage content | `url`, `format` (markdown/html/pdf/screenshot) |
| **LLMLayerPDFTool** | Extract text from PDFs | `url` |
| **LLMLayerYouTubeTool** | Get video transcripts | `url`, `language` |

## Usage Examples

### Research Agent with Citations

```python
from crewai import Agent, Task, Crew
from crewai_tools import LLMLayerSearchTool

researcher = Agent(
    role='Research Analyst',
    tools=[LLMLayerSearchTool()],
    verbose=True
)

task = Task(
    description='''
    Research climate change policies from 2024-2025.
    Model: anthropic/claude-sonnet-4
    Enable citations and sources.
    Filter: date_filter=month
    ''',
    agent=researcher,
    expected_output='Report with citations'
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

### Multi-Source Intelligence Agent

```python
from crewai_tools import (
    LLMLayerSearchTool,
    LLMLayerScraperTool,
    LLMLayerPDFTool
)

analyst = Agent(
    role='Intelligence Analyst',
    tools=[
        LLMLayerSearchTool(),
        LLMLayerScraperTool(),
        LLMLayerPDFTool()
    ],
    verbose=True
)

task = Task(
    description='''
    Analyze the company at https://example.com
    1. Search for recent news (model: openai/gpt-4o-mini)
    2. Scrape their website for key info
    3. Extract data from their whitepaper PDF
    ''',
    agent=analyst,
    expected_output='Comprehensive analysis'
)
```

### Domain-Filtered Search

```python
task = Task(
    description='''
    Find Python best practices.
    Model: openai/gpt-4o-mini
    Only search: stackoverflow.com, python.org
    Exclude: reddit.com
    Use domain_filter: ["stackoverflow.com", "python.org", "-reddit.com"]
    ''',
    agent=researcher,
    expected_output='Best practices summary'
)
```

### Structured JSON Output

```python
task = Task(
    description='''
    Summarize AI safety research.
    Model: openai/gpt-4o-mini
    Return as JSON with: summary, key_points (array), confidence (number)
    Use answer_type: json
    ''',
    agent=researcher,
    expected_output='JSON structured response'
)
```

### News Monitoring

```python
from crewai_tools import LLMLayerWebSearchTool

monitor = Agent(
    role='News Monitor',
    tools=[LLMLayerWebSearchTool()],
    verbose=True
)

task = Task(
    description='''
    Find AI regulation news from the past week.
    search_type: news
    recency: week
    ''',
    agent=monitor,
    expected_output='News summary'
)
```

### Web Scraping for Content Analysis

```python
from crewai_tools import LLMLayerScraperTool

content_analyst = Agent(
    role='Content Analyst',
    tools=[LLMLayerScraperTool()],
    verbose=True
)

task = Task(
    description='''
    Scrape https://example.com/blog/latest-article
    Extract as markdown format
    Include all images and links
    Analyze the key points
    ''',
    agent=content_analyst,
    expected_output='Article analysis with key points'
)
```

### Scrape Website as Screenshot

```python
task = Task(
    description='''
    Capture screenshot of https://competitor-site.com
    Format: screenshot
    Analyze the UI/UX design elements
    ''',
    agent=content_analyst,
    expected_output='Screenshot analysis'
)
```

### Extract and Analyze PDF Documents

```python
from crewai_tools import LLMLayerPDFTool

document_analyst = Agent(
    role='Document Analyst',
    tools=[LLMLayerPDFTool()],
    verbose=True
)

task = Task(
    description='''
    Extract text from https://example.com/whitepaper.pdf
    Summarize key findings
    Identify main conclusions
    ''',
    agent=document_analyst,
    expected_output='PDF summary with key findings'
)
```

### Analyze YouTube Videos

```python
from crewai_tools import LLMLayerYouTubeTool

video_analyst = Agent(
    role='Video Content Analyst',
    tools=[LLMLayerYouTubeTool()],
    verbose=True
)

task = Task(
    description='''
    Get transcript from https://youtube.com/watch?v=VIDEO_ID
    Language: en
    Summarize main topics discussed
    Extract key quotes
    ''',
    agent=video_analyst,
    expected_output='Video content summary'
)
```

### Multi-Language YouTube Analysis

```python
task = Task(
    description='''
    Extract Spanish transcript from https://youtube.com/watch?v=VIDEO_ID
    Language: es
    Translate key points to English
    ''',
    agent=video_analyst,
    expected_output='Translated summary'
)
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LLMLAYER_API_KEY` | Your LLMLayer API key | Yes |

### Supported Models

**OpenAI:** `openai/gpt-4o-mini`, `openai/gpt-4o`, `openai/gpt-4.1`  
**Anthropic:** `anthropic/claude-sonnet-4`,  
**Groq:** `groq/llama-3.3-70b-versatile`,

[See full model list →](https://docs.llmlayer.ai/answer)

### Tool Parameters

**LLMLayerSearchTool**
- **Required:** `query`, `model`
- **Optional:** `location` (country code), `citations` (bool), `return_sources` (bool), `return_images` (bool), `date_filter` (hour/day/week/month/year/anytime), `domain_filter` (list), `max_tokens` (int), `temperature` (float), `answer_type` (markdown/html/json), `json_schema` (str/dict)

**LLMLayerWebSearchTool**
- **Required:** `query`
- **Optional:** `search_type` (general/news/shopping/videos/images/scholar), `location`, `recency` (hour/day/week/month/year), `domain_filter` (list)

**LLMLayerScraperTool**
- **Required:** `url`
- **Optional:** `format` (markdown/html/screenshot/pdf), `include_images` (bool), `include_links` (bool)
- **Returns:** Extracted content in specified format. For screenshot/pdf, returns base64-encoded data with length indicator.

**LLMLayerPDFTool**
- **Required:** `url` (direct PDF link)
- **Returns:** Full text content with page count and metadata

**LLMLayerYouTubeTool**
- **Required:** `url` (YouTube video URL)
- **Optional:** `language` (e.g., 'en', 'es', 'fr')
- **Returns:** Full transcript with detected/specified language

## How Agents Use Tools

Agents automatically call tools based on task descriptions. You guide tool usage through natural language:

```python
# Agent will automatically:
# 1. Parse the task description
# 2. Identify required tool parameters
# 3. Call the appropriate tool
# 4. Process the results

task = Task(
    description='''
    Search for "AI breakthroughs 2025"
    Model: openai/gpt-4o-mini
    Return sources and citations
    Filter to last month only
    ''',
    agent=researcher
)
```

The agent extracts:
- `query`: "AI breakthroughs 2025"
- `model`: "openai/gpt-4o-mini"
- `return_sources`: True
- `citations`: True
- `date_filter`: "month"

## Tool Details

### LLMLayerSearchTool

**Purpose:** Combines web search with LLM processing to generate AI-powered answers with optional citations and sources.

**When to use:**
- Need AI-analyzed answers instead of raw search results
- Want citations and source attribution
- Require structured JSON responses
- Need domain-specific filtered results

**Example outputs:**
- Markdown text with inline citations: `[1]`
- HTML formatted responses
- Structured JSON matching your schema
- Images from search results (when `return_images=True`)

**Task description format:**
```python
description = '''
Query: your search question
Model: model_name
Citations: true/false
Return sources: true/false
Date filter: hour/day/week/month/year
Domain filter: ["domain1.com", "-exclude.com"]
'''
```

### LLMLayerWebSearchTool

**Purpose:** Raw web search across multiple content types without AI processing.

**When to use:**
- Need unprocessed search results
- Want to search specific content types (news, videos, images, scholarly articles)
- Prefer raw data for your own analysis
- Need shopping or video results

**Search types available:**
- `general` - Standard web search
- `news` - Recent news articles
- `shopping` - Product listings and prices
- `videos` - Video content
- `images` - Image search results
- `scholar` - Academic papers and citations

**Example outputs:**
- List of results with titles, URLs, and snippets
- No AI interpretation, just raw search data

**Task description format:**
```python
description = '''
Query: search terms
Search type: general/news/shopping/videos/images/scholar
Recency: hour/day/week/month/year
Location: country_code
'''
```

### LLMLayerScraperTool

**Purpose:** Extract content from any webpage in multiple formats.

**When to use:**
- Need to extract article text or documentation
- Want to analyze website content
- Need screenshots for visual analysis
- Want to generate PDFs from webpages

**Formats available:**
- `markdown` - Clean text with formatting (default)
- `html` - Full HTML source
- `screenshot` - Visual capture (returns base64-encoded image)
- `pdf` - Generated PDF (returns base64-encoded PDF)

**Options:**
- `include_images`: Keep or remove images from markdown
- `include_links`: Keep or remove hyperlinks from markdown

**Example outputs:**
- Markdown: Clean, readable text format
- HTML: Full webpage source code
- Screenshot: Base64-encoded PNG image data
- PDF: Base64-encoded PDF document

**Task description format:**
```python
description = '''
URL: webpage_url
Format: markdown/html/screenshot/pdf
Include images: true/false
Include links: true/false
'''
```

### LLMLayerPDFTool

**Purpose:** Extract full text content from PDF documents via URL.

**When to use:**
- Need to analyze PDF reports, papers, or documents
- Want to extract text from research papers
- Need to process whitepaper content
- Analyzing PDF-based documentation

**Returns:**
- Full text content extracted from PDF
- Total page count
- Original and final URL (after redirects)
- Processing metadata

**Task description format:**
```python
description = '''
URL: direct_pdf_url
Extract and analyze the content
Summarize key findings
'''
```

**Note:** URL must be a direct link to a PDF file (ends in .pdf or serves PDF content-type).

### LLMLayerYouTubeTool

**Purpose:** Extract transcripts from YouTube videos in multiple languages.

**When to use:**
- Need to analyze video content without watching
- Want to extract quotes from videos
- Need to translate or summarize video content
- Analyzing tutorial or lecture content

**Returns:**
- Full video transcript
- Detected or specified language code
- Complete video URL

**Supported languages:** 100+ languages including:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `zh` - Chinese
- And many more...

**Task description format:**
```python
description = '''
URL: youtube_video_url
Language: en/es/fr/de/etc (optional)
Analyze the content
Extract key points
'''
```

**Note:** Video must have captions/transcripts available. Auto-generated captions are supported.

## Advanced Configuration

### Using Your Own Model Provider Keys

```python
task = Task(
    description='''
    Research quantum computing.
    Model: openai/gpt-4o-mini
    Use provider_key: your_openai_api_key_here
    ''',
    agent=researcher
)
```

### Custom Timeouts and Metadata

```python
from crewai_tools import LLMLayerSearchTool

# Configure tool instance
search_tool = LLMLayerSearchTool(
    timeout=120,  # 2 minutes
    include_metadata=True  # Show response time and token usage
)

agent = Agent(
    role='Researcher',
    tools=[search_tool],
    verbose=True
)
```

## API Costs

LLMLayer uses transparent, pay-per-use pricing:

| Operation | Cost                |
|-----------|---------------------|
| Answer API (Search + AI) | Model cost + $0.004 |
| Web Search | $0.001              |
| Web Scraper | $0.001              |
| PDF Extraction | $0.002              |
| YouTube Transcript | $0.002              |

**Note:** Model costs vary by provider. Use `provider_key` to use your own model API keys (eliminates model cost).

## Error Handling

Tools return descriptive error messages instead of raising exceptions:

```python
# If API key is missing or invalid:
"Error: LLMLAYER_API_KEY not set. Set it as environment variable or pass to tool initialization."

# If API returns an error:
"Error: LLMLayer API error [authentication_error]: Invalid API key"

# If request times out:
"Error: Request timed out after 90 seconds"
```

Common error codes:
- `authentication_error` - Invalid API key
- `validation_error` - Invalid parameters
- `rate_limit` - Too many requests
- `provider_error` - LLM provider issue

## Best Practices

### 1. Use Environment Variables for API Keys

```python
# ✅ Good
import os
os.environ["LLMLAYER_API_KEY"] = "your_key"

# ❌ Bad
tool = LLMLayerSearchTool(api_key="hardcoded_key")
```

### 2. Choose the Right Model

```python
# For speed and cost
model = "openai/gpt-4o-mini"

# For quality
model = "anthropic/claude-sonnet-4"

# For long contexts
model = "google/gemini-1.5-pro"
```

### 3. Use Citations for Verifiable Information

```python
description = '''
Research climate policies.
Model: openai/gpt-4o-mini
Enable citations and return_sources
'''
```

### 4. Filter Domains for Quality

```python
description = '''
Search medical research.
Model: openai/gpt-4o-mini
Domain filter: ["nih.gov", "who.int", "nejm.org"]
'''
```

### 5. Apply Recency Filters for Current Events

```python
description = '''
Find tech news.
Model: openai/gpt-4o-mini
Date filter: day
'''
```

## Testing

Run tests:

```bash
uv run pytest tests/tools/llmlayer_tools_test.py -v
```

All tests passing: **29/29** ✓

## Support

- **Documentation:** [docs.llmlayer.ai](https://docs.llmlayer.ai)
- **API Reference:** [docs.llmlayer.ai/api-reference](https://docs.llmlayer.ai/api-reference)
- **Get API Key:** [app.llmlayer.ai](https://app.llmlayer.ai)
- **Issues:** [github.com/crewAIInc/crewAI-tools/issues](https://github.com/crewAIInc/crewAI-tools/issues)

## License

MIT License - Part of the CrewAI Tools project

---

**Built for [CrewAI](https://crewai.com) • Powered by [LLMLayer](https://llmlayer.ai)**