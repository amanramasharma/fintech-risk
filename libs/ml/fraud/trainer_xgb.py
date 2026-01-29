import argparse, json
from dataclasses import dataclass
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from libs.ml.fraud.vectorizer import DEFAULT_SPEC, extract_labels, vectorize_dataframe

try:
    from xgboost import XGBClassifier
except Exception as e:
    raise RuntimeError("missing dependency: xgboost. Add `xgboost` to pyproject.toml") from e


@dataclass(frozen=True)
class TrainConfig:
    train_csv: Path
    val_csv: Path | None
    out_dir: Path
    seed: int
    n_estimators: int
    max_depth: int
    learning_rate: float
    subsample: float
    colsample_bytree: float
    reg_lambda: float
    pos_weight: float
    label_col: str


def _read_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p)


def _metrics(y_true: np.ndarray, y_score: np.ndarray) -> dict:
    return {"roc_auc": float(roc_auc_score(y_true, y_score)),"pr_auc": float(average_precision_score(y_true, y_score)),
        "base_rate": float(y_true.mean()),}

def train(cfg: TrainConfig) -> dict:
    df = _read_csv(cfg.train_csv)
    y = extract_labels(df, label_col=cfg.label_col)
    if y is None:
        raise RuntimeError(f"label column not found: {cfg.label_col}")

    X = vectorize_dataframe(df, spec=DEFAULT_SPEC).astype("float32")
    model = XGBClassifier(n_estimators=cfg.n_estimators,
        max_depth=cfg.max_depth,
        learning_rate=cfg.learning_rate,
        subsample=cfg.subsample,
        colsample_bytree=cfg.colsample_bytree,
        reg_lambda=cfg.reg_lambda,
        scale_pos_weight=cfg.pos_weight,
        random_state=cfg.seed,
        n_jobs=-1,
        eval_metric="logloss",)
    model.fit(X, y)
    metrics = {"train": {"n": int(len(df))}}
    if cfg.val_csv:
        vdf = _read_csv(cfg.val_csv)
        vy = extract_labels(vdf, label_col=cfg.label_col)
        if vy is not None:
            Xv = vectorize_dataframe(vdf, spec=DEFAULT_SPEC).astype("float32")
            p = model.predict_proba(Xv)[:, 1].astype("float32")
            metrics["val"] = {"n": int(len(vdf)), **_metrics(vy, p)}
        else:
            metrics["val"] = {"n": int(len(vdf)), "note": "labels not present"}

    out = cfg.out_dir
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out / "model.joblib")
    (out / "vectorizer_spec.json").write_text(json.dumps(DEFAULT_SPEC.__dict__, indent=2), encoding="utf-8")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out / "model_type.json").write_text(json.dumps({"type": "xgb_classifier"}, indent=2), encoding="utf-8")
    return {"artifacts_dir": str(out), "metrics": metrics}


def _parse_args() -> TrainConfig:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-csv", type=str, required=True)
    ap.add_argument("--val-csv", type=str, default=None)
    ap.add_argument("--out-dir", type=str, default="artifacts/fraud_xgb")
    ap.add_argument("--seed", type=int, default=7)

    ap.add_argument("--n-estimators", type=int, default=500)
    ap.add_argument("--max-depth", type=int, default=5)
    ap.add_argument("--learning-rate", type=float, default=0.05)
    ap.add_argument("--subsample", type=float, default=0.9)
    ap.add_argument("--colsample-bytree", type=float, default=0.9)
    ap.add_argument("--reg-lambda", type=float, default=1.0)

    ap.add_argument("--pos-weight", type=float, default=20.0)
    ap.add_argument("--label-col", type=str, default="label_is_anomaly")

    a = ap.parse_args()
    return TrainConfig(
        train_csv=Path(a.train_csv),
        val_csv=Path(a.val_csv) if a.val_csv else None,
        out_dir=Path(a.out_dir),
        seed=a.seed,
        n_estimators=a.n_estimators,
        max_depth=a.max_depth,
        learning_rate=a.learning_rate,
        subsample=a.subsample,
        colsample_bytree=a.colsample_bytree,
        reg_lambda=a.reg_lambda,
        pos_weight=a.pos_weight,
        label_col=a.label_col,)

def main():
    cfg = _parse_args()
    print(json.dumps(train(cfg), indent=2))

if __name__ == "__main__":
    main()