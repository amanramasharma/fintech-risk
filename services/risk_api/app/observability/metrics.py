from prometheus_client import Counter,Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "risk_api_http_requests_total",
    "Total HTTP requests",
    ["method","path","status"],)

HTTP_REQUEST_LATENCY_SECONDS = Histogram(
    "risk_api_http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method","path"],
    buckets=(0.05,0.1,0.25,0.5,1,2,5,10),)

RISK_DECISIONS_TOTAL = Counter(
    "risk_api_risk_decisions_total",
    "Total number of risk decisions produced",
    ["category"],)

RISK_REASON_CODES_TOTAL = Counter(
    "risk_api_risk_reason_codes_total",
    "Total number of reason codes emitted",
    ["reason"],)

AUDIT_WRITES_TOTAL = Counter(
    "risk_api_audit_writes_total",
    "Total audit write attempts",
    ["status"],)