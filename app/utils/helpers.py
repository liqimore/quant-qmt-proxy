"""
辅助函数模块
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """设置日志配置"""
    import sys
    from loguru import logger
    
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 添加文件输出（如果指定）
    if log_file:
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days"
        )


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
    """验证股票代码格式"""
    if not stock_code or not isinstance(stock_code, str):
        return False
    
    # 基本格式验证（可根据实际需求调整）
    stock_code = stock_code.strip().upper()
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
