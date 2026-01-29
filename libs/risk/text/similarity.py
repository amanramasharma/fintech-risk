from pydantic import BaseModel, Field
from math import sqrt

class SimilarityHit(BaseModel):
    label: str
    score: float = Field(...,ge=0.0, le=1.0)

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x,y in zip(a,b))
    na = sqrt(sum( x * x for x in a)) or 1.0
    nb = sqrt(sum(y * y for y in b)) or 1.0
    return max(0.0, min(1.0, dot/ (na*nb)))

def top_hits(query_vec: list[float], labels: dict[str, list[float]], k: int=3) -> list[SimilarityHit]:
    scored = [(name,cosine_similarity(query_vec,vec)) for name,vec in labels.items()]
    scored.sort(key=lambda x:x[1], reverse=True)
    return [SimilarityHit(label=n, score=s) for n,s in scored[:k]]
