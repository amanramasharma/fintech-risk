from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class VectorizerSpec:
    numeric_cols: tuple[str, ...]
    categorical_cols: tuple[str, ...]
    onehot_categories: dict[str, tuple[str, ...]]


DEFAULT_SPEC = VectorizerSpec(numeric_cols=("txn_amount","txns_1h","txns_24h",
        "avg_txn_amount_30d","account_age_days","device_change_7d","failed_logins_24h",),
    categorical_cols=("txn_currency", "txn_country"),
    onehot_categories={"txn_currency": ("GBP", "EUR", "USD"),"txn_country": ("GB", "IE", "FR", "DE", "US"),},)

def _ensure_columns(df: pd.DataFrame, cols: tuple[str, ...]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def _one_hot(df: pd.DataFrame, col: str, categories: tuple[str, ...]) -> np.ndarray:
    values = df[col].astype(str).to_numpy()
    out = np.zeros((len(values), len(categories)), dtype=np.float32)
    idx = {cat: i for i, cat in enumerate(categories)}
    for row_i, v in enumerate(values):
        j = idx.get(v)
        if j is not None:
            out[row_i, j] = 1.0
    return out


def vectorize_dataframe(df: pd.DataFrame, spec: VectorizerSpec = DEFAULT_SPEC) -> np.ndarray:
    _ensure_columns(df, spec.numeric_cols + spec.categorical_cols)
    num = df.loc[:, list(spec.numeric_cols)].astype("float32").to_numpy()
    cat_blocks = []
    for c in spec.categorical_cols:
        cats = spec.onehot_categories[c]
        cat_blocks.append(_one_hot(df, c, cats))
    if cat_blocks:
        X = np.concatenate([num] + cat_blocks, axis=1)
    else:
        X = num
    return X


def extract_labels(df: pd.DataFrame, label_col: str = "label_is_anomaly") -> np.ndarray | None:
    if label_col not in df.columns:
        return None
    return df[label_col].astype("int64").to_numpy()


def vectorize_single(sample: dict[str, Any], spec: VectorizerSpec = DEFAULT_SPEC) -> np.ndarray:
    df = pd.DataFrame([sample])
    return vectorize_dataframe(df, spec=spec)