from libs.audit.writer import AuditWriter, AuditWriteResult
from libs.risk.decisioning.types import RiskDecision

class NoopAuditWriter(AuditWriter):
    def write(self, decision: RiskDecision, raw_input: dict) -> AuditWriteResult:
        return AuditWriteResult(audit_id="noop")