import pytest
from unittest.mock import Mock, patch
from crewai_tools.tools.llmlayer_tools import (
    LLMLayerSearchTool,
    LLMLayerWebSearchTool,
    LLMLayerScraperTool,
    LLMLayerPDFTool,
    LLMLayerYouTubeTool,
)


class TestLLMLayerSearchTool:
    @patch('requests.post')
    def test_search_basic_success(self, mock_post):
        """Test basic search functionality with successful response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "llm_response": "AI is advancing rapidly in 2024.",
            "response_time": "2.5",
            "input_tokens": 100,
            "output_tokens": 50,
            "model_cost": 0.001,
            "llmlayer_cost": 0.002,
            "sources": [],
            "images": []
        }
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="What is AI?", model="openai/gpt-4o-mini")

        assert "AI is advancing rapidly" in result
        assert "Response time:" not in result  # metadata disabled by default
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_search_with_metadata(self, mock_post):
        """Test search with metadata enabled"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "llm_response": "Test response",
            "response_time": "2.5",
            "input_tokens": 100,
            "output_tokens": 50,
            "sources": [],
            "images": []
        }
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key", include_metadata=True)
        result = tool._run(query="test", model="openai/gpt-4o-mini")

        assert "Response time:" in result
        assert "Tokens:" in result

    @patch('requests.post')
    def test_search_with_sources(self, mock_post):
        """Test search with sources returned"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "llm_response": "Test response",
            "response_time": "1.0",
            "input_tokens": 50,
            "output_tokens": 30,
            "sources": [
                {"title": "Source 1", "link": "https://example.com", "snippet": "Test snippet"}
            ],
            "images": []
        }
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="openai/gpt-4o-mini", return_sources=True)

        assert "Sources" in result
        assert "Source 1" in result
        assert "https://example.com" in result

    @patch('requests.post')
    def test_search_with_images(self, mock_post):
        """Test search with images returned"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "llm_response": "Test response",
            "response_time": "1.5",
            "input_tokens": 60,
            "output_tokens": 40,
            "sources": [],
            "images": [
                {"title": "Image 1", "imageUrl": "https://example.com/image.jpg"}
            ]
        }
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="openai/gpt-4o-mini", return_images=True)

        assert "Images" in result
        assert "Image 1" in result

    def test_search_missing_api_key(self):
        """Test that missing API key returns error"""
        tool = LLMLayerSearchTool(api_key="")
        result = tool._run(query="test", model="openai/gpt-4o-mini")
        assert "Error: LLMLAYER_API_KEY not set" in result

    @patch('requests.post')
    def test_search_api_error(self, mock_post):
        """Test handling of API errors"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.json.return_value = {
            "detail": {
                "error_code": "invalid_model",
                "message": "Model not supported"
            }
        }
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="invalid-model")

        assert "Error:" in result
        assert "invalid_model" in result

    @patch('requests.post')
    def test_search_json_response(self, mock_post):
        """Test JSON response format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "llm_response": {"key": "value"},
            "response_time": "1.0",
            "input_tokens": 50,
            "output_tokens": 30,
            "sources": [],
            "images": []
        }
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="openai/gpt-4o-mini", answer_type="json")

        assert '"key"' in result
        assert '"value"' in result


class TestLLMLayerWebSearchTool:
    @patch('requests.post')
    def test_web_search_basic(self, mock_post):
        """Test basic web search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"title": "Test Result", "link": "https://test.com", "snippet": "Test snippet"}
            ],
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerWebSearchTool(api_key="test_key", include_metadata=True)
        result = tool._run(query="test query")

        assert "Test Result" in result
        assert "https://test.com" in result
        assert "Cost:" in result

    @patch('requests.post')
    def test_web_search_no_results(self, mock_post):
        """Test web search with no results"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [], "cost": 0.001}
        mock_post.return_value = mock_response

        tool = LLMLayerWebSearchTool(api_key="test_key")
        result = tool._run(query="test")

        assert "No results found" in result

    def test_web_search_missing_api_key(self):
        """Test that missing API key returns error"""
        tool = LLMLayerWebSearchTool(api_key="")
        result = tool._run(query="test")
        assert "Error: LLMLAYER_API_KEY not set" in result

    @patch('requests.post')
    def test_web_search_multiple_results(self, mock_post):
        """Test web search with multiple results"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"title": "Result 1", "link": "https://test1.com", "snippet": "Snippet 1"},
                {"title": "Result 2", "url": "https://test2.com", "description": "Snippet 2"}
            ],
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerWebSearchTool(api_key="test_key")
        result = tool._run(query="test")

        assert "Result 1" in result
        assert "Result 2" in result
        assert "https://test1.com" in result
        assert "https://test2.com" in result


class TestLLMLayerScraperTool:
    @patch('requests.post')
    def test_scraper_markdown(self, mock_post):
        """Test scraping in markdown format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "markdown": "# Test Content\n\nThis is test content.",
            "url": "https://example.com",
            "status_code": 200,
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerScraperTool(api_key="test_key", include_metadata=True)
        result = tool._run(url="https://example.com", format="markdown")

        assert "Test Content" in result
        assert "Status: 200" in result

    @patch('requests.post')
    def test_scraper_html(self, mock_post):
        """Test scraping in HTML format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "markdown": "fallback",
            "html": "<html><body>Test</body></html>",
            "url": "https://example.com",
            "status_code": 200,
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerScraperTool(api_key="test_key")
        result = tool._run(url="https://example.com", format="html")

        assert "<html>" in result or "HTML" in result

    @patch('requests.post')
    def test_scraper_screenshot(self, mock_post):
        """Test scraping in screenshot format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "markdown": "",
            "screenshot_data": "base64encodeddata",
            "url": "https://example.com",
            "status_code": 200,
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerScraperTool(api_key="test_key")
        result = tool._run(url="https://example.com", format="screenshot")

        assert "Screenshot" in result
        assert "base64" in result

    def test_scraper_missing_api_key(self):
        """Test that missing API key returns error"""
        tool = LLMLayerScraperTool(api_key="")
        result = tool._run(url="https://example.com")
        assert "Error: LLMLAYER_API_KEY not set" in result


