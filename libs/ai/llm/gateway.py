from dataclasses import dataclass
from pydantic import BaseModel, Field


class LLMResult(BaseModel):
    model: str
    text: str = Field(..., min_length=1)


@dataclass(frozen=True)
class LLMGatewayConfig:
    provider: str
    model: str
    timeout_seconds: int = 30


class LLMGateway:
    def __init__(self, cfg: LLMGatewayConfig, provider):
        self.cfg = cfg
        self._provider = provider

    def generate(self, prompt: str) -> LLMResult:
        p = prompt.strip()
        if not p:
            raise ValueError("prompt must not be empty")
        return self._provider.generate(p)