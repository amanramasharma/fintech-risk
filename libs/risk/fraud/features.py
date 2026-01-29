from pydantic import BaseModel, Field


class FraudDerivedFeatures(BaseModel):
    velocity_1h: float = Field(..., ge=0.0)
    velocity_24h: float = Field(..., ge=0.0)
    amount_ratio_30d: float = Field(..., ge=0.0)


def derive_features(raw) -> FraudDerivedFeatures:
    vel_1h = float(raw.txns_1h)
    vel_24h = float(raw.txns_24h)

    denom = raw.avg_txn_amount_30d if raw.avg_txn_amount_30d > 0 else 1.0
    amt_ratio = float(raw.txn_amount) / denom

    return FraudDerivedFeatures(velocity_1h=vel_1h,velocity_24h=vel_24h,amount_ratio_30d=amt_ratio,)