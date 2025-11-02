"""
辅助函数模块
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


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
