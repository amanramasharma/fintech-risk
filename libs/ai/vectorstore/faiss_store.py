from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np
import faiss
from sklearn.neighbors import NearestNeighbors



@dataclass(frozen=True)
class VectorItem:
    id: str
    text: str
    meta: dict


@dataclass
class SearchHit:
    id: str
    score: float
    text: str
    meta: dict


class FaissVectorStore:
    def __init__(self, dim: int, items: list[VectorItem] | None = None):
        self.dim = dim
        self.items: list[VectorItem] = items or []
        self._X = np.zeros((0, dim), dtype="float32")

        self._faiss = None
        self._nn = None

    def add(self, vecs: list[list[float]], items: list[VectorItem]) -> None:
        V = np.asarray(vecs, dtype="float32")
        if V.ndim != 2 or V.shape[1] != self.dim:
            raise ValueError(f"bad vector shape: {V.shape}, expected (*,{self.dim})")

        self.items.extend(items)
        self._X = np.vstack([self._X, V]) if len(self._X) else V
        self._rebuild()

    def _rebuild(self):
        if faiss is not None:
            idx = faiss.IndexFlatIP(self.dim)
            Xn = self._normalize(self._X)
            idx.add(Xn)
            self._faiss = idx
            self._nn = None
            return

        if NearestNeighbors is None:
            raise RuntimeError("install faiss-cpu or scikit-learn for vector search")

        Xn = self._normalize(self._X)
        nn = NearestNeighbors(n_neighbors=min(10, len(Xn)), metric="cosine")
        nn.fit(Xn)
        self._nn = nn
        self._faiss = None

    def search(self, q: list[float], k: int = 5) -> list[SearchHit]:
        if len(self.items) == 0:
            return []

        qv = np.asarray(q, dtype="float32").reshape(1, -1)
        qv = self._normalize(qv)

        k = min(k, len(self.items))

        if self._faiss is not None:
            D, I = self._faiss.search(qv, k)
            hits = []
            for score, idx in zip(D[0].tolist(), I[0].tolist()):
                it = self.items[idx]
                hits.append(SearchHit(id=it.id, score=float(max(0.0, min(1.0, score))), text=it.text, meta=it.meta))
            return hits

        if self._nn is not None:
            dist, ind = self._nn.kneighbors(qv, n_neighbors=k)
            hits = []
            for d, idx in zip(dist[0].tolist(), ind[0].tolist()):
                it = self.items[idx]
                score = 1.0 - float(d)
                hits.append(SearchHit(id=it.id, score=float(max(0.0, min(1.0, score))), text=it.text, meta=it.meta))
            return hits

        return []

    def save(self, dir_path: Path) -> None:
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "items.json").write_text(
            json.dumps([{"id":i.id,"text":i.text,"meta":i.meta} for i in self.items], ensure_ascii=False),
            encoding="utf-8",
        )
        np.save(dir_path / "vectors.npy", self._X)

    @classmethod
    def load(cls, dir_path: Path) -> "FaissVectorStore":
        items_p = dir_path / "items.json"
        vec_p = dir_path / "vectors.npy"
        if not items_p.exists() or not vec_p.exists():
            raise FileNotFoundError("missing vectorstore files")

        raw_items = json.loads(items_p.read_text(encoding="utf-8"))
        items = [VectorItem(id=r["id"], text=r["text"], meta=r.get("meta") or {}) for r in raw_items]

        X = np.load(vec_p).astype("float32")
        if X.ndim != 2:
            raise ValueError("bad vectors.npy")

        store = cls(dim=int(X.shape[1]), items=items)
        store._X = X
        store._rebuild()
        return store

    def _normalize(self, X: np.ndarray) -> np.ndarray:
        n = np.linalg.norm(X, axis=1, keepdims=True)
        n[n == 0] = 1.0
        return X / n