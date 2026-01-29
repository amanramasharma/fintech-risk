from dataclasses import dataclass
from typing import Protocol
from pydantic import BaseModel, Field


class EmbeddingResult(BaseModel):
    model: str
    vector: list[float] = Field(..., min_length=8)

class EmbeddingsProvider(Protocol):
    def embed(self, text: str) -> EmbeddingResult:
        ...

@dataclass(frozen=True)
class EmbeddingsGatewayConfig:
    provider: str
    model: str


class EmbeddingsGateway:
    def __init__(self, cfg: EmbeddingsGatewayConfig, provider: EmbeddingsProvider):
        self.cfg = cfg
        self._provider = provider

    def embed(self, text: str) -> EmbeddingResult:
        t = text.strip()
        if not t:
            raise ValueError("text must not be empty")
        return self._provider.embed(t)