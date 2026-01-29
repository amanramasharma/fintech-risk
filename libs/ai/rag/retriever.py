from dataclasses import dataclass
from libs.ai.embeddings.gateway import EmbeddingsGateway
from libs.ai.rag.vector_store import FaissVectorStore, VectorDoc


@dataclass(frozen=True)
class Retriever:
    embeddings: EmbeddingsGateway
    store: FaissVectorStore

    def retrieve(self, query: str, k: int = 5) -> list[VectorDoc]:
        q = self.embeddings.embed(query).vector
        return self.store.search(q, k=k)