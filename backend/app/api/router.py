"""
API router that combines all endpoint modules.
"""
from fastapi import APIRouter

from backend.app.api.endpoints import health, ask, metrics

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["System"])
api_router.include_router(ask.router, tags=["RAG"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
