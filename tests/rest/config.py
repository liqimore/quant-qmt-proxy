"""
REST API 测试配置文件
"""
import os
from typing import List

# ==================== 服务器配置 ====================

# REST API 基础 URL
BASE_URL = os.getenv("REST_API_BASE_URL", "http://localhost:8000")

# API 认证
API_KEY = os.getenv("REST_API_KEY", "dev-api-key-001")

# 请求超时设置
DEFAULT_TIMEOUT = 60  # 默认超时（秒）
CONNECT_TIMEOUT = 10  # 连接超时（秒）
READ_TIMEOUT = 30     # 读取超时（秒）

# ==================== 测试控制 ====================

# 是否跳过集成测试（需要真实服务运行）
SKIP_INTEGRATION_TESTS = os.getenv("SKIP_INTEGRATION_TESTS", "true").lower() == "true"

# 是否跳过慢速测试
SKIP_SLOW_TESTS = os.getenv("SKIP_SLOW_TESTS", "false").lower() == "true"

# ==================== 测试账户配置 ====================

# 测试交易账户（用于集成测试）
TEST_ACCOUNT_ID = os.getenv("TEST_ACCOUNT_ID", "test_account_001")
TEST_ACCOUNT_PASSWORD = os.getenv("TEST_ACCOUNT_PASSWORD", "test_password")
TEST_ACCOUNT_TYPE = "SECURITY"

# ==================== 测试数据配置 ====================

# 测试股票代码
TEST_STOCK_CODES: List[str] = [
    "000001.SZ",  # 平安银行
    "600000.SH",  # 浦发银行
    "000002.SZ",  # 万科A
    "600519.SH",  # 贵州茅台
]

# 测试指数代码
TEST_INDEX_CODES: List[str] = [
    "000001.SH",  # 上证指数
    "000300.SH",  # 沪深300
    "399001.SZ",  # 深证成指
    "399006.SZ",  # 创业板指
]

# 测试板块名称
TEST_SECTOR_NAMES: List[str] = [
    "银行",
    "证券",
    "保险",
]

# 测试日期范围
TEST_START_DATE = "20240101"
TEST_END_DATE = "20241231"

# ==================== 日志配置 ====================

# 日志级别
LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", "INFO")

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 日志文件路径
LOG_FILE = "tests/rest/test_results.log"

# ==================== 性能测试配置 ====================

# 性能基准（毫秒）
PERFORMANCE_BENCHMARKS = {
    "health_check": 3000,         # 健康检查 < 3s
    "single_stock_data": 3000,    # 单股行情 < 3s
    "batch_stock_data": 5000,     # 批量行情 < 5s
    "financial_data": 3000,       # 财务数据 < 3s
    "submit_order": 2000,         # 提交订单 < 2s
    "query_positions": 2000,      # 查询持仓 < 2s
}

# 并发测试配置
CONCURRENT_REQUESTS = 10  # 并发请求数
CONCURRENT_TIMEOUT = 30   # 并发测试超时（秒）
