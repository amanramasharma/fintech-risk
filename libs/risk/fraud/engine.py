from pydantic import BaseModel
from libs.ml.fraud.explain import contributions_to_reasons_and_evidence,top_contributions
from libs.ml.fraud.vectorizer import vectorize_single
from libs.risk.decisioning.evidence import Evidence
from libs.risk.decisioning.provenance import DecisionProvenance
from libs.risk.decisioning.reasons import ReasonCode
from libs.risk.fraud.schema import FraudFeatureVector
from libs.risk.fraud.scorer import FraudScorer,FraudScoreOutput

class FraudSignals(BaseModel):
    base_score: float
    reasons: list[ReasonCode]
    evidence: list[Evidence]
    provenance: DecisionProvenance
    raw: FraudScoreOutput

class FraudEngine:
    def __init__(self, scorer: FraudScorer):
        self.scorer = scorer

    def detect(self, raw: FraudFeatureVector) -> FraudSignals:
        out = self.scorer.score(raw)
        sample = raw.model_dump()
        X = vectorize_single(sample,spec=self.scorer.spec)

        spec = self.scorer.spec
        feature_names: list[str] = list(spec.numeric_cols)
        for c in spec.categorical_cols:
            for cat in spec.onehot_categories[c]:
                feature_names.append(f"{c}={cat}")

        contribs = top_contributions(feature_names=feature_names,x=X,baseline=None,k=3)
        reasons,evidence = contributions_to_reasons_and_evidence(contribs,raw_input=sample)

        prov = DecisionProvenance(engine="fraud_engine",model_name=self.scorer.bundle.ref.name,model_version=self.scorer.bundle.ref.version,prompt_version=None,)
        return FraudSignals(base_score=float(out.score),reasons=reasons,evidence=evidence,provenance=prov,raw=out,)