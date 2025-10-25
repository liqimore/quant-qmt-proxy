"""
多环境启动脚本
"""
import os
import sys
import argparse
import uvicorn
from app.config import get_settings


def main():
    parser = argparse.ArgumentParser(description="xtquant-proxy 启动脚本")
    parser.add_argument(
        "--env", 
        choices=["dev", "test", "prod"], 
        default="dev",
        help="环境选择 (dev/test/prod)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="服务主机地址"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="服务端口"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="启用热重载"
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["ENVIRONMENT"] = args.env
    
    # 加载配置
    settings = get_settings()
    
    print("=" * 60)
    print(f"🚀 启动 {settings.app.name} v{settings.app.version}")
    print("=" * 60)
    print(f"📁 环境: {args.env}")
    print(f"🔧 xtquant模式: {settings.xtquant.mode.value}")
    print(f"💰 允许真实交易: {settings.xtquant.trading.allow_real_trading}")
    print(f"🌐 服务地址: http://{args.host}:{args.port}")
    print(f"📚 API文档: http://{args.host}:{args.port}/docs")
    print(f"📖 ReDoc文档: http://{args.host}:{args.port}/redoc")
    print("=" * 60)
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload or settings.app.debug,
        log_level=settings.logging.level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
