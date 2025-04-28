from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from crewai_tools.tools.rag.rag_tool import Adapter


class SimpleVectorStore(BaseModel):
    """A simple in-memory vector store implementation that doesn't use embedchain."""
    
    data: Dict[str, List[str]] = {}
    
    def add(self, source: str, content: str) -> None:
        """Add content to the vector store."""
        if source not in self.data:
            self.data[source] = []
        self.data[source].append(content)
    
    def search(self, question: str, source: Optional[str] = None) -> List[Tuple[str, float]]:
        """Simple search implementation that returns all content."""
        results = []
        
        if source:
            if source in self.data:
                for content in self.data[source]:
                    results.append((content, 1.0))
            return results
        
        for src, contents in self.data.items():
            for content in contents:
                results.append((content, 1.0))
        
        return results


class CustomAdapter(Adapter):
    """A custom adapter that doesn't depend on embedchain."""
    
    vector_store: SimpleVectorStore = SimpleVectorStore()
    summarize: bool = False
    
    def query(self, question: str) -> str:
        """Query the knowledge base with a question and return the answer."""
        results = self.vector_store.search(question)
        
        if not results:
            return "No relevant information found."
        
        if self.summarize:
            return results[0][0]
        
        return "\n\n".join([result[0] for result in results])
    
    def add(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Add content to the knowledge base."""
        source = args[0] if args else kwargs.get("source", "default")
        content = args[1] if len(args) > 1 else kwargs.get("content", "")
        
        if content:
            self.vector_store.add(source, content)
