from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelRef:
    name: str
    version: str

class ModelRegistry(ABC):
    @abstractmethod
    def save(self, ref: ModelRef, artifacts_dir: Path) -> None:
        ...
    @abstractmethod
    def load(self, ref: ModelRef, dest_dir: Path) -> Path:
        ...