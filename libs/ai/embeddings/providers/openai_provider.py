from dataclasses import dataclass

from openai import OpenAI

from libs.ai.embeddings.gateway import EmbeddingResult, EmbeddingsProvider


@dataclass(frozen=True)
class OpenAIEmbeddingsConfig:
    api_key: str
    model: str


class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self, cfg: OpenAIEmbeddingsConfig):
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.api_key)

    def embed(self, text: str) -> EmbeddingResult:
        resp = self.client.embeddings.create(
            model=self.cfg.model,
            input=text,
        )
        vec = resp.data[0].embedding
        return EmbeddingResult(model=self.cfg.model, vector=list(vec))