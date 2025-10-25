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


def print_banner(settings):
    """打印启动横幅"""
    print("\n" + "=" * 80)
    print("🚀 xtquant-proxy 服务启动中...")
    print("=" * 80)
    print(f"应用名称:     {settings.app.name} v{settings.app.version}")
    print(f"运行模式:     {settings.xtquant.mode.value}")
    print(f"调试模式:     {'开启' if settings.app.debug else '关闭'}")
    print(f"允许交易:     {'是' if settings.xtquant.trading.allow_real_trading else '否'}")
    print("-" * 80)
    print(f"REST API:     http://{settings.app.host}:{settings.app.port}")
    print(f"gRPC 服务:    {settings.grpc_host}:{settings.grpc_port}")
    print(f"API 文档:     http://{settings.app.host}:{settings.app.port}/docs")
    print(f"日志级别:     {settings.logging.level}")
    print("=" * 80)
    print("\n💡 提示: 使用环境变量 APP_MODE 切换运行模式")
    print("   • mock - 模拟模式，不连接 xtquant，返回模拟数据")
    print("   • dev  - 开发模式，连接 xtquant，禁止真实交易")
    print("   • prod - 生产模式，连接 xtquant，允许真实交易")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    # 设置运行模式（如果未设置）
    if not os.getenv("APP_MODE"):
        os.environ["APP_MODE"] = "dev"
    
    # 加载配置（单例模式，仅加载一次）
    from app.config import get_settings
    from app.utils.helpers import setup_logging
    settings = get_settings()
    
    # 初始化日志系统
    setup_logging(
        log_level=settings.logging.level,
        log_file=settings.logging.file,
        error_file=settings.logging.error_file,
        log_format=settings.logging.format,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        compression=settings.logging.compression,
        console_output=settings.logging.console_output,
        backtrace=settings.logging.backtrace,
        diagnose=settings.logging.diagnose
    )
    
    # 打印启动信息
    print_banner(settings)
    
    # 在单独的线程中启动 gRPC 服务
    grpc_thread = threading.Thread(target=start_grpc, daemon=True, name="gRPC-Server")
    grpc_thread.start()
    
    # 主线程运行 FastAPI
    # 热加载配置：关闭热加载，或仅监控 .py 文件
    reload_enabled = False  # 默认关闭热加载
    reload_includes = None
    
    # 如果需要启用热加载，取消下面的注释并设置为 True
    # reload_enabled = settings.app.debug
    # reload_includes = ["*.py"]  # 仅监控 Python 源码文件
    
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=reload_enabled,
        reload_includes=reload_includes,
        log_level=settings.logging.level.lower(),
        access_log=True
    )
