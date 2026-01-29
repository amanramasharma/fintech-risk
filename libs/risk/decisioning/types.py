from pydantic import BaseModel, Field
from typing import Any
from libs.risk.decisioning.reasons import ReasonCode
from libs.risk.decisioning.evidence import Evidence
from libs.risk.decisioning.provenance import DecisionProvenance

class RiskDecision(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_category: str
    reasons: list[ReasonCode] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    provenance: DecisionProvenance
    metadata: dict[str, Any] = Field(default_factory=dict)