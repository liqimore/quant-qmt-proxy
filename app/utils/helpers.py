"""
辅助函数模块
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "logs/app.log",
    error_file: Optional[str] = "logs/error.log",
    log_format: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "30 days",
    compression: str = "zip",
    console_output: bool = True,
    backtrace: bool = True,
    diagnose: bool = False
):
    """设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 主日志文件路径
        error_file: 错误日志文件路径 (只记录 ERROR 及以上级别)
        log_format: 日志格式字符串
        rotation: 日志轮转大小或时间 (如 "10 MB", "500 KB", "1 day")
        retention: 日志保留时间 (如 "30 days", "1 week")
        compression: 压缩格式 (zip, gz, tar.gz 等)
        console_output: 是否同时输出到控制台
        backtrace: 是否显示完整堆栈跟踪
        diagnose: 是否显示诊断信息
    """
    import sys
    import os
    from loguru import logger
    
    # 设置标准输出编码为 UTF-8 (Windows 兼容性)
    if sys.platform == 'win32':
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except Exception:
            pass  # 如果设置失败，继续使用默认编码
    
    # 移除默认处理器
    logger.remove()
    
    # 默认格式
    if log_format is None:
        log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    
    # 控制台格式（带颜色）
    console_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # 添加控制台输出
    if console_output:
        logger.add(
            sys.stdout,
            level=log_level,
            format=console_format,
            colorize=True,
            backtrace=backtrace,
            diagnose=diagnose
        )
    
    # 确保日志目录存在
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 添加主日志文件输出（所有级别）
        logger.add(
            log_file,
            level=log_level,
            format=log_format,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            backtrace=backtrace,
            diagnose=diagnose,
            enqueue=True  # 异步写入，提高性能
        )
    
    # 添加错误日志文件输出（仅 ERROR 及以上级别）
    if error_file:
        error_dir = os.path.dirname(error_file)
        if error_dir and not os.path.exists(error_dir):
            os.makedirs(error_dir, exist_ok=True)
        
        logger.add(
            error_file,
            level="ERROR",
            format=log_format,
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            backtrace=True,  # 错误日志总是显示完整堆栈
            diagnose=diagnose,
            enqueue=True
        )
    
    # 拦截标准 logging 模块的日志，重定向到 loguru
    # 这样 uvicorn 和其他使用标准 logging 的库也会输出到文件
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # 获取对应的 loguru 级别
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            # 找到调用者的帧
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
    
    # 配置标准 logging 使用拦截器
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 为常见的日志记录器设置拦截
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
    
    return logger


def format_response(
    data: Any = None,
    message: str = "success",
    success: bool = True,
    code: int = 200
) -> Dict[str, Any]:
    """格式化API响应"""
    response = {
        "success": success,
        "message": message,
        "code": code,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def serialize_data(data: Any) -> Any:
    """序列化数据，处理特殊类型"""
    if isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [serialize_data(item) for item in data]
    else:
        return data


def validate_stock_code(stock_code: str) -> bool:
    """验证股票代码格式
    支持格式:
    - A股: 000001.SZ, 600000.SH
    - 港股: 00700.HK
    - 期货等其他格式
    """
    if not stock_code or not isinstance(stock_code, str):
        return False
    
    stock_code = stock_code.strip().upper()
    
    # 检查是否包含市场后缀
    if '.' in stock_code:
        parts = stock_code.split('.')
        if len(parts) != 2:
            return False
        code, market = parts
        
        # 验证代码部分是否为数字
        if not code.isdigit():
            return False
        
        # 验证市场代码
        valid_markets = ['SH', 'SZ', 'BJ', 'HK', 'US']  # 上海、深圳、北京、香港、美国
        if market not in valid_markets:
            return False
        
        # A股代码应该是6位数字
        if market in ['SH', 'SZ', 'BJ'] and len(code) != 6:
            return False
        
        return True
    else:
        # 没有市场后缀，只检查是否为数字且长度合理
        if not stock_code.isdigit():
            return False
        if len(stock_code) < 4 or len(stock_code) > 8:
            return False
        return True


def validate_date_range(start_date: str, end_date: str) -> bool:
    """验证日期范围"""
    try:
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        return start <= end
    except ValueError:
        return False


def parse_date_string(date_str: str) -> Optional[datetime]:
    """解析日期字符串"""
    formats = ["%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    return dictionary.get(key, default) if dictionary else default
