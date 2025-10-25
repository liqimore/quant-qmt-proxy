"""
混合模式：同时运行 REST API 和 gRPC 服务
"""
import sys
import os
import threading
import uvicorn

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from app.grpc_server import serve as grpc_serve
from app.config import get_settings


def start_fastapi():
    """启动 FastAPI"""
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )


def start_grpc():
    """启动 gRPC"""
    grpc_serve()


if __name__ == '__main__':
    settings = get_settings()
    
    print("=" * 70)
    print("🚀 启动混合模式：FastAPI + gRPC")
    print("=" * 70)
    print(f"   REST API: http://{settings.app.host}:{settings.app.port}")
    print(f"   gRPC: {getattr(settings, 'grpc_host', '0.0.0.0')}:{getattr(settings, 'grpc_port', 50051)}")
    print(f"   模式: {settings.xtquant.mode.value}")
    print("=" * 70)
    print()
    
    # 在单独的线程中启动 gRPC
    grpc_thread = threading.Thread(target=start_grpc, daemon=True)
    grpc_thread.start()
    
    # 主线程运行 FastAPI
    start_fastapi()
