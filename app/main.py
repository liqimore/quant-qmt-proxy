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
from app.routers import health, data, trading
from app.utils.helpers import setup_logging, format_response
from app.utils.exceptions import XTQuantException, handle_xtquant_exception


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    settings = get_settings()
    setup_logging(settings.log_level, settings.log_file)
    
    print(f"启动 {settings.app_name} v{settings.app_version}")
    print(f"调试模式: {settings.debug}")
    print(f"服务地址: http://{settings.host}:{settings.port}")
    
    yield
    
    # 关闭时执行
    print("应用正在关闭...")


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


@app.get("/")
async def root():
    """根路径"""
    settings = get_settings()
    return format_response(
        data={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
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
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port,
            "log_level": settings.log_level
        },
        message="应用信息获取成功"
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
