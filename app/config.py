"""
应用配置管理
"""
import os
import yaml
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class XTQuantMode(str, Enum):
    """xtquant接口模式"""
    MOCK = "mock"  # 使用模拟数据
    REAL = "real"  # 使用真实xtquant接口
    DEV = "dev"    # 开发模式，使用真实接口但不下单


class AppConfig(BaseModel):
    """应用基础配置"""
    name: str = "xtquant-proxy"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    file: Optional[str] = None
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"


class XTQuantDataConfig(BaseModel):
    """xtquant数据配置"""
    path: str = "./data"
    config_path: str = "./xtquant/config"
    qmt_userdata_path: Optional[str] = None  # QMT客户端的userdata_mini路径


class XTQuantTradingConfig(BaseModel):
    """xtquant交易配置"""
    allow_real_trading: bool = False
    mock_account_id: str = "mock_account_001"
    mock_password: str = "mock_password"
    test_account_id: Optional[str] = None
    test_password: Optional[str] = None
    real_accounts: Optional[List[Dict[str, Any]]] = None


class XTQuantConfig(BaseModel):
    """xtquant配置"""
    mode: XTQuantMode = XTQuantMode.MOCK
    data: XTQuantDataConfig = Field(default_factory=XTQuantDataConfig)
    trading: XTQuantTradingConfig = Field(default_factory=XTQuantTradingConfig)


class SecurityConfig(BaseModel):
    """安全配置"""
    secret_key: str = "your-secret-key-change-in-production"
    api_key_header: str = "X-API-Key"
    api_keys: List[str] = Field(default_factory=list)


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: Optional[str] = None


class RedisConfig(BaseModel):
    """Redis配置"""
    url: Optional[str] = None


class CORSConfig(BaseModel):
    """CORS配置"""
    allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])


class Settings(BaseModel):
    """完整配置类"""
    app: AppConfig = Field(default_factory=AppConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    xtquant: XTQuantConfig = Field(default_factory=XTQuantConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)


def load_config(config_file: Optional[str] = None) -> Settings:
    """加载配置文件"""
    if config_file is None:
        # 根据环境变量确定配置文件
        env = os.getenv("ENVIRONMENT", "dev")
        config_file = f"config_{env}.yml"
    
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在，使用默认配置")
        return Settings()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return Settings(**config_data)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return load_config()


# 全局配置实例
settings = get_settings()
