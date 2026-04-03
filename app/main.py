from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uuid
import time

from .schemas import AskRequest, RAGAnswer
from .rag_service import RAGService
from .logger import logger
from .metrics import METRICS
from .rate_limit import SimpleRateLimiter

app = FastAPI(title="RAG Service")

rag = RAGService()
limiter = SimpleRateLimiter(max_requests=30, window_seconds=60)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    key = request.client.host if request.client else "unknown"
    if not limiter.allow(key):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = rid

    t0 = time.perf_counter()
    response = await call_next(request)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    response.headers["x-request-id"] = rid
    logger.info(f"request_id={rid} path={request.url.path} latency_ms={latency_ms}")
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics-lite")
def metrics_lite():
    return {
        "requests_total": METRICS.requests_total,
        "cache_hits": METRICS.cache_hits,
        "cache_misses": METRICS.cache_misses,
        "errors_total": METRICS.errors_total,
        "last_latency_ms": METRICS.last_latency_ms,
        "stable_requests": METRICS.stable_requests,
        "canary_requests": METRICS.canary_requests,
        "stable_errors": METRICS.stable_errors,
        "canary_errors": METRICS.canary_errors,
    }

@app.post("/ask", response_model=RAGAnswer)
def ask(req: AskRequest, request: Request):
    try:
        rid = getattr(request.state, "request_id", "-")
        return rag.ask(req.question, request_id=rid)
    except Exception:
        rid = getattr(request.state, "request_id", "-")
        logger.exception(f"request_id={rid} unhandled_error=true")
        raise HTTPException(status_code=500, detail="Internal error")
