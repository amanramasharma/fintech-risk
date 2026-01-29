from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    env: str = Field(..., alias="ENV")
    service_name: str = Field("risk_api", alias="SERVICE_NAME")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    model_registry_provider: str = Field("local", alias="MODEL_REGISTRY_PROVIDER")
    local_model_dir: str = Field("artifacts", alias="LOCAL_MODEL_DIR")

    fraud_model_name: str = Field("fraud_iforest", alias="FRAUD_MODEL_NAME")
    fraud_model_version: str = Field("v1", alias="FRAUD_MODEL_VERSION")
    model_cache_dir: str = Field("/tmp/model_cache", alias="MODEL_CACHE_DIR")

    embeddings_provider: str = Field("openai", alias="EMBEDDINGS_PROVIDER")
    embeddings_model: str = Field("text-embedding-3-small", alias="EMBEDDINGS_MODEL")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")

    taxonomy_path: str = Field("configs/risk_taxonomy.yaml", alias="TAXONOMY_PATH")
    label_index_path: str = Field("artifacts/text/label_index.json", alias="LABEL_INDEX_PATH")