import logging
from pythonjsonlogger import jsonlogger
from .context import request_id_ctx, trace_id_ctx


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.trace_id = trace_id_ctx.get()
        return True

def setup_logging(service_name: str, level: str = "INFO") -> None:
    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler()

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(request_id)s %(trace_id)s"
    )
    handler.setFormatter(formatter)

    handler.addFilter(ContextFilter())

    logger.handlers.clear()
    logger.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)