import os
from tempfile import NamedTemporaryFile
from typing import cast
from unittest import mock

from pytest import fixture

from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter
from crewai_tools.tools.rag.rag_tool import RagTool


@fixture(autouse=True)
def mock_embedchain_db_uri():
    with NamedTemporaryFile() as tmp:
        uri = f"sqlite:///{tmp.name}"
        with mock.patch.dict(os.environ, {"EMBEDCHAIN_DB_URI": uri}):
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


def test_vertexai_config():
    class MyTool(RagTool):
        pass

    with mock.patch.dict(os.environ, {
        "VERTEXAI_LOCATION": "us-central1",
        "GOOGLE_CLOUD_PROJECT": "mock-project-id"
    }), mock.patch("google.auth.default", return_value=(None, "mock-project-id")), \
    mock.patch("google.cloud.aiplatform.initializer._Config.project", new_callable=mock.PropertyMock, return_value="mock-project-id"), \
    mock.patch("vertexai.init"), \
    mock.patch("langchain_google_vertexai.ChatVertexAI"), \
    mock.patch("langchain_google_vertexai.VertexAIEmbeddings"):
        tool = MyTool(
            config=dict(
                llm=dict(
                    provider="vertexai",
                    config=dict(
                        model="gemini-2.0-flash",
                        temperature=1.0,
                        top_p=1.0,
                    ),
                ),
                embedder=dict(
                    provider="vertexai",
                    config=dict(
                        model="text-multilingual-embedding-002",
                    ),
                ),
            )
        )
        assert tool.adapter is not None
        assert isinstance(tool.adapter, EmbedchainAdapter)

        adapter = cast(EmbedchainAdapter, tool.adapter)
        assert adapter.embedchain_app.llm.config.model == "gemini-2.0-flash"
        assert (
            adapter.embedchain_app.embedding_model.config.model
            == "text-multilingual-embedding-002"
        )
