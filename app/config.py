"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "xtquant-proxy"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # xtquant配置
    xtquant_data_path: str = "./data"
    xtquant_config_path: str = "./xtquant/config"
    
    # 安全配置
    secret_key: str = "your-secret-key-change-in-production"
    api_key_header: str = "X-API-Key"
    
    # 数据库配置
    database_url: Optional[str] = None
    
    # Redis配置
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
