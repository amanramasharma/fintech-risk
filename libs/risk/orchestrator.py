from pydantic import BaseModel
from libs.risk.decisioning.engine import DecisionEngine
from libs.risk.decisioning.evidence import Evidence
from libs.risk.decisioning.provenance import DecisionProvenance
from libs.risk.decisioning.reasons import ReasonCode
from libs.risk.decisioning.types import RiskDecision
from libs.risk.fraud.engine import FraudEngine
from libs.risk.fraud.schema import FraudFeatureVector
from libs.risk.text.engine import TextRiskEngine
from libs.risk.text.schema import TextCase

class RiskRequest(BaseModel):
    fraud: FraudFeatureVector | None = None
    text: TextCase | None = None

class RiskOrchestrator:
    def __init__(self, decision_engine: DecisionEngine, fraud_engine: FraudEngine, text_engine: TextRiskEngine):
        self.decision_engine = decision_engine
        self.fraud_engine = fraud_engine
        self.text_engine = text_engine

    def score(self, req: RiskRequest) -> RiskDecision:
        reasons: list[ReasonCode] = []
        evidence: list[Evidence] = []
        prov: list[DecisionProvenance] = []
        base_scores: list[float] = []

        if req.fraud is not None:
            fs = self.fraud_engine.detect(req.fraud)
            base_scores.append(fs.base_score)
            reasons.extend(fs.reasons)
            evidence.extend(fs.evidence)
            prov.append(fs.provenance)

        if req.text is not None:
            ts = self.text_engine.detect(req.text)
            base_scores.append(ts.base_score)
            reasons.extend(ts.reasons)
            evidence.extend(ts.evidence)
            prov.append(ts.provenance)

        base = float(max(base_scores)) if base_scores else 0.0
        meta = {"provenance":[p.model_dump() for p in prov],"inputs_present":{"fraud":req.fraud is not None,"text":req.text is not None},}

        return self.decision_engine.decide(base_score=base,reasons=reasons,evidence=evidence,provenance=DecisionProvenance(engine="risk_orchestrator",model_name="multi_engine",model_version="v1",prompt_version=None,),metadata=meta,)