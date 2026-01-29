import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import numpy as np
import pandas as pd


Currency = Literal["GBP", "EUR", "USD"]
Country = Literal["GB", "IE", "FR", "DE", "US"]


@dataclass(frozen=True)
class GeneratorConfig:
    seed: int
    n_customers: int
    n_txns: int
    fraud_rate: float
    out_dir: Path

    split_train: float
    split_val: float
    split_test: float


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)

def _choice(r: np.random.Generator, items, p=None):
    return items[int(r.choice(len(items), p=p))]

def _lognormal_amount(r: np.random.Generator, mu: float, sigma: float) -> float:
    return float(r.lognormal(mean=mu, sigma=sigma))

def _clip_int(x: float, lo: int = 0, hi: int = 10_000) -> int:
    return int(max(lo, min(hi, round(x))))

def _clip_float(x: float, lo: float = 0.0, hi: float = 1e9) -> float:
    return float(max(lo, min(hi, x)))

def _make_customers(r: np.random.Generator, n_customers: int) -> pd.DataFrame:
    currencies: list[Currency] = ["GBP", "EUR", "USD"]
    countries: list[Country] = ["GB", "IE", "FR", "DE", "US"]
    rows = []
    for cid in range(n_customers):
        home_country = _choice(r, countries, p=[0.65, 0.08, 0.09, 0.10, 0.08])
        currency = "GBP" if home_country == "GB" else _choice(r, currencies, p=[0.35, 0.35, 0.30])
        acct_age = _clip_int(r.gamma(shape=2.0, scale=180.0), lo=1, hi=3650)
        spend_mu = 3.2 + (0.15 if currency == "GBP" else 0.0)
        spend_sigma = 0.55 + (0.10 if acct_age < 30 else 0.0)
        avg_30d = _clip_float(_lognormal_amount(r, spend_mu, spend_sigma), lo=5.0, hi=5000.0)
        base_txns_1h = _clip_int(r.poisson(lam=0.25), lo=0, hi=10)
        base_txns_24h = _clip_int(base_txns_1h + r.poisson(lam=1.2), lo=0, hi=40)
        rows.append({"customer_id": f"c{cid:07d}",
                "home_country": home_country,
                "default_currency": currency,
                "account_age_days": acct_age,
                "avg_txn_amount_30d": avg_30d,
                "baseline_txns_1h": base_txns_1h,
                "baseline_txns_24h": base_txns_24h,})
    return pd.DataFrame(rows)

def _fraud_propensity(r: np.random.Generator, cust: dict) -> float:
    age = cust["account_age_days"]
    avg_30d = cust["avg_txn_amount_30d"]
    p = 0.002
    if age < 14:
        p += 0.020
    elif age < 60:
        p += 0.006
    if avg_30d < 20:
        p += 0.004
    p += float(r.normal(0.0, 0.002))
    return float(max(0.0005, min(0.15, p)))


def _generate_normal_txn(r: np.random.Generator, cust: dict) -> dict:
    txn_country = cust["home_country"] if r.random() < 0.92 else _choice(r, ["GB", "IE", "FR", "DE", "US"])
    txn_currency = cust["default_currency"]
    avg_30d = float(cust["avg_txn_amount_30d"])
    amount = _clip_float(_lognormal_amount(r, np.log(max(10.0, avg_30d)) - 0.4, 0.55), lo=0.5, hi=20_000.0)
    txns_1h = _clip_int(cust["baseline_txns_1h"] + r.poisson(lam=0.15), lo=0, hi=20)
    txns_24h = _clip_int(max(txns_1h, cust["baseline_txns_24h"] + r.poisson(lam=0.8)), lo=0, hi=60)
    device_change_7d = _clip_int(r.poisson(lam=0.05), lo=0, hi=6)
    failed_logins_24h = _clip_int(r.poisson(lam=0.08), lo=0, hi=20)
    return {"txn_amount": float(amount),
        "txn_currency": str(txn_currency),
        "txn_country": str(txn_country),
        "txns_1h": int(txns_1h),
        "txns_24h": int(txns_24h),
        "avg_txn_amount_30d": float(avg_30d),
        "account_age_days": int(cust["account_age_days"]),
        "device_change_7d": int(device_change_7d),
        "failed_logins_24h": int(failed_logins_24h),
        "label_is_anomaly": 0,
        "anomaly_type": "none",}


