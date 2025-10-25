"""
统一日志工具模块
提供便捷的日志记录接口
"""
from loguru import logger
from typing import Any, Dict, Optional
import sys


def get_logger(name: Optional[str] = None):
    """
    获取logger实例
    
    Args:
        name: 模块名称（可选，用于标识日志来源）
    
    Returns:
        logger实例
    
    Usage:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("这是一条信息日志")
        logger.error("这是一条错误日志")
    """
    if name:
        return logger.bind(name=name)
    return logger


def log_function_call(func_name: str, **kwargs):
    """
    记录函数调用日志
    
    Args:
        func_name: 函数名
        **kwargs: 函数参数
    """
    logger.debug(f"调用函数: {func_name}", extra={"params": kwargs})


def log_api_request(method: str, path: str, params: Optional[Dict[str, Any]] = None):
    """
    记录API请求日志
    
    Args:
        method: HTTP方法
        path: 请求路径
        params: 请求参数
    """
    logger.info(
        f"API请求: {method} {path}",
        extra={"method": method, "path": path, "params": params}
    )


def log_api_response(path: str, status_code: int, duration_ms: float):
    """
    记录API响应日志
    
    Args:
        path: 请求路径
        status_code: HTTP状态码
        duration_ms: 响应时间（毫秒）
    """
    level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
    logger.log(
        level,
        f"API响应: {path} - {status_code} ({duration_ms:.2f}ms)",
        extra={"path": path, "status_code": status_code, "duration_ms": duration_ms}
    )


def log_grpc_request(service: str, method: str, request_data: Optional[Dict[str, Any]] = None):
    """
    记录gRPC请求日志
    
    Args:
        service: 服务名
        method: 方法名
        request_data: 请求数据
    """
    logger.info(
        f"gRPC请求: {service}/{method}",
        extra={"service": service, "method": method, "request": request_data}
    )


def log_grpc_response(service: str, method: str, success: bool, duration_ms: float):
    """
    记录gRPC响应日志
    
    Args:
        service: 服务名
        method: 方法名
        success: 是否成功
        duration_ms: 响应时间（毫秒）
    """
    level = "INFO" if success else "ERROR"
    logger.log(
        level,
        f"gRPC响应: {service}/{method} - {'成功' if success else '失败'} ({duration_ms:.2f}ms)",
        extra={"service": service, "method": method, "success": success, "duration_ms": duration_ms}
    )


def log_xtquant_call(function: str, params: Optional[Dict[str, Any]] = None):
    """
    记录xtquant函数调用日志
    
    Args:
        function: xtquant函数名
        params: 函数参数
    """
    logger.debug(
        f"调用xtquant: {function}",
        extra={"function": function, "params": params}
    )


def log_xtquant_result(function: str, success: bool, result: Optional[Any] = None, error: Optional[str] = None):
    """
    记录xtquant函数结果日志
    
    Args:
        function: xtquant函数名
        success: 是否成功
        result: 返回结果
        error: 错误信息
    """
    if success:
        logger.debug(
            f"xtquant调用成功: {function}",
            extra={"function": function, "result_type": type(result).__name__}
        )
    else:
        logger.error(
            f"xtquant调用失败: {function} - {error}",
            extra={"function": function, "error": error}
        )


def log_exception(exc: Exception, context: Optional[str] = None):
    """
    记录异常日志
    
    Args:
        exc: 异常对象
        context: 上下文信息
    """
    logger.exception(
        f"发生异常: {context or type(exc).__name__}",
        extra={"exception_type": type(exc).__name__, "context": context}
    )


def log_performance(operation: str, duration_ms: float, threshold_ms: float = 1000):
    """
    记录性能日志
    
    Args:
        operation: 操作名称
        duration_ms: 执行时间（毫秒）
        threshold_ms: 警告阈值（毫秒）
    """
    level = "WARNING" if duration_ms > threshold_ms else "DEBUG"
    logger.log(
        level,
        f"性能: {operation} 耗时 {duration_ms:.2f}ms",
        extra={"operation": operation, "duration_ms": duration_ms}
    )


def log_data_operation(operation: str, stock_code: Optional[str] = None, count: Optional[int] = None):
    """
    记录数据操作日志
    
    Args:
        operation: 操作类型（如：获取K线、获取Tick等）
        stock_code: 股票代码
        count: 数据条数
    """
    logger.info(
        f"数据操作: {operation}",
        extra={"operation": operation, "stock_code": stock_code, "count": count}
    )


# 导出常用的logger方法，方便直接导入使用
__all__ = [
    'get_logger',
    'logger',
    'log_function_call',
    'log_api_request',
    'log_api_response',
    'log_grpc_request',
    'log_grpc_response',
    'log_xtquant_call',
    'log_xtquant_result',
    'log_exception',
    'log_performance',
    'log_data_operation',
]
