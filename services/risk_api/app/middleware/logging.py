import logging
from starlette.middleware.base import BaseHTTPMiddleware
from libs.core.context import request_id_ctx,trace_id_ctx

logger = logging.getLogger("risk_api.request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request_id_ctx.get()
        tid = trace_id_ctx.get()
        logger.info("request_started",extra={"path":request.url.path,"method":request.method,"request_id":rid,"trace_id":tid})
        resp = await call_next(request)
        logger.info("request_completed",extra={"path":request.url.path,"method":request.method,"status_code":resp.status_code,"request_id":rid,"trace_id":tid})
        return resp