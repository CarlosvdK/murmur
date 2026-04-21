import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.api.routes import businesses, simulations, uploads, survey
from backend.api.routes import crm_contacts, crm_organisations, crm_twin
from backend.db.client import get_supabase
from backend.observability import (
    RequestIDMiddleware,
    configure_logging,
    get_logger,
    init_sentry,
)
from backend.observability.rate_limit import limiter


APP_VERSION = "0.1.0"

configure_logging()
init_sentry()

log = get_logger("murmur.api")

app = FastAPI(
    title="Murmur API",
    description="Customer simulation platform for small businesses",
    version=APP_VERSION,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Request ID must be added first so it wraps everything below.
app.add_middleware(RequestIDMiddleware)

_allowed_origins = [
    "http://localhost:3000",
]
_prod_url = os.getenv("FRONTEND_URL")
if _prod_url:
    _allowed_origins.append(_prod_url)
_allowed_origins.append("https://murmurdynamics.com")
_allowed_origins.append("https://www.murmurdynamics.com")
_allowed_origins.append("https://murmur-production-fbb0.up.railway.app")
_allowed_origins.append("https://murmur-lemon.vercel.app")
_allowed_origins.append("https://murmur-k6kp3h1ny-carlosvdks-projects.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.include_router(businesses.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(survey.router, prefix="/api")
app.include_router(crm_contacts.router, prefix="/api")
app.include_router(crm_organisations.router, prefix="/api")
app.include_router(crm_twin.router, prefix="/api")


def _check_db() -> tuple[str, str | None]:
    """Ping Supabase with a trivial select. Returns (status, error_message)."""
    try:
        db = get_supabase()
        # Cheap, schema-agnostic: a SELECT against pg_tables is fine, but
        # supabase-py is table-oriented -- just issue a head-count.
        db.table("businesses").select("id").limit(1).execute()
        return "ok", None
    except Exception as exc:  # pragma: no cover -- logged below
        log.warning("health: db check failed", extra={"error": str(exc)})
        return "error", str(exc)


@app.get("/api/health")
async def health():
    db_status, db_error = _check_db()
    body = {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": APP_VERSION,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "git_sha": os.getenv("GIT_SHA"),
        "checks": {"db": db_status},
    }
    if db_error:
        body["checks"]["db_error"] = db_error
    http_status = 200 if db_status == "ok" else 503
    return JSONResponse(body, status_code=http_status)
