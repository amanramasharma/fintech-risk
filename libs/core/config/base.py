from pydantic_settings import BaseSettings
from pydantic import Field


class BaseConfig(BaseSettings):
    env: str = Field(..., alias="ENV")
    service_name: str = Field(..., alias="SERVICE_NAME")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    json_logs: bool = Field(True, alias="JSON_LOGS")

    request_id_header: str = Field("x-request-id", alias="REQUEST_ID_HEADER")

    otel_enabled: bool = Field(True, alias="OTEL_ENABLED")
    otel_service_name: str = Field("ai-risk-intel", alias="OTEL_SERVICE_NAME")
    otel_endpoint: str | None = Field(None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")

    metrics_enabled: bool = Field(True, alias="METRICS_ENABLED")
    metrics_port: int = Field(9090, alias="METRICS_PORT")

    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(5432, alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")

    db_pool_size: int = Field(10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(20, alias="DB_MAX_OVERFLOW")
    db_pool_recycle_seconds: int = Field(1800, alias="DB_POOL_RECYCLE_SECONDS")

    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "forbid"