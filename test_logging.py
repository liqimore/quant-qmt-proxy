"""
测试日志系统
运行此脚本验证日志配置是否正常工作
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import get_settings
from app.utils.helpers import setup_logging
from app.utils.logger import (
    get_logger,
    log_api_request,
    log_api_response,
    log_grpc_request,
    log_grpc_response,
    log_xtquant_call,
    log_xtquant_result,
    log_exception,
    log_performance,
    log_data_operation
)


def test_basic_logging():
    """测试基本日志功能"""
    print("\n=== 测试基本日志功能 ===")
    
    logger = get_logger(__name__)
    
    logger.debug("这是一条DEBUG日志")
    logger.info("这是一条INFO日志")
    logger.warning("这是一条WARNING日志")
    logger.error("这是一条ERROR日志")
    
    print("✓ 基本日志测试完成")


def test_structured_logging():
    """测试结构化日志"""
    print("\n=== 测试结构化日志 ===")
    
    # API请求日志
    log_api_request("GET", "/api/data/kline", {"stock_code": "000001.SZ"})
    log_api_response("/api/data/kline", 200, 123.45)
    
    # gRPC请求日志
    log_grpc_request("DataService", "GetKline", {"stock_code": "000001.SZ"})
    log_grpc_response("DataService", "GetKline", True, 234.56)
    
    # xtquant调用日志
    log_xtquant_call("get_market_data", {"stock_code": "000001.SZ"})
    log_xtquant_result("get_market_data", True, result={"data": "some_data"})
    log_xtquant_result("get_market_data", False, error="连接超时")
    
    # 性能日志
    log_performance("数据查询", 1234.5, threshold_ms=1000)
    log_performance("快速查询", 123.4, threshold_ms=1000)
    
    # 数据操作日志
    log_data_operation("获取K线数据", stock_code="000001.SZ", count=100)
    
    print("✓ 结构化日志测试完成")


def test_exception_logging():
    """测试异常日志"""
    print("\n=== 测试异常日志 ===")
    
    try:
        # 故意引发异常
        result = 1 / 0
    except Exception as e:
        log_exception(e, "除零错误测试")
    
    print("✓ 异常日志测试完成")


def test_context_logging():
    """测试上下文日志"""
    print("\n=== 测试上下文日志 ===")
    
    logger = get_logger(__name__)
    
    # 带上下文的日志
    logger.bind(user_id=123, request_id="abc-123").info("用户登录")
    logger.bind(order_id="ORD-001", stock_code="000001.SZ").info("下单成功")
    
    print("✓ 上下文日志测试完成")


def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("📝 日志系统测试")
    print("=" * 80)
    
    # 加载配置
    settings = get_settings()
    
    print(f"\n当前配置:")
    print(f"  日志级别: {settings.logging.level}")
    print(f"  主日志文件: {settings.logging.file}")
    print(f"  错误日志文件: {settings.logging.error_file}")
    print(f"  轮转大小: {settings.logging.rotation}")
    print(f"  保留时间: {settings.logging.retention}")
    print(f"  压缩格式: {settings.logging.compression}")
    print(f"  控制台输出: {settings.logging.console_output}")
    
    # 初始化日志系统
    setup_logging(
        log_level=settings.logging.level,
        log_file=settings.logging.file,
        error_file=settings.logging.error_file,
        log_format=settings.logging.format,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        compression=settings.logging.compression,
        console_output=settings.logging.console_output,
        backtrace=settings.logging.backtrace,
        diagnose=settings.logging.diagnose
    )
    
    # 运行测试
    test_basic_logging()
    test_structured_logging()
    test_exception_logging()
    test_context_logging()
    
    print("\n" + "=" * 80)
    print("✅ 所有日志测试完成！")
    print("=" * 80)
    print(f"\n请检查以下文件:")
    print(f"  • {settings.logging.file}")
    print(f"  • {settings.logging.error_file}")
    print("\n")


if __name__ == "__main__":
    main()