class TestLLMLayerPDFTool:
    @patch('requests.post')
    def test_pdf_extraction(self, mock_post):
        """Test PDF text extraction"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "This is extracted PDF text.",
            "pages": 5,
            "url": "https://example.com/doc.pdf",
            "status_code": 200,
            "cost": 0.005
        }
        mock_post.return_value = mock_response

        tool = LLMLayerPDFTool(api_key="test_key", include_metadata=True)
        result = tool._run(url="https://example.com/doc.pdf")

        assert "extracted PDF text" in result
        assert "Pages:** 5" in result
        assert "Status: 200" in result

    def test_pdf_missing_api_key(self):
        """Test that missing API key returns error"""
        tool = LLMLayerPDFTool(api_key="")
        result = tool._run(url="https://example.com/doc.pdf")
        assert "Error: LLMLAYER_API_KEY not set" in result

    @patch('requests.post')
    def test_pdf_error_handling(self, mock_post):
        """Test PDF extraction error handling"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.json.return_value = {
            "detail": {
                "error_code": "pdf_not_found",
                "message": "PDF not found"
            }
        }
        mock_post.return_value = mock_response

        tool = LLMLayerPDFTool(api_key="test_key")
        result = tool._run(url="https://example.com/missing.pdf")

        assert "Error:" in result
        assert "pdf_not_found" in result


class TestLLMLayerYouTubeTool:
    @patch('requests.post')
    def test_youtube_transcript(self, mock_post):
        """Test YouTube transcript extraction"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transcript": "This is the video transcript.",
            "url": "https://youtube.com/watch?v=test",
            "language": "en",
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerYouTubeTool(api_key="test_key")
        result = tool._run(url="https://youtube.com/watch?v=test")

        assert "video transcript" in result
        assert "Language:** en" in result

    @patch('requests.post')
    def test_youtube_with_language(self, mock_post):
        """Test YouTube transcript with specific language"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transcript": "Transcript in Spanish",
            "url": "https://youtube.com/watch?v=test",
            "language": "es",
            "cost": 0.001
        }
        mock_post.return_value = mock_response

        tool = LLMLayerYouTubeTool(api_key="test_key")
        result = tool._run(url="https://youtube.com/watch?v=test", language="es")

        assert "Transcript" in result
        assert "es" in result

    def test_youtube_missing_api_key(self):
        """Test that missing API key returns error"""
        tool = LLMLayerYouTubeTool(api_key="")
        result = tool._run(url="https://youtube.com/watch?v=test")
        assert "Error: LLMLAYER_API_KEY not set" in result


class TestToolInitialization:
    def test_api_key_from_env(self):
        """Test API key loading from environment"""
        with patch.dict('os.environ', {'LLMLAYER_API_KEY': 'env_key'}):
            tool = LLMLayerSearchTool()
            assert tool.api_key == 'env_key'

    def test_api_key_override(self):
        """Test API key can be overridden"""
        with patch.dict('os.environ', {'LLMLAYER_API_KEY': 'env_key'}):
            tool = LLMLayerSearchTool(api_key='custom_key')
            assert tool.api_key == 'custom_key'

    def test_custom_timeout(self):
        """Test custom timeout configuration"""
        tool = LLMLayerSearchTool(api_key='test', timeout=120)
        assert tool.timeout == 120

    def test_metadata_flag(self):
        """Test metadata flag configuration"""
        tool = LLMLayerSearchTool(api_key='test', include_metadata=True)
        assert tool.include_metadata is True

    def test_default_values(self):
        """Test default initialization values"""
        tool = LLMLayerSearchTool(api_key='test')
        assert tool.timeout == 90
        assert tool.include_metadata is False


class TestErrorHandling:
    @patch('requests.post')
    def test_timeout_error(self, mock_post):
        """Test timeout error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="openai/gpt-4o-mini")

        assert "Error:" in result
        assert "timed out" in result

    @patch('requests.post')
    def test_connection_error(self, mock_post):
        """Test connection error handling"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="openai/gpt-4o-mini")

        assert "Error:" in result

    @patch('requests.post')
    def test_malformed_json_response(self, mock_post):
        """Test handling of malformed JSON in error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_post.return_value = mock_response

        tool = LLMLayerSearchTool(api_key="test_key")
        result = tool._run(query="test", model="openai/gpt-4o-mini")

        assert "Error:" in result
        assert "500" in result