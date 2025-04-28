import os
from tempfile import NamedTemporaryFile
from typing import cast
from unittest import mock

from pytest import fixture

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
    
    try:
        from crewai_tools.adapters.embedchain_adapter import EmbedchainAdapter
        if isinstance(tool.adapter, EmbedchainAdapter):
            adapter = cast(EmbedchainAdapter, tool.adapter)
            assert adapter.embedchain_app.llm.config.model == "gpt-3.5-custom"
            assert (
                adapter.embedchain_app.embedding_model.config.model == "text-embedding-3-custom"
            )
    except ImportError:
        from crewai_tools.adapters.custom_adapter import CustomAdapter
        assert isinstance(tool.adapter, CustomAdapter)
