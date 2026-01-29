from pydantic import BaseModel,Field
from typing import Any

class Evidence(BaseModel):
    source: str
    description: str
    value: Any | None = None
    threshold: Any | None = None
    metadata: dict[str,Any] = Field(default_factory=dict)