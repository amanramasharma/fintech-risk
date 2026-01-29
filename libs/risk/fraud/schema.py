from pydantic import BaseModel, Field


class FraudFeatureVector(BaseModel):
    txn_amount: float = Field(..., ge=0.0)
    txn_currency: str
    txn_country: str

    txns_1h: int = Field(..., ge=0)
    txns_24h: int = Field(..., ge=0)

    avg_txn_amount_30d: float = Field(..., ge=0.0)
    account_age_days: int = Field(..., ge=0)

    device_change_7d: int = Field(..., ge=0)
    failed_logins_24h: int = Field(..., ge=0)