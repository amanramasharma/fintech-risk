from pydantic import Field
from .base import BaseConfig


class WorkerConfig(BaseConfig):
    queue_provider: str = Field("none", alias="QUEUE_PROVIDER")
    sqs_queue_url: str | None = Field(None, alias="SQS_QUEUE_URL")

    worker_max_concurrency: int = Field(4, alias="WORKER_MAX_CONCURRENCY")
    worker_poll_seconds: int = Field(2, alias="WORKER_POLL_SECONDS")