"""
启动脚本
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print("=" * 50)
    print(f"启动 {settings.app_name} v{settings.app_version}")
    print("=" * 50)
    print(f"服务地址: http://{settings.host}:{settings.port}")
    print(f"API文档: http://{settings.host}:{settings.port}/docs")
    print(f"ReDoc文档: http://{settings.host}:{settings.port}/redoc")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
