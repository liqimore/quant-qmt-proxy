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
    
    # 这里可以添加实际的API密钥验证逻辑
    # 目前简单验证非空
    if not api_key.strip():
        raise AuthenticationException("无效的API密钥")
    
    return api_key


def get_xtquant_data_path(settings: Settings = Depends(get_settings)) -> str:
    """获取xtquant数据路径"""
    return settings.xtquant_data_path


def get_xtquant_config_path(settings: Settings = Depends(get_settings)) -> str:
    """获取xtquant配置路径"""
    return settings.xtquant_config_path
