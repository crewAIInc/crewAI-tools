from typing import Any, Optional

from pydantic import BaseModel

from crewai_tools.adapters.custom_adapter import CustomAdapter
from crewai_tools.tools.rag.rag_tool import Adapter


class CustomPDFAdapter(CustomAdapter):
    """A custom PDF adapter that doesn't depend on embedchain."""
    
    src: Optional[str] = None
    
    def query(self, question: str) -> str:
        """Query the knowledge base with a question and return the answer."""
        results = self.vector_store.search(question, self.src)
        
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
        self.src = args[0] if args else None
        
        source = args[0] if args else kwargs.get("source", "default")
        pdf_path = source
        
        content = f"Content from PDF: {pdf_path}"
        self.vector_store.add(source, content)
