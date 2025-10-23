"""
健康检查路由
"""
from fastapi import APIRouter, Depends
from app.utils.helpers import format_response
from app.config import get_settings, Settings

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("/")
async def health_check(settings: Settings = Depends(get_settings)):
    """健康检查接口"""
    return format_response(
        data={
            "status": "healthy",
            "app_name": settings.app.name,
            "app_version": settings.app.version,
            "xtquant_mode": settings.xtquant.mode.value,
            "timestamp": "2024-01-01T00:00:00"
        },
        message="服务运行正常"
    )


@router.get("/ready")
async def readiness_check():
    """就绪检查接口"""
    return format_response(
        data={"status": "ready"},
        message="服务就绪"
    )


@router.get("/live")
async def liveness_check():
    """存活检查接口"""
    return format_response(
        data={"status": "alive"},
        message="服务存活"
    )
