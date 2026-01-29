from pydantic import Field
from .base import BaseConfig


class TrainingConfig(BaseConfig):
    model_registry_provider: str = Field("s3", alias="MODEL_REGISTRY_PROVIDER")
    model_registry_bucket: str = Field(..., alias="MODEL_REGISTRY_BUCKET")
    model_registry_prefix: str = Field("model-registry", alias="MODEL_REGISTRY_PREFIX")
    