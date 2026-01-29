import json
from dataclasses import dataclass
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest

from libs.ml.registry.interface import ModelRef, ModelRegistry
from libs.ml.fraud.vectorizer import VectorizerSpec
from libs.ml.fraud.calibration import CalibratorBundle, load_calibrator


@dataclass(frozen=True)
class FraudModelBundle:
    ref: ModelRef
    model: object
    vectorizer_spec: VectorizerSpec
    artifacts_dir: Path
    model_type: str
    calibrator: CalibratorBundle | None = None


def _load_vectorizer_spec(p: Path) -> VectorizerSpec:
    raw = json.loads(p.read_text(encoding="utf-8"))
    return VectorizerSpec(
        numeric_cols=tuple(raw["numeric_cols"]),
        categorical_cols=tuple(raw["categorical_cols"]),
        onehot_categories={k: tuple(v) for k,v in raw["onehot_categories"].items()},
    )


def _read_model_type(artifacts: Path) -> str:
    p = artifacts / "model_type.json"
    if not p.exists():
        return "iforest"
    raw = json.loads(p.read_text(encoding="utf-8"))
    t = raw.get("type")
    return str(t) if t else "iforest"


def load_fraud_model(registry: ModelRegistry, ref: ModelRef, cache_dir: Path = Path("/tmp/model_cache/fraud")) -> FraudModelBundle:
    artifacts = cache_dir / ref.name / ref.version
    registry.load(ref, artifacts)

    model = joblib.load(artifacts / "model.joblib")
    spec = _load_vectorizer_spec(artifacts / "vectorizer_spec.json")
    model_type = _read_model_type(artifacts)

    calibrator = None
    cp = artifacts / "calibrator.joblib"
    if cp.exists():
        calibrator = load_calibrator(cp)

    return FraudModelBundle(ref=ref, model=model, vectorizer_spec=spec, artifacts_dir=artifacts, model_type=model_type, calibrator=calibrator)