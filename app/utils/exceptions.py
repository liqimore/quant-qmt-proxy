"""
异常处理模块
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class XTQuantException(Exception):
    """xtquant相关异常基类"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DataServiceException(XTQuantException):
    """数据服务异常"""
    pass


class TradingServiceException(XTQuantException):
    """交易服务异常"""
    pass


class ConfigurationException(XTQuantException):
    """配置异常"""
    pass


class AuthenticationException(XTQuantException):
    """认证异常"""
    pass


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """创建标准错误响应"""
    error_detail = {
        "message": message,
        "error_code": error_code or "INTERNAL_ERROR"
    }
    if details:
        error_detail.update(details)
    
    return HTTPException(
        status_code=status_code,
        detail=error_detail
    )


def handle_xtquant_exception(exc: XTQuantException) -> HTTPException:
    """处理xtquant异常"""
    if isinstance(exc, DataServiceException):
        # 对于验证相关的错误（如空列表），使用422状态码
        if exc.error_code in ["EMPTY_SYMBOLS", "INVALID_SYMBOLS"]:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code or "DATA_SERVICE_ERROR",
            status_code=status_code
        )
    elif isinstance(exc, TradingServiceException):
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code or "TRADING_SERVICE_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    elif isinstance(exc, AuthenticationException):
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code or "AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    elif isinstance(exc, ConfigurationException):
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code or "CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    else:
        return create_error_response(
            message=exc.message,
            error_code=exc.error_code or "UNKNOWN_ERROR"
        )
