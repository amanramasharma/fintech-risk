import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score
from libs.ml.fraud.vectorizer import DEFAULT_SPEC, extract_labels, vectorize_dataframe


@dataclass(frozen=True)
class TrainConfig:
    train_csv: Path
    val_csv: Path | None
    out_dir: Path
    seed: int
    n_estimators: int
    contamination: float
    max_samples: int


def _read_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p)


def _fit_iforest(X: np.ndarray, cfg: TrainConfig) -> IsolationForest:
    model = IsolationForest(n_estimators=cfg.n_estimators,
        contamination=cfg.contamination,max_samples=cfg.max_samples,
        random_state=cfg.seed,n_jobs=-1,)
    model.fit(X)
    return model

def _iforest_scores(model: IsolationForest, X: np.ndarray) -> np.ndarray:
    raw = -model.score_samples(X)
    raw = raw.astype("float32")
    lo = float(np.percentile(raw, 1))
    hi = float(np.percentile(raw, 99))
    hi = hi if hi > lo else lo + 1e-6
    scaled = (raw - lo) / (hi - lo)
    return np.clip(scaled, 0.0, 1.0)

def _metrics(y_true: np.ndarray, y_score: np.ndarray) -> dict:
    return {"roc_auc": float(roc_auc_score(y_true, y_score)),
        "pr_auc": float(average_precision_score(y_true, y_score)),
        "base_rate": float(y_true.mean()),}


def train(cfg: TrainConfig) -> dict:
    train_df = _read_csv(cfg.train_csv)
    X_train = vectorize_dataframe(train_df, spec=DEFAULT_SPEC)
    model = _fit_iforest(X_train, cfg)
    artifacts = cfg.out_dir
    artifacts.mkdir(parents=True, exist_ok=True)
    metrics = {"train": {"n": int(len(train_df))}}
    if cfg.val_csv:
        val_df = _read_csv(cfg.val_csv)
        X_val = vectorize_dataframe(val_df, spec=DEFAULT_SPEC)
        y_val = extract_labels(val_df)
        if y_val is not None:
            raw = -model.score_samples(X_val).astype("float32")
            metrics["calibration"] = {"p01": float(np.percentile(raw,1)), "p99": float(np.percentile(raw,99))}
            scores = _iforest_scores(model, X_val)
            metrics["val"] = {"n": int(len(val_df)), **_metrics(y_val, scores)}
        else:
            metrics["val"] = {"n": int(len(val_df)), "note": "labels not present"}
    joblib.dump(model, artifacts / "model.joblib")
    (artifacts / "vectorizer_spec.json").write_text(json.dumps(DEFAULT_SPEC.__dict__, indent=2), encoding="utf-8")
    (artifacts / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return {"artifacts_dir": str(artifacts), "metrics": metrics}

def _parse_args() -> TrainConfig:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-csv", type=str, required=True)
    ap.add_argument("--val-csv", type=str, default=None)
    ap.add_argument("--out-dir", type=str, default="artifacts/fraud_iforest")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n-estimators", type=int, default=300)
    ap.add_argument("--contamination", type=float, default=0.01)
    ap.add_argument("--max-samples", type=int, default=256)
    args = ap.parse_args()

    return TrainConfig(train_csv=Path(args.train_csv),
        val_csv=Path(args.val_csv) if args.val_csv else None,
        out_dir=Path(args.out_dir),
        seed=args.seed,
        n_estimators=args.n_estimators,
        contamination=args.contamination,
        max_samples=args.max_samples,)

def main():
    cfg = _parse_args()
    out = train(cfg)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()