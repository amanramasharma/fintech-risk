from fastapi import APIRouter

from .risk import router as risk_router
from .metrics import router as metrics_router

router = APIRouter()
router.include_router(risk_router)
router.include_router(metrics_router)