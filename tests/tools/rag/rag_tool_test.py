import os
from contextlib import ExitStack
from tempfile import NamedTemporaryFile
from typing import cast
from unittest import mock

import pytest
from google.auth.exceptions import GoogleAuthError
from pytest import fixture

from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter
from crewai_tools.tools.rag.rag_tool import RagTool


@fixture(autouse=True)
def mock_embedchain_db_uri():
    with NamedTemporaryFile() as tmp:
        uri = f"sqlite:///{tmp.name}"
        with mock.patch.dict(os.environ, {
            "EMBEDCHAIN_DB_URI": uri,
            "OPENAI_API_KEY": "sk-mock-key"
        }, clear=True), \
        mock.patch("embedchain.core.db.database.alembic_upgrade"):
            yield


def test_custom_llm_and_embedder():
    class MyTool(RagTool):
        pass

    tool = MyTool(
        config=dict(
            llm=dict(
                provider="openai",
                config=dict(model="gpt-3.5-custom"),
            ),
            embedder=dict(
                provider="openai",
                config=dict(model="text-embedding-3-custom"),
            ),
        )
    )
    assert tool.adapter is not None
    assert isinstance(tool.adapter, EmbedchainAdapter)

    adapter = cast(EmbedchainAdapter, tool.adapter)
    assert adapter.embedchain_app.llm.config.model == "gpt-3.5-custom"
    assert (
        adapter.embedchain_app.embedding_model.config.model == "text-embedding-3-custom"
    )


VERTEX_AI_CONFIG = {
    "llm": {
        "provider": "vertexai",
        "config": {
            "model": "gemini-2.0-flash",
            "temperature": 1.0,
            "top_p": 1.0,
        },
    },
    "embedder": {
        "provider": "vertexai",
        "config": {
            "model": "text-multilingual-embedding-002",
        },
    },
}


def test_vertexai_config() -> None:
    """
    Test VertexAI configuration in RagTool with location parameter support.
    
    Verifies:
    - Proper initialization of VertexAI with location parameter.
    - Correct model configuration for both LLM and embedder.
    - Environment variable handling.
    """
    class MyTool(RagTool):
        pass

    mock_env = {
        "VERTEXAI_LOCATION": "us-central1",
        "GOOGLE_CLOUD_PROJECT": "mock-project-id"
    }
    
    mocks = [
        mock.patch.dict(os.environ, mock_env),
        mock.patch("google.auth.default", return_value=(None, "mock-project-id")),
        mock.patch("google.cloud.aiplatform.initializer._Config.project", 
                  new_callable=mock.PropertyMock, 
                  return_value="mock-project-id"),
        mock.patch("vertexai.init"),
        mock.patch("langchain_google_vertexai.ChatVertexAI"),
        mock.patch("langchain_google_vertexai.VertexAIEmbeddings")
    ]
    
    with ExitStack() as stack:
        for m in mocks:
            stack.enter_context(m)
        
        tool: RagTool = MyTool(config=VERTEX_AI_CONFIG)
        assert tool.adapter is not None
        assert isinstance(tool.adapter, EmbedchainAdapter)

        adapter: EmbedchainAdapter = cast(EmbedchainAdapter, tool.adapter)
        assert adapter.embedchain_app.llm.config.model == "gemini-2.0-flash"
        assert (
            adapter.embedchain_app.embedding_model.config.model
            == "text-multilingual-embedding-002"
        )


def test_vertexai_config_missing_location() -> None:
    """
    Test VertexAI configuration with missing location parameter.
    
    Verifies that attempting to initialize VertexAI without a location
    parameter raises an appropriate error.
    """
    class MyTool(RagTool):
        pass

    mock_llm = mock.MagicMock()
    mock_llm.side_effect = GoogleAuthError("Unable to find your project")
    mock_embedder = mock.MagicMock()
    mock_embedder.side_effect = GoogleAuthError("Unable to find your project")

    mocks = [
        mock.patch.dict(os.environ, {}, clear=True),
        mock.patch("embedchain.llm.vertex_ai.VertexAILlm", mock_llm),
        mock.patch("embedchain.embedder.vertexai.VertexAIEmbeddings", mock_embedder),
        mock.patch("embedchain.core.db.database.alembic_upgrade")
    ]
    
    with ExitStack() as stack:
        for m in mocks:
            stack.enter_context(m)
        with pytest.raises(GoogleAuthError, match="Unable to find your project"):
            MyTool(config=VERTEX_AI_CONFIG)
