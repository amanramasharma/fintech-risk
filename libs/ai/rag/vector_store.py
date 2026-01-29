from dataclasses import dataclass
from typing import Any
import json
from pathlib import Path

import numpy as np

try:
    import faiss
except Exception as e:
    raise RuntimeError("faiss-cpu is required for local vector store") from e


@dataclass(frozen=True)
class VectorDoc:
    doc_id: str
    text: str
    metadata: dict[str, Any]


class FaissVectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.docs: list[VectorDoc] = []

    def add(self, vectors: list[list[float]], docs: list[VectorDoc]) -> None:
        X = np.array(vectors, dtype="float32")
        faiss.normalize_L2(X)
        self.index.add(X)
        self.docs.extend(docs)

    def search(self, query_vec: list[float], k: int = 5) -> list[VectorDoc]:
        q = np.array([query_vec], dtype="float32")
        faiss.normalize_L2(q)
        scores, idx = self.index.search(q, k)
        out = []
        for i in idx[0]:
            if i < 0:
                continue
            out.append(self.docs[int(i)])
        return out

    def save(self, dir_path: Path) -> None:
        dir_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(dir_path / "index.faiss"))
        payload = [{"doc_id": d.doc_id, "text": d.text, "metadata": d.metadata} for d in self.docs]
        (dir_path / "docs.json").write_text(json.dumps(payload), encoding="utf-8")

    @classmethod
    def load(cls, dir_path: Path) -> "FaissVectorStore":
        idx = faiss.read_index(str(dir_path / "index.faiss"))
        raw = json.loads((dir_path / "docs.json").read_text(encoding="utf-8"))
        dim = idx.d
        store = cls(dim=dim)
        store.index = idx
        store.docs = [VectorDoc(**r) for r in raw]
        return store