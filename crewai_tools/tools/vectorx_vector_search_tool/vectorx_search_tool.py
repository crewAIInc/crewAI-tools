import os
import logging
import uuid
from typing import List, Dict, Callable, Optional, Any, Type

from pydantic import BaseModel
from crewai.tools import BaseTool

# Try importing dependencies with optional installation notes
try:
    from vecx.vectorx import VectorX
except ImportError:
    raise ImportError("Install vecx package via 'pip install vecx' to use VectorX features.")

try:
    from google import genai  # Gemini client
except ImportError:
    genai = None

try:
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    import torch
except ImportError:
    AutoTokenizer = None
    AutoModelForMaskedLM = None
    torch = None

_logger = logging.getLogger(__name__)


# ---------------- Sparse SPLADE Wrapper ---------------- #
class SpladeSparseEmbedder:
    """Wrapper for SPLADE (prithivida/Splade_PP_en_v1) to generate sparse vectors.

    This is used for hybrid search, combining dense and sparse representations.
    """

    def __init__(self, model_name: str = None):
        """Initializes the SPLADE model and tokenizer."""
        self.model_name = model_name or os.environ.get("SPLADE_MODEL", "prithivida/Splade_PP_en_v1")
        if AutoTokenizer is None or AutoModelForMaskedLM is None:
            raise ImportError("transformers not installed. Install with `pip install transformers`")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(self.model_name)
        self.model.eval()
        self.vocab_size = self.model.config.vocab_size

    def get_vocab_size(self) -> int:
        """Returns vocabulary size of the model."""
        return self.vocab_size

    def encode_query(self, text: str, return_sparse: bool = True):
        """Encodes a query into sparse format using SPLADE.

        Args:
            text: Input query text.
            return_sparse: If True, returns indices and values.

        Returns:
            A list of sparse vectors with indices and values or raw logits.
        """
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**inputs).logits.squeeze(0)  # shape: [seq_len, vocab]
            max_logits, _ = torch.max(logits, dim=0)         # shape: [vocab]
            scores = torch.log1p(torch.relu(max_logits)).cpu().numpy()

        nz = scores.nonzero()[0]
        values = scores[nz]

        if return_sparse:
            return [{"indices": nz.tolist(), "values": values.tolist()}]
        return scores


# ---------------- CrewAI Tool: VectorX Search ---------------- #
class VectorXSearchArgs(BaseModel):
    """Argument schema for VectorX search tool."""
    query: str
    top_k: Optional[int] = None


