import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from libs.ml.fraud.calibration import fit_isotonic, fit_platt, save_calibrator
from libs.ml.fraud.vectorizer import DEFAULT_SPEC, extract_labels, vectorize_dataframe
import joblib


def _read_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p)


def _parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--val-csv", type=str, required=True)
    ap.add_argument("--artifacts-dir", type=str, required=True)
    ap.add_argument("--method", type=str, default="platt", choices=["platt","isotonic"])
    ap.add_argument("--model-type", type=str, default="iforest", choices=["iforest","xgb","logreg","lgbm"])
    return ap.parse_args()


def main():
    a = _parse()
    artifacts = Path(a.artifacts_dir)
    model = joblib.load(artifacts / "model.joblib")

    df = _read_csv(Path(a.val_csv))
    y = extract_labels(df)
    if y is None:
        raise RuntimeError("val csv must contain label column 'label_is_anomaly' (or modify extract_labels)")

    X = vectorize_dataframe(df, spec=DEFAULT_SPEC).astype("float32")

    if a.model_type in ("xgb","logreg","lgbm"):
        raw = model.predict_proba(X)[:,1].astype("float32")
        raw01 = raw
    else:
        raw = (-model.score_samples(X)).astype("float32")
        lo = float(np.percentile(raw, 1)); hi = float(np.percentile(raw, 99))
        hi = hi if hi > lo else lo + 1e-6
        raw01 = np.clip((raw - lo) / (hi - lo), 0.0, 1.0).astype("float32")

        m = artifacts / "metrics.json"
        metrics = {}
        if m.exists():
            metrics = json.loads(m.read_text(encoding="utf-8"))
        metrics["calibration"] = {"p01": lo, "p99": hi}
        m.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    bundle = fit_platt(raw01, y) if a.method == "platt" else fit_isotonic(raw01, y)
    save_calibrator(bundle, artifacts / "calibrator.joblib")

    (artifacts / "model_type.json").write_text(json.dumps({"type": a.model_type}, indent=2), encoding="utf-8")
    print(json.dumps({"artifacts_dir": str(artifacts), "method": a.method, "model_type": a.model_type}, indent=2))


if __name__ == "__main__":
    main()