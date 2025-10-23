"""
启动脚本
"""
import os
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    # 设置环境变量（如果未设置）
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "dev"
    
    settings = get_settings()
    
    print("=" * 50)
    print(f"启动 {settings.app.name} v{settings.app.version}")
    print("=" * 50)
    print(f"环境: {os.getenv('ENVIRONMENT', 'dev')}")
    print(f"xtquant模式: {settings.xtquant.mode.value}")
    print(f"服务地址: http://{settings.app.host}:{settings.app.port}")
    print(f"API文档: http://{settings.app.host}:{settings.app.port}/docs")
    print(f"ReDoc文档: http://{settings.app.host}:{settings.app.port}/redoc")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug,
        log_level=settings.logging.level.lower(),
        access_log=True
    )
