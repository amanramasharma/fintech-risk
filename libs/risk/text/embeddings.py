from dataclasses import dataclass

from libs.ai.embeddings.gateway import EmbeddingResult, EmbeddingsGateway


@dataclass(frozen=True)
class TextEmbeddingsClient:
    gateway: EmbeddingsGateway

    def embed(self, text: str) -> EmbeddingResult:
        return self.gateway.embed(text)