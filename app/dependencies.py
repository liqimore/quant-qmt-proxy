"""
依赖注入模块
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import sys
import os

# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import get_settings, Settings
from app.utils.exceptions import AuthenticationException


# 安全方案
security = HTTPBearer(auto_error=False)


# 全局服务实例（单例模式）
_data_service_instance = None
_trading_service_instance = None


def get_data_service(settings: Settings = Depends(get_settings)):
    """获取DataService单例实例"""
    global _data_service_instance
    
    if _data_service_instance is None:
        from app.services.data_service import DataService
        print("🔧 首次创建DataService实例")
        _data_service_instance = DataService(settings)
    
    return _data_service_instance


def get_trading_service(settings: Settings = Depends(get_settings)):
    """获取TradingService单例实例"""
    global _trading_service_instance
    
    if _trading_service_instance is None:
        from app.services.trading_service import TradingService
        print("🔧 首次创建TradingService实例")
        _trading_service_instance = TradingService(settings)
    
    return _trading_service_instance


async def get_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: Settings = Depends(get_settings)
) -> Optional[str]:
    """获取API密钥"""
    if not credentials:
        return None
    
    # 这里可以添加API密钥验证逻辑
    # 目前简单返回token
    return credentials.credentials


async def verify_api_key(
    api_key: Optional[str] = Depends(get_api_key),
    settings: Settings = Depends(get_settings)
) -> str:
    """验证API密钥"""
    if not api_key:
        raise AuthenticationException("API密钥缺失")
    
    # 验证API密钥是否在允许列表中
    if settings.security.api_keys and api_key not in settings.security.api_keys:
        raise AuthenticationException("无效的API密钥")
    
    return api_key


def get_xtquant_data_path(settings: Settings = Depends(get_settings)) -> str:
    """获取xtquant数据路径"""
    return settings.xtquant.data.path


def get_xtquant_config_path(settings: Settings = Depends(get_settings)) -> str:
    """获取xtquant配置路径"""
    return settings.xtquant.data.config_path


def get_xtquant_mode(settings: Settings = Depends(get_settings)) -> str:
    """获取xtquant接口模式"""
    return settings.xtquant.mode.value


def is_real_trading_allowed(settings: Settings = Depends(get_settings)) -> bool:
    """检查是否允许真实交易"""
    return (
        settings.xtquant.mode.value == "real" and 
        settings.xtquant.trading.allow_real_trading
    )
