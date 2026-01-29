from pydantic import Field
from .base import BaseConfig


class ApiConfig(BaseConfig):
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8080, alias="API_PORT")
    api_workers: int = Field(1, alias="API_WORKERS")

    cors_allow_origins: str | None = Field(None, alias="CORS_ALLOW_ORIGINS")