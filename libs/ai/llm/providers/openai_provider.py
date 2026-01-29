from dataclasses import dataclass
import httpx

from libs.ai.llm.gateway import LLMResult


@dataclass(frozen=True)
class OpenAIChatConfig:
    api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    timeout_seconds: int = 30


class OpenAIChatProvider:
    def __init__(self, cfg: OpenAIChatConfig):
        self.cfg = cfg

    def generate(self, prompt: str) -> LLMResult:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.cfg.api_key}"}

        payload = {
            "model": self.cfg.model,
            "temperature": float(self.cfg.temperature),
            "messages": [{"role": "user", "content": prompt}],
        }

        with httpx.Client(timeout=self.cfg.timeout_seconds) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()

        text = (data["choices"][0]["message"]["content"] or "").strip()
        return LLMResult(model=self.cfg.model, text=text)