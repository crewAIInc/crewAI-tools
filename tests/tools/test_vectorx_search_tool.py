import pytest

# Import VectorX tool class 
from crewai_tools import VectorXVectorSearchTool

# ==== Utility Functions / Dummy Classes ====

def dummy_embed(text: str):
    """Returns a fixed-size dense embedding for testing."""
    return [0.1] * 128

class DummyIndex:
    """Simulates index behavior for upsert, query, and hybrid search."""
    def __init__(self):
        self.docs = []

    def upsert(self, events):
        self.docs.extend(events)

    def query(self, vector, top_k, include_vectors):
        return self.docs[:top_k]

    def search(self, dense_vector, sparse_vector, dense_top_k, sparse_top_k, filter_query):
        return self.docs[:dense_top_k]

class DummyClient:
    """Simulates VectorX client with index lifecycle methods."""
    def get_index(self, name, key=None):
        return DummyIndex()

    def create_index(self, name, dimension, space_type, key=None):
        return True

    def get_hybrid_index(self, name, key=None):
        return DummyIndex()

    def create_hybrid_index(self, name, dimension, space_type, vocab_size, key=None):
        return True

class DummySPLADE:
    """Simulates SPLADE sparse embedder for hybrid search."""
    def get_vocab_size(self):
        return 10

    def encode_query(self, text, return_sparse=True):
        return [{"indices": [0], "values": [1.0]}]

# ==== Fixtures ====

@pytest.fixture
def vx_tool(monkeypatch):
    """
    Fixture that provides a VectorXVectorSearchTool with
    its VectorX client monkeypatched to the DummyClient.
    """
    monkeypatch.setattr(
        "crewai_tools.tools.vectorx_vector_search_tool.vectorx_search_tool.VectorX",
        lambda token: DummyClient()
    )
    return VectorXVectorSearchTool(
        api_token="fake-token",
        collection_name="test_collection",
        embed_fn=dummy_embed,
        use_sparse=False
    )

# ==== Tests ====

def test_store_and_search_dense(vx_tool):
    """
    Tests dense-only mode:
    - Documents are stored via store_documents()
    - Search returns results with `text` and `score` fields
    """
    vx_tool.store_documents(["doc1", "doc2"], [{"id": "1"}, {"id": "2"}])
    results = vx_tool._run("query")
    assert isinstance(results, list)
    assert "text" in results[0]
    assert results[0]["text"] == "doc1"
    assert "score" in results[0]

def test_hybrid_search(monkeypatch):
    """
    Tests hybrid mode (dense + sparse):
    - SPLADE embedder is replaced with DummySPLADE
    - Documents are stored and search returns expected results
    """
    monkeypatch.setattr(
        "crewai_tools.tools.vectorx_vector_search_tool.vectorx_search_tool.VectorX",
        lambda token: DummyClient()
    )
    monkeypatch.setattr(
        "crewai_tools.tools.vectorx_vector_search_tool.vectorx_search_tool.SpladeSparseEmbedder",
        lambda *args, **kwargs: DummySPLADE()
    )
    tool = VectorXVectorSearchTool(
        api_token="tok",
        collection_name="hybrid_col",
        embed_fn=dummy_embed,
        use_sparse=True
    )
    tool.store_documents(["doc_hybrid"], [{"id": "h1"}])
    results = tool._run("query")
    assert isinstance(results, list)
    assert results[0]["text"] == "doc_hybrid"