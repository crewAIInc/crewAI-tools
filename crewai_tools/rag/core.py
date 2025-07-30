import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import chromadb
import litellm
from pydantic import BaseModel, Field, PrivateAttr

from crewai_tools.tools.rag.rag_tool import Adapter
from .data_types import DataType

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model: str = "text-embedding-3-small", **kwargs):
        self.model = model
        self.kwargs = kwargs

    def embed_text(self, text: str) -> List[float]:
        try:
            response = litellm.embedding(
                model=self.model,
                input=[text],
                **self.kwargs
            )
            return response.data[0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        try:
            response = litellm.embedding(
                model=self.model,
                input=texts,
                **self.kwargs
            )
            return [data['embedding'] for data in response.data]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    data_type: DataType = DataType.TEXT
    source: Optional[str] = None


class CustomRAGAdapter(Adapter):
    collection_name: str = "crewai_knowledge_base"
    persist_directory: Optional[str] = None
    embedding_model: str = "text-embedding-3-large"
    summarize: bool = False
    top_k: int = 5
    embedding_config: Dict[str, Any] = Field(default_factory=dict)

    _client: Any = PrivateAttr()
    _collection: Any = PrivateAttr()
    _embedding_service: EmbeddingService = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        try:
            if self.persist_directory:
                self._client = chromadb.PersistentClient(path=self.persist_directory)
            else:
                self._client = chromadb.Client()

            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine", "description": "CrewAI Knowledge Base"}
            )

            self._embedding_service = EmbeddingService(model=self.embedding_model, **self.embedding_config)
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

        super().model_post_init(__context)

    def add(
        self,
        content: Union[str, Path, List[str], List[Dict[str, Any]]],
        data_type: Optional[Union[str, DataType]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        loader: Optional[Any] = None,
        **kwargs: Any
    ) -> None:
        if isinstance(data_type, str):
            data_type = DataType(data_type)

        documents = []

        if isinstance(content, (str, Path)):
            if isinstance(content, Path):
                try:
                    text_content = content.read_text(encoding='utf-8')
                    source = str(content)
                except Exception as e:
                    logger.error(f"Failed to read file {content}: {e}")
                    return
            else:
                text_content = content
                source = metadata.get('source', 'text_input') if metadata else 'text_input'

            # Simple text chunking
            chunks = self._chunk_text(text_content)
            for i, chunk in enumerate(chunks):
                doc_metadata = (metadata or {}).copy()
                doc_metadata['chunk_index'] = i
                documents.append(Document(
                    content=chunk,
                    metadata=doc_metadata,
                    data_type=data_type or DataType.TEXT,
                    source=source
                ))

        if not documents:
            logger.warning("No documents to add")
            return

        contents = [doc.content for doc in documents]
        try:
            embeddings = self._embedding_service.embed_batch(contents)
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return

        ids = [doc.id for doc in documents]
        metadatas = []

        for doc in documents:
            doc_metadata = doc.metadata.copy()
            doc_metadata.update({
                "data_type": doc.data_type.value,
                "source": doc.source or "unknown"
            })
            metadatas.append(doc_metadata)

        try:
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to knowledge base")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")

    def query(self, question: str, where: Optional[Dict[str, Any]] = None) -> str:
        try:
            question_embedding = self._embedding_service.embed_text(question)

            results = self._collection.query(
                query_embeddings=[question_embedding],
                n_results=self.top_k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            if not results or not results.get("documents") or not results["documents"][0]:
                return "No relevant content found."

            documents = results["documents"][0]
            metadatas = results.get("metadatas", [None])[0] or []
            distances = results.get("distances", [None])[0] or []

            # Return sources with relevance scores
            formatted_results = []
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0
                source = metadata.get("source", "unknown") if metadata else "unknown"
                score = 1 - distance if distance is not None else 0  # Convert distance to similarity
                formatted_results.append(f"[Source: {source}, Relevance: {score:.3f}]\n{doc}")

            return "\n\n".join(formatted_results)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Error querying knowledge base: {e}"

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap
            if start >= len(text):
                break

        return chunks

    def delete_collection(self) -> None:
        try:
            self._client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")

    def get_collection_info(self) -> Dict[str, Any]:
        try:
            count = self._collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
