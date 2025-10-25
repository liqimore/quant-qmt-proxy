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
    MOCK = "mock"  # 不连接xtquant，使用模拟数据
    DEV = "dev"    # 连接xtquant，获取真实数据，但不允许交易
    PROD = "prod"  # 连接xtquant，获取真实数据，允许真实交易


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
    file: Optional[str] = "logs/app.log"
    error_file: Optional[str] = "logs/error.log"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    rotation: str = "10 MB"  # 日志文件轮转大小
    retention: str = "30 days"  # 日志保留时间
    compression: str = "zip"  # 压缩格式
    console_output: bool = True  # 是否同时输出到控制台
    backtrace: bool = True  # 是否显示完整堆栈跟踪
    diagnose: bool = False  # 是否显示诊断信息


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
    
    # gRPC 配置（使用属性访问以保持向后兼容）
    grpc_enabled: bool = True
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051
    grpc_max_workers: int = 10
    grpc_max_message_length: int = 50 * 1024 * 1024  # 50MB


def load_config(config_file: Optional[str] = None) -> Settings:
    """
    加载配置文件
    通过环境变量 APP_MODE 选择模式: mock, dev, prod
    默认使用 dev 模式
    """
    if config_file is None:
        config_file = "config.yml"
    
    if not os.path.exists(config_file):
        return Settings()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 获取运行模式
        app_mode = os.getenv("APP_MODE", "dev").lower()
        
        if app_mode not in ["mock", "dev", "prod"]:
            app_mode = "dev"
        
        # 获取模式特定配置
        modes_config = config_data.get("modes", {})
        mode_config = modes_config.get(app_mode, {})
        
        if not mode_config:
            return Settings()
        
        # 构建完整配置
        final_config = {
            "app": {
                "name": config_data.get("app", {}).get("name", "xtquant-proxy"),
                "version": config_data.get("app", {}).get("version", "1.0.0"),
                "debug": mode_config.get("debug", False),
                "host": mode_config.get("host", "0.0.0.0"),
                "port": mode_config.get("port", 8000)
            },
            "logging": {
                "level": mode_config.get("log_level", "INFO"),
                "file": config_data.get("logging", {}).get("file", "logs/app.log"),
                "error_file": config_data.get("logging", {}).get("error_file", "logs/error.log"),
                "format": config_data.get("logging", {}).get("format"),
                "rotation": config_data.get("logging", {}).get("rotation", "10 MB"),
                "retention": config_data.get("logging", {}).get("retention", "30 days"),
                "compression": config_data.get("logging", {}).get("compression", "zip"),
                # 允许模式特定配置覆盖全局配置
                "console_output": mode_config.get("logging", {}).get("console_output", config_data.get("logging", {}).get("console_output", True)),
                "backtrace": mode_config.get("logging", {}).get("backtrace", config_data.get("logging", {}).get("backtrace", True)),
                "diagnose": mode_config.get("logging", {}).get("diagnose", config_data.get("logging", {}).get("diagnose", False))
            },
            "xtquant": {
                "mode": mode_config.get("xtquant_mode", app_mode),
                "data": {
                    "path": config_data.get("xtquant", {}).get("data", {}).get("path", "./data"),
                    "config_path": config_data.get("xtquant", {}).get("data", {}).get("config_path", "./xtquant/config"),
                    "qmt_userdata_path": config_data.get("xtquant", {}).get("qmt_userdata_path")
                },
                "trading": {
                    "allow_real_trading": mode_config.get("allow_real_trading", False),
                    "mock_account_id": "mock_account_001",
                    "mock_password": "mock_password"
                }
            },
            "security": {
                "secret_key": config_data.get("security", {}).get("secret_key", "change-me"),
                "api_key_header": config_data.get("security", {}).get("api_key_header", "X-API-Key"),
                "api_keys": mode_config.get("api_keys", [])
            },
            "database": {
                "url": mode_config.get("database", {}).get("url")
            },
            "redis": {
                "url": mode_config.get("redis", {}).get("url")
            },
            "cors": mode_config.get("cors", {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"]
            })
        }
        
        return Settings(**final_config)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Settings()


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = load_config()
    return _settings_instance


def reset_settings():
    """重置配置实例（用于测试）"""
    global _settings_instance
    _settings_instance = None


# 全局配置实例（延迟加载）
settings = None
