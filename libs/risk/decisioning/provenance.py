from pydantic import BaseModel


class DecisionProvenance(BaseModel):
    engine: str
    model_name: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None