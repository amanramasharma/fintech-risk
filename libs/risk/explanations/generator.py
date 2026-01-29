from dataclasses import dataclass

from libs.ai.llm.gateway import LLMGateway
from libs.ai.llm.prompts import EXPLAIN_DECISION_V1
from libs.risk.decisioning.types import RiskDecision


@dataclass(frozen=True)
class ExplanationOutput:
    prompt_version: str
    text: str


class ExplanationGenerator:
    def __init__(self, llm: LLMGateway):
        self.llm = llm

    def generate(self, *, decision: RiskDecision, taxonomy=None) -> ExplanationOutput:
        reasons = (
            "\n".join(f"- {r.value}" for r in decision.reasons)
            if decision.reasons
            else "- no explicit risk drivers detected"
        )

        evidence = (
            "\n".join(
                f"- {e.source}: {e.description} ({e.value})"
                for e in decision.evidence
            )
            if decision.evidence
            else "- no supporting evidence available"
        )

        risk_band = decision.metadata.get("risk_band", "unknown")
        severity = decision.metadata.get("severity", "n/a")

        prompt = EXPLAIN_DECISION_V1.render(
            risk_category=str(decision.risk_category),
            risk_score=f"{float(decision.risk_score):.2f}",
            risk_band=risk_band,
            severity=str(severity),
            reasons=reasons,
            evidence=evidence,
        )

        out = self.llm.generate(prompt)

        return ExplanationOutput(
            prompt_version=EXPLAIN_DECISION_V1.version,
            text=out.text.strip(),
        )