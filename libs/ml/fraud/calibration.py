from dataclasses import dataclass
from typing import Literal
import joblib
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


Method = Literal["platt","isotonic"]


@dataclass(frozen=True)
class CalibratorBundle:
    method: Method
    model: object


def fit_platt(x: np.ndarray, y: np.ndarray) -> CalibratorBundle:
    x = x.reshape(-1,1).astype("float32")
    y = y.astype("int64")
    lr = LogisticRegression(solver="lbfgs", max_iter=2000)
    lr.fit(x, y)
    return CalibratorBundle(method="platt", model=lr)


def fit_isotonic(x: np.ndarray, y: np.ndarray) -> CalibratorBundle:
    x = x.reshape(-1).astype("float32")
    y = y.astype("int64")
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(x, y)
    return CalibratorBundle(method="isotonic", model=iso)


def calibrate(bundle: CalibratorBundle, x: np.ndarray) -> np.ndarray:
    if bundle.method == "platt":
        X = x.reshape(-1,1).astype("float32")
        p = bundle.model.predict_proba(X)[:,1]
        return p.astype("float32")
    X = x.reshape(-1).astype("float32")
    p = bundle.model.predict(X)
    return np.clip(p, 0.0, 1.0).astype("float32")


def save_calibrator(bundle: CalibratorBundle, path):
    joblib.dump({"method": bundle.method, "model": bundle.model}, path)


def load_calibrator(path) -> CalibratorBundle:
    raw = joblib.load(path)
    return CalibratorBundle(method=raw["method"], model=raw["model"])