import numpy as np
from pydantic import BaseModel, Field

from libs.ml.fraud.loader import FraudModelBundle
from libs.ml.fraud.vectorizer import vectorize_single
from libs.ml.fraud.calibration import calibrate
from libs.risk.fraud.schema import FraudFeatureVector
from libs.risk.fraud.features import FraudDerivedFeatures, derive_features


def _scale_to_unit(x: float, lo: float, hi: float) -> float:
    hi = hi if hi > lo else lo + 1e-6
    return float(max(0.0, min(1.0, (x - lo) / (hi - lo))))


class FraudScoreOutput(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    raw_score: float = Field(..., ge=0.0)
    derived: FraudDerivedFeatures
    model_type: str


class FraudScorer:
    def __init__(self, bundle: FraudModelBundle):
        self.bundle = bundle
        self.model = bundle.model
        self.spec = bundle.vectorizer_spec

        m = bundle.artifacts_dir / "metrics.json"
        self._lo = 0.0
        self._hi = 1.0
        if m.exists():
            import json
            raw = json.loads(m.read_text(encoding="utf-8"))
            lo = raw.get("calibration", {}).get("p01")
            hi = raw.get("calibration", {}).get("p99")
            if isinstance(lo,(int,float)) and isinstance(hi,(int,float)):
                self._lo = float(lo); self._hi = float(hi)

    def _raw_iforest(self, X: np.ndarray) -> float:
        s = -self.model.score_samples(X)[0]
        return float(max(0.0, s))

    def _raw_proba(self, X: np.ndarray) -> float:
        p = self.model.predict_proba(X)[0][1]
        return float(max(0.0, min(1.0, p)))

    def score(self, raw: FraudFeatureVector) -> FraudScoreOutput:
        derived = derive_features(raw)
        X = vectorize_single(raw.model_dump(), spec=self.spec).astype("float32")

        if self.bundle.model_type in ("xgb","logreg","lgbm"):
            base_raw = self._raw_proba(X)
            raw01 = base_raw
        else:
            base_raw = self._raw_iforest(X)
            raw01 = _scale_to_unit(base_raw, self._lo, self._hi)

        if self.bundle.calibrator is not None:
            cal = calibrate(self.bundle.calibrator, np.array([raw01], dtype="float32"))[0]
            score01 = float(cal)
        else:
            score01 = float(raw01)

        return FraudScoreOutput(score=score01, raw_score=float(raw01), derived=derived, model_type=self.bundle.model_type)