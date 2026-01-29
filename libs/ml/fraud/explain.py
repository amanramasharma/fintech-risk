from dataclasses import dataclass
from typing import Any

import numpy as np

from libs.risk.decisioning.reasons import ReasonCode
from libs.risk.decisioning.evidence import Evidence


@dataclass(frozen=True)
class Contribution:
    feature: str
    weight: float
    value: float | None = None
    baseline: float | None = None


FEATURE_TO_REASON: dict[str, ReasonCode] = {
    "txns_1h": ReasonCode.HIGH_TRANSACTION_VELOCITY,
    "txns_24h": ReasonCode.HIGH_TRANSACTION_VELOCITY,
    "txn_amount": ReasonCode.UNUSUAL_AMOUNT,
    "avg_txn_amount_30d": ReasonCode.UNUSUAL_AMOUNT,
    "failed_logins_24h": ReasonCode.ACCOUNT_BEHAVIOR_CHANGE,
    "device_change_7d": ReasonCode.ACCOUNT_BEHAVIOR_CHANGE,
    "txn_country": ReasonCode.ACCOUNT_BEHAVIOR_CHANGE,
}


def top_contributions(
    feature_names: list[str],
    x: np.ndarray,
    baseline: np.ndarray | None = None,
    k: int = 3,
) -> list[Contribution]:
    x1 = x.reshape(-1).astype("float32")
    if baseline is None:
        b1 = np.zeros_like(x1)
    else:
        b1 = baseline.reshape(-1).astype("float32")

    weights = np.abs(x1 - b1)
    idx = np.argsort(weights)[::-1][:k]

    out: list[Contribution] = []
    for i in idx:
        out.append(
            Contribution(
                feature=feature_names[i],
                weight=float(weights[i]),
                value=float(x1[i]),
                baseline=float(b1[i]),
            )
        )
    return out


def contributions_to_reasons_and_evidence(
    contribs: list[Contribution],
    raw_input: dict[str, Any],
) -> tuple[list[ReasonCode], list[Evidence]]:
    reasons: list[ReasonCode] = []
    evidence: list[Evidence] = []

    for c in contribs:
        base_feature = c.feature.split("=")[0]
        reason = FEATURE_TO_REASON.get(base_feature)
        if not reason:
            continue

        reasons.append(reason)

        evidence.append(
            Evidence(
                source="fraud.explain",
                description=f"Top contributing feature: {base_feature}",
                value={"feature": base_feature, "value": raw_input.get(base_feature), "weight": c.weight},
                threshold=None,
                metadata={"baseline": c.baseline, "model_explanation": "abs(x-baseline)"},
            )
        )

    seen = set()
    dedup = []
    for r in reasons:
        if r.value not in seen:
            seen.add(r.value)
            dedup.append(r)
    return dedup, evidence