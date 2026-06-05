"""Application configuration."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.utils.exceptions import ConfigurationException


class XTQuantMode(str, Enum):
    MOCK = "mock"
    DEV = "dev"
    PROD = "prod"


class AccountKind(str, Enum):
    MOCK = "mock"
    SIMULATED = "simulated"
    REAL = "real"


class AppConfig(BaseModel):
    name: str = "xtquant-proxy"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str | None = "logs/app.log"
    error_file: str | None = "logs/error.log"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    rotation: str = "10 MB"
    retention: str = "30 days"
    compression: str = "zip"
    console_output: bool = True
    backtrace: bool = True
    diagnose: bool = False


class XTQuantDataConfig(BaseModel):
    path: str = "./data"
    config_path: str = "./xtquant/config"
    qmt_userdata_path: str | None = None
    max_queue_size: int = 1000
    max_subscriptions: int = 100
    heartbeat_interval: int = 60
    whole_quote_enabled: bool = False


class XTQuantTradingAccountConfig(BaseModel):
    name: str
    account_id: str
    account_type: str = "STOCK"
    account_kind: AccountKind = AccountKind.SIMULATED
    allowed_modes: list[XTQuantMode] = Field(default_factory=lambda: [XTQuantMode.DEV])
    enabled: bool = True


class XTQuantTradingConfig(BaseModel):
    mock_account_id: str = "mock_account_001"
    mock_password: str = "mock_password"
    enable_prod_orders: bool = False
    disconnect_timeout_seconds: float = 3.0
    accounts: list[XTQuantTradingAccountConfig] = Field(default_factory=list)


class XTQuantConfig(BaseModel):
    mode: XTQuantMode = XTQuantMode.MOCK
    data: XTQuantDataConfig = Field(default_factory=XTQuantDataConfig)
    trading: XTQuantTradingConfig = Field(default_factory=XTQuantTradingConfig)


class SecurityConfig(BaseModel):
    secret_key: str = "your-secret-key-change-in-production"
    api_keys: list[str] = Field(default_factory=list)


class DatabaseConfig(BaseModel):
    url: str | None = None


class RedisConfig(BaseModel):
    url: str | None = None


class CORSConfig(BaseModel):
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])


class UvicornConfig(BaseModel):
    timeout_keep_alive: int = 5


class TestingConfig(BaseModel):
    default_account_profile: str | None = None
    enable_prod_readonly_tests: bool = False
    qmt_userdata_path: str | None = None
    prod_unlock_token: str | None = None


class MarketDataSyncConfig(BaseModel):
    enabled: bool = False
    cron_time: str = "18:00"
    periods: list[str] = Field(default_factory=lambda: ["1d", "1m"])
    concurrency: int = 3
    on_startup: bool = True
    max_retries: int = 2
    retry_backoff_seconds: float = 1.0
    fail_fast: bool = False
    symbols_override: list[str] | None = None


class Settings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    xtquant: XTQuantConfig = Field(default_factory=XTQuantConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    uvicorn: UvicornConfig = Field(default_factory=UvicornConfig)
    testing: TestingConfig = Field(default_factory=TestingConfig)
    market_data_sync: MarketDataSyncConfig = Field(default_factory=MarketDataSyncConfig)
    grpc_enabled: bool = True
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051
    grpc_max_workers: int = 10
    grpc_max_message_length: int = 50 * 1024 * 1024
    app_servers: str = "all"

    def market_data_sync_effective_enabled(self) -> bool:
        return self.market_data_sync.enabled and self.xtquant.mode != XTQuantMode.MOCK


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _deep_merge(base: Any, overlay: Any) -> Any:
    if not isinstance(base, dict) or not isinstance(overlay, dict):
        return overlay
    merged = dict(base)
    for key, value in overlay.items():
        if key in merged:
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml_file(path: str | os.PathLike[str] | None) -> dict[str, Any]:
    if not path:
        return {}
    file_path = Path(path)
    if not file_path.exists():
        return {}
    with file_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            return {}
        return data


def _normalize_mode(mode: str | None) -> str:
    normalized = (mode or "dev").strip().lower()
    if normalized not in {"mock", "dev", "prod"}:
        if mode is None or not str(mode).strip():
            return "dev"
        raise ConfigurationException(
            f"invalid app mode: {mode}",
            "INVALID_APP_MODE",
        )
    return normalized


def _normalize_app_servers(value: str | None) -> str:
    normalized = (value or "all").strip().lower()
    if normalized not in {"all", "grpc", "rest"}:
        if value is None or not str(value).strip():
            return "all"
        raise ConfigurationException(
            f"invalid app servers: {value}",
            "INVALID_APP_SERVERS",
        )
    return normalized


def load_config(
    config_file: str | None = None,
    *,
    app_mode: str | None = None,
    local_config_file: str | None = "config.local.yml",
) -> Settings:
    config_file = config_file or "config.yml"

    config_data = _load_yaml_file(config_file)
    if local_config_file:
        config_data = _deep_merge(config_data, _load_yaml_file(local_config_file))

    if not config_data:
        raise ConfigurationException(
            f"configuration file '{config_file}' is missing or empty",
            "CONFIG_FILE_MISSING",
        )

    resolved_mode = _normalize_mode(app_mode or os.getenv("APP_MODE", "dev"))
    mode_config = config_data.get("modes", {}).get(resolved_mode, {})
    if not mode_config:
        raise ConfigurationException(
            f"mode '{resolved_mode}' is not defined in '{config_file}'",
            "MODE_CONFIG_MISSING",
        )

    app_env_host = os.getenv("APP_HOST")
    app_env_port = os.getenv("APP_PORT")
    grpc_env_host = os.getenv("GRPC_HOST")
    grpc_env_port = os.getenv("GRPC_PORT")
    qmt_userdata_override = os.getenv("QMT_USERDATA_PATH")
    api_keys_override = os.getenv("APP_API_KEYS")
    debug_override = os.getenv("APP_DEBUG")
    enable_prod_orders_override = os.getenv("APP_ENABLE_PROD_ORDERS")
    xtquant_config = config_data.get("xtquant", {})
    xtquant_data_config = xtquant_config.get("data", {})
    xtquant_trading_config = xtquant_config.get("trading", {})

    resolved_api_keys = (
        [item.strip() for item in api_keys_override.split(",") if item.strip()]
        if api_keys_override
        else mode_config.get("api_keys", [])
    )

    testing_config = config_data.get("testing", {})
    qmt_userdata_path = (
        qmt_userdata_override
        or xtquant_config.get("qmt_userdata_path")
        or xtquant_data_config.get("qmt_userdata_path")
    )

    final_config = {
        "app": {
            "name": config_data.get("app", {}).get("name", "xtquant-proxy"),
            "version": config_data.get("app", {}).get("version", "1.0.0"),
            "debug": (
                _env_flag("APP_DEBUG", False)
                if debug_override is not None
                else mode_config.get("debug", False)
            ),
            "host": app_env_host or mode_config.get("host", "0.0.0.0"),
            "port": int(app_env_port or mode_config.get("port", 8000)),
        },
        "logging": {
            "level": mode_config.get("log_level", "INFO"),
            "file": config_data.get("logging", {}).get("file", "logs/app.log"),
            "error_file": config_data.get("logging", {}).get("error_file", "logs/error.log"),
            "format": config_data.get("logging", {}).get(
                "format",
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            ),
            "rotation": config_data.get("logging", {}).get("rotation", "10 MB"),
            "retention": config_data.get("logging", {}).get("retention", "30 days"),
            "compression": config_data.get("logging", {}).get("compression", "zip"),
            "console_output": mode_config.get("logging", {}).get(
                "console_output",
                config_data.get("logging", {}).get("console_output", True),
            ),
            "backtrace": mode_config.get("logging", {}).get(
                "backtrace",
                config_data.get("logging", {}).get("backtrace", True),
            ),
            "diagnose": mode_config.get("logging", {}).get(
                "diagnose",
                config_data.get("logging", {}).get("diagnose", False),
            ),
        },
        "xtquant": {
            "mode": mode_config.get("xtquant_mode", resolved_mode),
            "data": {
                "path": xtquant_data_config.get("path", "./data"),
                "config_path": xtquant_data_config.get("config_path", "./xtquant/config"),
                "qmt_userdata_path": qmt_userdata_path,
                "max_queue_size": xtquant_data_config.get("max_queue_size", 1000),
                "max_subscriptions": xtquant_data_config.get("max_subscriptions", 100),
                "heartbeat_interval": xtquant_data_config.get(
                    "heartbeat_interval",
                    xtquant_data_config.get("heartbeat_timeout", 60),
                ),
                "whole_quote_enabled": xtquant_data_config.get("whole_quote_enabled", False),
            },
            "trading": {
                "mock_account_id": xtquant_trading_config.get("mock_account_id", "mock_account_001"),
                "mock_password": xtquant_trading_config.get("mock_password", "mock_password"),
                "enable_prod_orders": (
                    _env_flag("APP_ENABLE_PROD_ORDERS", False)
                    if enable_prod_orders_override is not None
                    else xtquant_trading_config.get("enable_prod_orders", False)
                ),
                "disconnect_timeout_seconds": float(
                    xtquant_trading_config.get("disconnect_timeout_seconds", 3.0)
                ),
                "accounts": xtquant_trading_config.get("accounts", []),
            },
        },
        "security": {
            "secret_key": config_data.get("security", {}).get("secret_key", "change-me"),
            "api_keys": resolved_api_keys,
        },
        "database": {
            "url": mode_config.get("database", {}).get("url"),
        },
        "redis": {
            "url": mode_config.get("redis", {}).get("url"),
        },
        "cors": mode_config.get(
            "cors",
            {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            },
        ),
        "uvicorn": {
            "timeout_keep_alive": config_data.get("uvicorn", {}).get("timeout_keep_alive", 5),
        },
        "testing": {
            "default_account_profile": testing_config.get("default_account_profile"),
            "enable_prod_readonly_tests": testing_config.get("enable_prod_readonly_tests", False),
            "qmt_userdata_path": testing_config.get("qmt_userdata_path"),
            "prod_unlock_token": testing_config.get("prod_unlock_token"),
        },
        "market_data_sync": config_data.get("market_data_sync", {}),
        "grpc_enabled": config_data.get("grpc", {}).get("enabled", True),
        "grpc_host": grpc_env_host or config_data.get("grpc", {}).get("host", "0.0.0.0"),
        "grpc_port": int(grpc_env_port or config_data.get("grpc", {}).get("port", 50051)),
        "grpc_max_workers": config_data.get("grpc", {}).get("max_workers", 10),
        "grpc_max_message_length": config_data.get("grpc", {}).get("max_message_length", 50 * 1024 * 1024),
        "app_servers": _normalize_app_servers(os.getenv("APP_SERVERS", "all")),
    }
    return Settings(**final_config)


_settings_instance: Settings | None = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = load_config()
    return _settings_instance


def reset_settings() -> None:
    global _settings_instance
    _settings_instance = None


settings = None
