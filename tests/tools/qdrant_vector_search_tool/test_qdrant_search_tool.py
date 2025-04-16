import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from crewai_tools.tools.qdrant_vector_search_tool.qdrant_search_tool import (
    QdrantVectorSearchTool,
    QDRANT_AVAILABLE,
)


@pytest.mark.skipif(not QDRANT_AVAILABLE, reason="Qdrant client not available")
class TestQdrantVectorSearchTool:
    @pytest.fixture
    def mock_vector(self):
        return [0.1, 0.2, 0.3]

    @pytest.fixture
    def mock_search_results(self):
        mock_point = MagicMock()
        mock_point_data = MagicMock()
        mock_point_data.payload = {"metadata": {"title": "Test"}, "text": "Test content"}
        mock_point_data.score = 0.95
        mock_point.__getitem__.side_effect = lambda idx: ([mock_point_data] if idx == 1 else None)
        return [mock_point]

    @pytest.fixture
    def async_mock_search_results(self):
        mock_point = MagicMock()
        mock_point_data = MagicMock()
        mock_point_data.payload = {"metadata": {"title": "Test"}, "text": "Test content"}
        mock_point_data.score = 0.95
        mock_point.__getitem__.side_effect = lambda idx: ([mock_point_data] if idx == 1 else None)
        return [mock_point]

    @patch("crewai_tools.tools.qdrant_vector_search_tool.qdrant_search_tool.QdrantClient")
    def test_run(self, mock_qdrant_client, mock_vector, mock_search_results):
        mock_client_instance = mock_qdrant_client.return_value
        mock_client_instance.query_points.return_value = mock_search_results
        
        tool = QdrantVectorSearchTool(
            qdrant_url="http://localhost:6333",
            collection_name="test_collection"
        )
        
        tool._vectorize_query = MagicMock(return_value=mock_vector)
        
        result = tool._run("test query")
        result_json = json.loads(result)
        
        assert mock_client_instance.query_points.called
        assert len(result_json) == 1
        assert result_json[0]["metadata"] == {"title": "Test"}
        assert result_json[0]["context"] == "Test content"
        assert result_json[0]["distance"] == 0.95

    @patch("crewai_tools.tools.qdrant_vector_search_tool.qdrant_search_tool.AsyncQdrantClient")
    @pytest.mark.asyncio
    async def test_arun(self, mock_async_qdrant_client, mock_vector, async_mock_search_results):
        mock_client_instance = mock_async_qdrant_client.return_value
        mock_client_instance.query_points = AsyncMock(return_value=async_mock_search_results)
        
        tool = QdrantVectorSearchTool(
            qdrant_url="http://localhost:6333",
            collection_name="test_collection"
        )
        
        tool._vectorize_query = MagicMock(return_value=mock_vector)
        
        result = await tool._arun("test query")
        result_json = json.loads(result)
        
        assert mock_client_instance.query_points.called
        assert len(result_json) == 1
        assert result_json[0]["metadata"] == {"title": "Test"}
        assert result_json[0]["context"] == "Test content"
        assert result_json[0]["distance"] == 0.95
