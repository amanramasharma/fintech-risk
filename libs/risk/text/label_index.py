import json
from dataclasses import dataclass
from pathlib import Path
from libs.ai.embeddings.gateway import EmbeddingsGateway

@dataclass(frozen=True)
class LabelIndex:
    model: str
    vectors: dict[str,list[float]]

def build_label_index(gateway: EmbeddingsGateway, labels: list[str]) -> LabelIndex:
    vecs: dict[str,list[float]] = {}
    for lab in labels:
        vecs[lab] = gateway.embed(lab).vector
    return LabelIndex(model=gateway.cfg.model,vectors=vecs)

def save_label_index(idx: LabelIndex, path: Path) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({"model":idx.model,"vectors":idx.vectors},ensure_ascii=False),encoding="utf-8")

def load_label_index(path: Path) -> LabelIndex:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return LabelIndex(model=raw["model"],vectors=raw["vectors"])