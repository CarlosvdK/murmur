import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import businesses, simulations, uploads, survey
from backend.api.routes import crm_contacts, crm_organisations, crm_twin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI(
    title="Murmur API",
    description="Customer simulation platform for small businesses",
    version="0.1.0",
)

import os

_allowed_origins = [
    "http://localhost:3000",
]
_prod_url = os.getenv("FRONTEND_URL")
if _prod_url:
    _allowed_origins.append(_prod_url)
# Always allow the production domain
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
)

app.include_router(businesses.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(survey.router, prefix="/api")
app.include_router(crm_contacts.router, prefix="/api")
app.include_router(crm_organisations.router, prefix="/api")
app.include_router(crm_twin.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
