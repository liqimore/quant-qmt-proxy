"""
启动脚本
"""
import os
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    # 设置运行模式（如果未设置）
    # 可选值: mock, dev, prod
    if not os.getenv("APP_MODE"):
        os.environ["APP_MODE"] = "dev"
    
    # 启动信息
    app_mode = os.getenv("APP_MODE", "dev")
    print("=" * 60)
    print(f"🚀 启动 xtquant-proxy")
    print("=" * 60)
    print(f"运行模式: {app_mode}")
    print(f"服务地址: http://0.0.0.0:8000")
    print(f"API文档: http://0.0.0.0:8000/docs")
    print("=" * 60)
    print("\n💡 提示: 通过环境变量 APP_MODE 切换模式")
    print("   - mock: 不连接xtquant，使用模拟数据")
    print("   - dev:  连接xtquant，获取真实数据，禁止交易")
    print("   - prod: 连接xtquant，获取真实数据，允许交易")
    print("=" * 60 + "\n")
    
    # uvicorn会在加载app时自动调用get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式启用热重载
        log_level="info",
        access_log=True
    )
