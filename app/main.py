"""
FastAPI主应用入口
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
import os

# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import get_settings, Settings
from app.routers import health, data, trading, websocket
from app.utils.helpers import format_response
from app.utils.exceptions import XTQuantException, handle_xtquant_exception
from app.utils.logger import configure_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    settings = get_settings()
    
    # 初始化日志系统
    configure_logging(
        log_level=settings.logging.level,
        log_file=settings.logging.file or "logs/app.log",
        error_log_file=settings.logging.error_file or "logs/error.log",
        log_format=settings.logging.format,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        compression=settings.logging.compression
    )
    
    # 初始化订阅管理器并设置事件循环
    import asyncio
    from app.dependencies import get_subscription_manager
    
    try:
        loop = asyncio.get_running_loop()
        subscription_manager = get_subscription_manager(settings)
        subscription_manager.set_event_loop(loop)
        logger.info("订阅管理器已初始化")
    except Exception as e:
        logger.warning(f"订阅管理器初始化失败: {e}")
    
    logger.info("REST API 服务已就绪")
    
    yield
    
    # 关闭时执行
    logger.info("REST API 服务正在关闭...")
    
    # 关闭订阅管理器
    try:
        subscription_manager = get_subscription_manager(settings)
        subscription_manager.shutdown()
        logger.info("订阅管理器已关闭")
    except Exception as e:
        logger.error(f"关闭订阅管理器失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="xtquant-proxy",
    description="基于xtquant的量化交易代理服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(XTQuantException)
async def xtquant_exception_handler(request: Request, exc: XTQuantException):
    """处理xtquant相关异常"""
    return JSONResponse(
        status_code=500,
        content=format_response(
            data=None,
            message=exc.message,
            success=False,
            code=500
        )
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    return JSONResponse(
        status_code=exc.status_code,
        content=format_response(
            data=None,
            message=str(exc.detail),
            success=False,
            code=exc.status_code
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    return JSONResponse(
        status_code=500,
        content=format_response(
            data=None,
            message=f"内部服务器错误: {str(exc)}",
            success=False,
            code=500
        )
    )


# 注册路由
app.include_router(health.router)
app.include_router(data.router)
app.include_router(trading.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """根路径"""
    settings = get_settings()
    return format_response(
        data={
            "app_name": settings.app.name,
            "app_version": settings.app.version,
            "xtquant_mode": settings.xtquant.mode.value,
            "description": "基于xtquant的量化交易代理服务",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        },
        message="欢迎使用xtquant-proxy服务"
    )


@app.get("/info")
async def app_info():
    """应用信息"""
    settings = get_settings()
    return format_response(
        data={
            "name": settings.app.name,
            "version": settings.app.version,
            "debug": settings.app.debug,
            "host": settings.app.host,
            "port": settings.app.port,
            "log_level": settings.logging.level,
            "xtquant_mode": settings.xtquant.mode.value,
            "allow_real_trading": settings.xtquant.trading.allow_real_trading
        },
        message="应用信息获取成功"
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    # 关闭热加载，如需启用请设置 reload=True 和 reload_includes=["*.py"]
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False,  # 热加载已关闭
        reload_includes=None,  # 仅监控 .py 文件（当 reload=True 时）
        log_level=settings.logging.level.lower()
    )
