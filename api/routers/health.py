"""
Health check router.
"""
from fastapi import APIRouter

try:
    from core.config import APP_TITLE, APP_VERSION
except ImportError:
    from api.core.config import APP_TITLE, APP_VERSION

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Service Health Check")
def health_check():
    return {
        "status": "ok",
        "service": APP_TITLE,
        "version": APP_VERSION,
    }
