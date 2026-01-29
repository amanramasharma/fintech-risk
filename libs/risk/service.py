from dataclasses import dataclass

from libs.audit.writer import AuditWriteResult, AuditWriter
from libs.risk.decisioning.types import RiskDecision
from libs.risk.orchestrator import RiskOrchestrator, RiskRequest
from libs.risk.explanations.generator import ExplanationOutput


@dataclass(frozen=True)
class RiskServiceResult:
    decision: RiskDecision
    audit: AuditWriteResult
    explanation: ExplanationOutput | None = None


class RiskService:
    def __init__(self, orchestrator, audit_writer, explainer=None):
        self.orchestrator = orchestrator
        self.audit_writer = audit_writer
        self.explainer = explainer

    def score(self, req: RiskRequest, *, explain: bool = False) -> RiskServiceResult:
        decision = self.orchestrator.score(req)

        explanation = None
        if explain and self.explainer:
            try:
                explanation = self.explainer.generate(
                    decision=decision,
                    taxonomy=self.orchestrator.decision_engine.taxonomy,
                )
            except Exception:
                explanation = None

        audit = self.audit_writer.write(decision=decision, raw_input=req.model_dump())

        return RiskServiceResult(decision=decision, audit=audit, explanation=explanation)