class VectorXVectorSearchTool(BaseTool):
    """
    CrewAI Tool for semantic search using VectorX vector database.

    Supports both dense (semantic) and sparse (keyword-like via SPLADE) search.
    Default embedding model is Gemini via `google-genai`.

    Attributes:
        api_token: API token for VectorX.
        collection_name: Name of the index/collection in VectorX.
        embed_fn: Custom embedding function (optional).
        encryption_key: Encryption key for secure collections.
        space_type: Vector distance metric (e.g., "cosine").
        use_sparse: Whether to use sparse (SPLADE) embedding.
        sparse_embedder: SPLADE embedder instance.
        sparse_vocab_size: Vocabulary size for sparse encoder.
        top_k: Number of results to retrieve.
    """

    name: str = "VectorXVectorSearchTool"
    description: str = (
        "Tool for semantic search using VectorX vector DB "
        "with optional sparse embedding support (SPLADE)."
    )
    args_schema: Type[BaseModel] = VectorXSearchArgs

    def __init__(
        self,
        api_token: str,
        collection_name: str,
        embed_fn: Optional[Callable[[str], List[float]]] = None,
        encryption_key: Optional[str] = None,
        space_type: str = "cosine",
        use_sparse: bool = False,
        sparse_embedder: Optional[Any] = None,
        sparse_vocab_size: Optional[int] = None,
        top_k: int = 3,
        gemini_model: Optional[str] = None,
    ):
        """Initializes the VectorX search tool, sets up index and embedding model."""
        super().__init__()
        object.__setattr__(self, "api_token", api_token)
        object.__setattr__(self, "collection_name", collection_name)
        object.__setattr__(self, "encryption_key", encryption_key)
        object.__setattr__(self, "space_type", space_type)
        object.__setattr__(self, "use_sparse", use_sparse)
        object.__setattr__(self, "top_k", top_k)

        gemini_model = gemini_model or os.environ.get("GEMINI_MODEL", "models/embedding-001")
        _logger.info(f"Using Gemini embedding model: {gemini_model}")

        # Setup sparse encoder
        if use_sparse:
            if sparse_embedder is None:
                sparse_embedder = SpladeSparseEmbedder()
            object.__setattr__(self, "sparse_embedder", sparse_embedder)
            sparse_vocab_size = sparse_vocab_size or sparse_embedder.get_vocab_size()
        else:
            object.__setattr__(self, "sparse_embedder", None)
            sparse_vocab_size = 0
        object.__setattr__(self, "sparse_vocab_size", sparse_vocab_size)

        # Dense embedding function setup (default: Gemini)
        if embed_fn:
            object.__setattr__(self, "embed_fn", embed_fn)
        else:
            if genai is None:
                raise ImportError("google-genai not installed. Install with `pip install google-genai`")

            gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

            def gemini_embed(text: str) -> List[float]:
                """Uses Gemini to generate dense embeddings."""
                emb = gemini_client.models.embed_content(
                    model=gemini_model,
                    contents=text
                )
                vector_obj = emb.embeddings[0].values
                vec = [float(v) for v in (vector_obj.values() if isinstance(vector_obj, dict) else vector_obj)]
                _logger.debug(f"Gemini embedding len={len(vec)}, sample={vec[:5]}")
                return vec

            object.__setattr__(self, "embed_fn", gemini_embed)

        # Setup VectorX index
        client = VectorX(token=api_token)
        object.__setattr__(self, "client", client)

        # Determine embedding dimension
        dim = len(self.embed_fn("test"))
        try:
            if use_sparse:
                index = client.get_hybrid_index(name=collection_name, key=encryption_key)
            else:
                index = client.get_index(name=collection_name, key=encryption_key)
        except Exception:
            _logger.info(f"Creating new index {collection_name}")
            if use_sparse:
                client.create_hybrid_index(
                    name=collection_name,
                    dimension=dim,
                    space_type=space_type,
                    vocab_size=sparse_vocab_size,
                    key=encryption_key,
                )
                index = client.get_hybrid_index(name=collection_name, key=encryption_key)
            else:
                client.create_index(
                    name=collection_name,
                    dimension=dim,
                    space_type=space_type,
                    key=encryption_key,
                )
                index = client.get_index(name=collection_name, key=encryption_key)

        object.__setattr__(self, "index", index)

    def _prepare_sparse_vector(self, text: str) -> Dict[str, Any]:
        """Generates sparse representation for given text using SPLADE."""
        sparse_vec = self.sparse_embedder.encode_query(text, return_sparse=True)[0]
        return sparse_vec

    def _run(self, query: str, top_k: Optional[int] = None, **kwargs) -> Any:
        """Performs a semantic or hybrid search on VectorX.

        Args:
            query: The search query.
            top_k: Number of top results to return.

        Returns:
            A list of search results or error messages.
        """
        top_k = top_k or self.top_k
        embedding = self.embed_fn(query)
        results = []

        try:
            if self.use_sparse:
                sparse_vec = self._prepare_sparse_vector(query)
                search_results = self.index.search(
                    dense_vector=embedding,
                    sparse_vector=sparse_vec,
                    dense_top_k=top_k,
                    sparse_top_k=top_k,
                    filter_query={},
                )
                for r in search_results:
                    results.append({
                        "text": r["meta"].get("value", ""),
                        "score": r.get("rrf_score", 0),
                        "metadata": r["meta"],
                    })
            else:
                search_results = self.index.query(
                    vector=embedding,
                    top_k=top_k,
                    include_vectors=False,
                )
                for r in search_results:
                    results.append({
                        "text": r["meta"].get("value", ""),
                        "score": r.get("similarity", 0),
                        "metadata": r["meta"],
                    })
        except Exception as e:
            _logger.error(f"VectorX Search Error: {e}")
            return [{"error": "Search failed"}]

        return results or [{"message": "No results found"}]

    def store_documents(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """Stores a list of documents into the VectorX index.

        Args:
            texts: List of documents to store.
            metadatas: Optional metadata dicts corresponding to each document.
        """
        metadatas = metadatas or [{} for _ in texts]
        events = []

        for text, meta in zip(texts, metadatas):
            meta["value"] = text
            embedding = self.embed_fn(text)

            event = {
                "id": str(uuid.uuid4()),
                "meta": meta,
            }

            if self.use_sparse:
                sparse_vec = self._prepare_sparse_vector(text)
                event["dense_vector"] = embedding
                event["sparse_vector"] = sparse_vec
            else:
                event["vector"] = embedding

            events.append(event)

        try:
            self.index.upsert(events)
        except Exception as e:
            _logger.error(f"VectorX Upsert Error: {e}")
