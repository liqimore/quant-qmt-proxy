"""
启动脚本 - 同时运行 REST API 和 gRPC 服务
"""
import sys
import os
import threading
import uvicorn

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))


def start_grpc():
    """启动 gRPC 服务"""
    from app.grpc_server import serve as grpc_serve
    grpc_serve()


if __name__ == '__main__':
    # 设置运行模式（如果未设置）
    # 可选值: mock, dev, prod
    if not os.getenv("APP_MODE"):
        os.environ["APP_MODE"] = "dev"
    
    # 预先加载配置（仅在主进程）
    from app.config import get_settings
    settings = get_settings()
    
    print("=" * 70)
    print("🚀 启动 xtquant-proxy 服务")
    print("=" * 70)
    print(f"   运行模式: {settings.xtquant.mode.value}")
    print(f"   REST API: http://{settings.app.host}:{settings.app.port}")
    print(f"   gRPC:     {settings.grpc_host}:{settings.grpc_port}")
    print(f"   API文档:  http://{settings.app.host}:{settings.app.port}/docs")
    print("=" * 70)
    print("\n💡 提示: 通过环境变量 APP_MODE 切换模式")
    print("   - mock: 不连接xtquant，使用模拟数据")
    print("   - dev:  连接xtquant，获取真实数据，禁止交易")
    print("   - prod: 连接xtquant，获取真实数据，允许交易")
    print("=" * 70 + "\n")
    
    # 在单独的线程中启动 gRPC
    grpc_thread = threading.Thread(target=start_grpc, daemon=True)
    grpc_thread.start()
    
    # 主线程运行 FastAPI (带热重载)
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level="info",
        access_log=True
    )
