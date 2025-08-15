from fastapi import APIRouter, Depends
from common.logger import get_logger
from common.config import settings

router = APIRouter()
logger = get_logger()

@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "aahb-api-gateway",
        "version": settings.VERSION,
        "environment": settings.ENV
    }