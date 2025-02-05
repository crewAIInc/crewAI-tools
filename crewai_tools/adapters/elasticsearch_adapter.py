from typing import Any, Callable
from elasticsearch import Elasticsearch
from openai import Client as OpenAIClient
from pydantic import Field, PrivateAttr

from crewai_tools.tools.rag.rag_tool import Adapter


def _default_embedding_function():
    client = OpenAIClient()

    def _embedding_function(input):
        rs = client.embeddings.create(input=input, model="text-embedding-ada-002")
        return [record.embedding for record in rs.data]

    return _embedding_function


class ElasticsearchAdapter(Adapter):
    es_url: str
    index_name: str
    embedding_function: Callable = Field(default_factory=_default_embedding_function)
    api_key: str | None = None
    username: str | None = None
    password: str | None = None
    cloud_id: str | None = None
    top_k: int = 3
    
    _client: Elasticsearch = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        auth_kwargs = {}
        if self.api_key:
            auth_kwargs["api_key"] = self.api_key
        elif self.username and self.password:
            auth_kwargs["basic_auth"] = (self.username, self.password)
        if self.cloud_id:
            auth_kwargs["cloud_id"] = self.cloud_id
            
        self._client = Elasticsearch(self.es_url, **auth_kwargs)
        super().model_post_init(__context)
    
    def query(self, question: str) -> str:
        query_vector = self.embedding_function([question])[0]
        response = self._client.search(
            index=self.index_name,
            body={
                "query": {
                    "bool": {
                        "should": [
                            {
                                "script_score": {
                                    "query": {"match_all": {}},
                                    "script": {
                                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                        "params": {"query_vector": query_vector}
                                    }
                                }
                            },
                            {
                                "match": {
                                    "text": {
                                        "query": question,
                                        "boost": 0.3
                                    }
                                }
                            }
                        ]
                    }
                },
                "size": self.top_k
            }
        )
        hits = response["hits"]["hits"]
        return "\n".join(hit["_source"]["text"] for hit in hits)
    
    def add(self, texts: list[str], **kwargs: Any) -> None:
        embeddings = self.embedding_function(texts)
        documents = []
        for text, embedding in zip(texts, embeddings):
            doc = {
                "text": text,
                "embedding": embedding,
                **kwargs
            }
            documents.append(doc)
        
        actions = []
        for doc in documents:
            actions.extend([
                {"index": {"_index": self.index_name}},
                doc
            ])
        self._client.bulk(
            index=self.index_name,
            body=actions
        )