def _generate_anomalous_txn(r: np.random.Generator, cust: dict) -> dict:
    base = _generate_normal_txn(r, cust)
    avg_30d = float(base["avg_txn_amount_30d"])

    anomaly_type = _choice(r,
        ["velocity_burst", "amount_spike", "account_takeover", "geo_shift", "mixed"],
        p=[0.30, 0.25, 0.25, 0.10, 0.10],)

    if anomaly_type in ("velocity_burst", "mixed"):
        base["txns_1h"] = _clip_int(base["txns_1h"] + r.integers(6, 25), lo=0, hi=200)
        base["txns_24h"] = _clip_int(max(base["txns_24h"], base["txns_1h"] + r.integers(5, 60)), lo=0, hi=500)

    if anomaly_type in ("amount_spike", "mixed"):
        spike = _clip_float(_lognormal_amount(r, mu=np.log(max(30.0, avg_30d)) + 1.5, sigma=0.7), lo=50.0, hi=100_000.0)
        base["txn_amount"] = float(spike)

    if anomaly_type in ("account_takeover", "mixed"):
        base["failed_logins_24h"] = _clip_int(base["failed_logins_24h"] + r.integers(5, 40), lo=0, hi=500)
        base["device_change_7d"] = _clip_int(base["device_change_7d"] + r.integers(1, 6), lo=0, hi=50)

    if anomaly_type in ("geo_shift", "mixed"):
        foreign = _choice(r, ["GB", "IE", "FR", "DE", "US"])
        if foreign == cust["home_country"]:
            foreign = _choice(r, ["GB", "IE", "FR", "DE", "US"])
        base["txn_country"] = str(foreign)

    base["label_is_anomaly"] = 1
    base["anomaly_type"] = anomaly_type
    return base


def generate_dataset(cfg: GeneratorConfig) -> pd.DataFrame:
    r = _rng(cfg.seed)
    customers = _make_customers(r, cfg.n_customers)
    cust_rows = customers.to_dict(orient="records")

    rows = []
    for i in range(cfg.n_txns):
        cust = cust_rows[int(r.integers(0, len(cust_rows)))]
        p = max(cfg.fraud_rate, _fraud_propensity(r, cust))
        is_anom = 1 if r.random() < p else 0
        row = _generate_anomalous_txn(r, cust) if is_anom else _generate_normal_txn(r, cust)
        row["customer_id"] = cust["customer_id"]
        row["txn_id"] = f"t{i:09d}"
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sample(frac=1.0, random_state=cfg.seed).reset_index(drop=True)
    return df


def split_and_write(df: pd.DataFrame, cfg: GeneratorConfig) -> None:
    n = len(df)
    n_train = int(n * cfg.split_train)
    n_val = int(n * cfg.split_val)
    n_test = n - n_train - n_val

    out = cfg.out_dir
    out.mkdir(parents=True, exist_ok=True)

    train = df.iloc[:n_train].copy()
    val = df.iloc[n_train : n_train + n_val].copy()
    test = df.iloc[n_train + n_val :].copy()

    train.to_csv(out / "train.csv", index=False)
    val.to_csv(out / "val.csv", index=False)
    test.to_csv(out / "test.csv", index=False)

    meta = {
        "seed": cfg.seed,
        "n_customers": cfg.n_customers,
        "n_txns": cfg.n_txns,
        "fraud_rate_target": cfg.fraud_rate,
        "splits": {"train": len(train), "val": len(val), "test": len(test)},
        "anomaly_rate_actual": float(df["label_is_anomaly"].mean()),
    }
    (out / "meta.json").write_text(pd.Series(meta).to_json(), encoding="utf-8")


def _parse_args() -> GeneratorConfig:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n-customers", type=int, default=25_000)
    ap.add_argument("--n-txns", type=int, default=250_000)
    ap.add_argument("--fraud-rate", type=float, default=0.01)
    ap.add_argument("--out-dir", type=str, default="synthetic_data/fraud/out")

    ap.add_argument("--split-train", type=float, default=0.80)
    ap.add_argument("--split-val", type=float, default=0.10)
    ap.add_argument("--split-test", type=float, default=0.10)

    args = ap.parse_args()

    s = args.split_train + args.split_val + args.split_test
    if abs(s - 1.0) > 1e-9:
        raise ValueError("splits must sum to 1.0")

    return GeneratorConfig(
        seed=args.seed,
        n_customers=args.n_customers,
        n_txns=args.n_txns,
        fraud_rate=args.fraud_rate,
        out_dir=Path(args.out_dir),
        split_train=args.split_train,
        split_val=args.split_val,
        split_test=args.split_test,
    )


def main():
    cfg = _parse_args()
    df = generate_dataset(cfg)
    split_and_write(df, cfg)


if __name__ == "__main__":
    main()