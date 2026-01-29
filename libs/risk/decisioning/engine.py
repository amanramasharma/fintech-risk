from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from libs.risk.decisioning.evidence import Evidence
from libs.risk.decisioning.provenance import DecisionProvenance
from libs.risk.decisioning.reasons import ReasonCode
from libs.risk.decisioning.types import RiskDecision
from libs.risk.taxonomy.schema import TaxonomyConfig


@dataclass(frozen=True)
class _CategoryScore:
    category: str
    severity: float
    matched_reasons: list[str]
    matched_count: int
    score: float
    band: str


def _band_for(score: float, cfg) -> str:
    t = getattr(cfg, "thresholds", None)
    if not t:
        return "unknown"
    hi = float(getattr(t, "score_high", 0.85))
    med = float(getattr(t, "score_medium", 0.60))
    if score >= hi:
        return "high"
    if score >= med:
        return "medium"
    return "low"


def _should_no_risk(base_score: float, rs_set: set[str], candidates: list[_CategoryScore]) -> bool:
    if not candidates:
        return True
    if base_score < 0.60 and len(rs_set) <= 1:
        return True
    return False


class DecisionEngine:
    def __init__(self, taxonomy: TaxonomyConfig):
        self.taxonomy = taxonomy

    def decide(self,*,reasons: Iterable[ReasonCode],evidence: list[Evidence],base_score: float,provenance: DecisionProvenance,metadata: dict | None = None,) -> RiskDecision:
        rs = [r.value for r in reasons]
        rs_set = set(rs)
        candidates: list[_CategoryScore] = []
        for category, cfg in self.taxonomy.categories.items():
            if category == "no_risk":
                continue
            matched = [r for r in rs if r in cfg.reasons]
            if not matched:
                continue
            severity = float(cfg.severity)
            boost = min(0.10, 0.03 * len(set(matched)))
            score = float(min(1.0, (base_score * severity) + boost))
            band = _band_for(score, cfg)
            candidates.append(_CategoryScore(
                    category=category,
                    severity=severity,
                    matched_reasons=sorted(set(matched)),
                    matched_count=len(set(matched)),
                    score=score,
                    band=band,))

        if _should_no_risk(float(base_score), rs_set, candidates):
            final_category = "no_risk"
            final_score = float(min(1.0, max(0.0, base_score)))
            severity = 0.0
            risk_band = "low"
            per_category = [
                {
                    "category": "no_risk",
                    "score": final_score,
                    "band": "low",
                    "severity": 0.0,
                    "matched_count": len(rs_set),
                    "matched_reasons": sorted(rs_set),
                }
            ]
        else:
            best = max(candidates, key=lambda x: (x.score, x.severity, x.matched_count))

            final_category = best.category
            final_score = best.score
            severity = best.severity
            risk_band = best.band

            per_category = [
                {
                    "category": c.category,
                    "score": c.score,
                    "band": c.band,
                    "severity": c.severity,
                    "matched_count": c.matched_count,
                    "matched_reasons": c.matched_reasons,
                }
                for c in sorted(candidates, key=lambda x: x.score, reverse=True)]

        out_meta = dict(metadata or {})
        out_meta.update(
            {
                "risk_band": risk_band,
                "severity": severity,
                "base_score": float(base_score),
                "matched_reason_codes": sorted(rs_set),
                "per_category_scores": per_category,})

        return RiskDecision(risk_score=float(final_score),risk_category=final_category,reasons=[ReasonCode(r) for r in sorted(rs_set)],
            evidence=evidence,provenance=provenance,metadata=out_meta,)