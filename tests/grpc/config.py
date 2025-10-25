"""
gRPC 测试配置文件

用于配置 gRPC 测试的服务器地址、超时时间等参数
"""

# gRPC 服务器配置
GRPC_SERVER_HOST = "localhost"
GRPC_SERVER_PORT = 50051
GRPC_SERVER_ADDRESS = f"{GRPC_SERVER_HOST}:{GRPC_SERVER_PORT}"

# 超时配置（秒）
DEFAULT_TIMEOUT = 30
CONNECT_TIMEOUT = 10
ORDER_TIMEOUT = 5
QUERY_TIMEOUT = 10

# 测试账户配置（用于集成测试）
TEST_ACCOUNT_ID = "test_account"
TEST_ACCOUNT_PASSWORD = "test_password"
TEST_CLIENT_ID = 1

# 测试数据配置
TEST_STOCK_CODES = [
    "000001.SZ",  # 平安银行
    "600000.SH",  # 浦发银行
    "000002.SZ",  # 万科A
    "600519.SH",  # 贵州茅台
]

TEST_INDEX_CODES = [
    "000300.SH",  # 沪深300
    "000016.SH",  # 上证50
    "399006.SZ",  # 创业板指
]

# 测试日期范围
TEST_START_DATE = "20240101"
TEST_END_DATE = "20240131"

# 性能测试配置
PERFORMANCE_TEST_ITERATIONS = 100
PERFORMANCE_TEST_CONCURRENT_WORKERS = 10
MAX_ACCEPTABLE_LATENCY_MS = 100  # 毫秒

# 批量操作配置
BATCH_SIZE = 50

# 是否跳过需要真实连接的测试
SKIP_INTEGRATION_TESTS = True  # 设置为 False 以运行集成测试

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
