import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from ..observability.metrics import HTTP_REQUESTS_TOTAL,HTTP_REQUEST_LATENCY_SECONDS

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start = time.perf_counter()
        status = 500
        try:
            resp: Response = await call_next(request)
            status = resp.status_code
            return resp
        finally:
            elapsed = time.perf_counter() - start
            route = None
            try:
                r = request.scope.get("route")
                route = getattr(r, "path", None)
            except Exception:
                route = None
            path = route or request.url.path
            HTTP_REQUESTS_TOTAL.labels(method=request.method,path=path,status=str(status)).inc()
            HTTP_REQUEST_LATENCY_SECONDS.labels(method=request.method,path=path).observe(elapsed)