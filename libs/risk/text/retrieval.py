from dataclasses import dataclass
from pathlib import Path

from libs.ai.vectorstore.faiss_store import FaissVectorStore, VectorItem, SearchHit
from libs.ai.embeddings.gateway import EmbeddingsGateway


@dataclass(frozen=True)
class RetrievedCase:
    case_id: str
    score: float
    text: str
    meta: dict


class CaseRetriever:
    def __init__(self, gateway: EmbeddingsGateway, store: FaissVectorStore):
        self.gateway = gateway
        self.store = store

    def retrieve(self, text: str, k: int = 3) -> list[RetrievedCase]:
        q = self.gateway.embed(text).vector
        hits: list[SearchHit] = self.store.search(q, k=k)
        out: list[RetrievedCase] = []
        for h in hits:
            out.append(RetrievedCase(case_id=h.id, score=h.score, text=h.text, meta=h.meta))
        return out

    def add_case(self, case_id: str, text: str, meta: dict | None = None):
        meta = meta or {}
        v = self.gateway.embed(text).vector
        self.store.add([v], [VectorItem(id=case_id, text=text, meta=meta)])

    def save(self, path: Path):
        self.store.save(path)

    @classmethod
    def load(cls, gateway: EmbeddingsGateway, path: Path) -> "CaseRetriever":
        store = FaissVectorStore.load(path)
        return cls(gateway=gateway, store=store)