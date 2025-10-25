"""
pytest 配置文件 - 共享 fixtures 和测试配置

本文件定义了所有 gRPC 测试共享的 fixtures 和配置
"""

import pytest
import logging
from typing import Generator
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入测试配置
from tests.grpc.config import (
    GRPC_SERVER_ADDRESS,
    DEFAULT_TIMEOUT,
    SKIP_INTEGRATION_TESTS,
    LOG_LEVEL,
    LOG_FORMAT,
    TEST_ACCOUNT_ID,
    TEST_ACCOUNT_PASSWORD,
    TEST_CLIENT_ID,
)

# TODO: proto 生成后取消注释
# import grpc
# from generated import data_pb2, data_pb2_grpc
# from generated import trading_pb2, trading_pb2_grpc
# from generated import health_pb2, health_pb2_grpc


# ==================== 日志配置 ====================

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """配置测试日志"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('tests/grpc/test_results.log')
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("开始 gRPC 测试")
    logger.info("=" * 80)
    yield
    logger.info("=" * 80)
    logger.info("gRPC 测试完成")
    logger.info("=" * 80)


# ==================== gRPC 连接 Fixtures ====================

@pytest.fixture(scope="session")
def grpc_server_address():
    """gRPC 服务器地址"""
    return GRPC_SERVER_ADDRESS


@pytest.fixture(scope="session")
def grpc_channel(grpc_server_address):
    """
    创建 gRPC 连接通道（会话级别，所有测试共享）
    
    使用 scope="session" 以提高测试性能，避免频繁建立连接
    """
    # TODO: proto 生成后取消注释
    # logger = logging.getLogger(__name__)
    # logger.info(f"建立 gRPC 连接: {grpc_server_address}")
    # 
    # channel = grpc.insecure_channel(
    #     grpc_server_address,
    #     options=[
    #         ('grpc.max_send_message_length', 50 * 1024 * 1024),
    #         ('grpc.max_receive_message_length', 50 * 1024 * 1024),
    #         ('grpc.keepalive_time_ms', 10000),
    #         ('grpc.keepalive_timeout_ms', 5000),
    #     ]
    # )
    # 
    # # 等待连接就绪
    # try:
    #     grpc.channel_ready_future(channel).result(timeout=10)
    #     logger.info("gRPC 连接就绪")
    # except grpc.FutureTimeoutError:
    #     logger.error("gRPC 连接超时")
    #     pytest.skip("无法连接到 gRPC 服务器")
    # 
    # yield channel
    # 
    # logger.info("关闭 gRPC 连接")
    # channel.close()
    
    # 临时占位
    yield None


@pytest.fixture(scope="class")
def grpc_channel_per_class(grpc_server_address):
    """
    创建 gRPC 连接通道（类级别，每个测试类一个连接）
    
    用于需要独立连接的测试类
    """
    # TODO: 实现
    yield None


# ==================== Stub Fixtures ====================

@pytest.fixture(scope="session")
def data_stub(grpc_channel):
    """数据服务 stub（会话级别）"""
    # TODO: proto 生成后取消注释
    # if grpc_channel is None:
    #     pytest.skip("gRPC 连接不可用")
    # return data_pb2_grpc.DataServiceStub(grpc_channel)
    return None


@pytest.fixture(scope="session")
def trading_stub(grpc_channel):
    """交易服务 stub（会话级别）"""
    # TODO: proto 生成后取消注释
    # if grpc_channel is None:
    #     pytest.skip("gRPC 连接不可用")
    # return trading_pb2_grpc.TradingServiceStub(grpc_channel)
    return None


@pytest.fixture(scope="session")
def health_stub(grpc_channel):
    """健康检查服务 stub（会话级别）"""
    # TODO: proto 生成后取消注释
    # if grpc_channel is None:
    #     pytest.skip("gRPC 连接不可用")
    # return health_pb2_grpc.HealthStub(grpc_channel)
    return None


# ==================== 健康检查 Fixtures ====================

@pytest.fixture(scope="session", autouse=False)  # 改为 False，不自动运行
def check_grpc_server_health():
    """
    检查 gRPC 服务器健康状态
    
    注意：已禁用自动运行，避免 fixture scope 冲突
    """
    if SKIP_INTEGRATION_TESTS:
        return
    
    # 简单实现，不依赖其他 fixtures
    from tests.grpc.client import GRPCTestClient
    try:
        with GRPCTestClient() as client:
            response = client.check_health()
            from generated import health_pb2
            if response.status == health_pb2.HealthCheckResponse.SERVING:
                return True
    except Exception:
        pytest.skip("无法连接到 gRPC 服务器")


# ==================== 交易会话 Fixtures ====================

@pytest.fixture(scope="class")
def test_session(trading_stub):
    """
    测试交易会话（类级别）
    
    自动连接账户，测试完成后自动断开
    """
    if SKIP_INTEGRATION_TESTS:
        yield "test_session_id"
        return
    
    # TODO: proto 生成后取消注释
    # logger = logging.getLogger(__name__)
    # 
    # # 连接账户
    # request = trading_pb2.ConnectRequest(
    #     account_id=TEST_ACCOUNT_ID,
    #     password=TEST_ACCOUNT_PASSWORD,
    #     client_id=TEST_CLIENT_ID
    # )
    # 
    # try:
    #     response = trading_stub.Connect(request, timeout=CONNECT_TIMEOUT)
    #     
    #     if response.success:
    #         session_id = response.session_id
    #         logger.info(f"✅ 测试账户连接成功: {session_id}")
    #         yield session_id
    #         
    #         # 清理：断开连接
    #         disconnect_request = trading_pb2.DisconnectRequest(
    #             session_id=session_id
    #         )
    #         disconnect_response = trading_stub.Disconnect(disconnect_request)
    #         if disconnect_response.success:
    #             logger.info("✅ 测试账户已断开")
    #     else:
    #         logger.error(f"❌ 测试账户连接失败: {response.message}")
    #         pytest.skip("无法连接测试账户")
    # except grpc.RpcError as e:
    #     logger.error(f"❌ 连接异常: {e}")
    #     pytest.skip("连接测试账户时发生错误")
    
    # 临时占位
    yield "test_session_id"


# ==================== 测试数据 Fixtures ====================

@pytest.fixture
def sample_stock_codes():
    """示例股票代码"""
    from tests.grpc.config import TEST_STOCK_CODES
    return TEST_STOCK_CODES


@pytest.fixture
def sample_index_codes():
    """示例指数代码"""
    from tests.grpc.config import TEST_INDEX_CODES
    return TEST_INDEX_CODES


@pytest.fixture
def sample_date_range():
    """示例日期范围"""
    from tests.grpc.config import TEST_START_DATE, TEST_END_DATE
    return {
        'start_date': TEST_START_DATE,
        'end_date': TEST_END_DATE
    }


# ==================== 性能测试 Fixtures ====================

@pytest.fixture
def performance_timer():
    """性能计时器"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.elapsed_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            if self.start_time is None:
                raise RuntimeError("Timer not started")
            self.elapsed_time = time.time() - self.start_time
            return self.elapsed_time
        
        def elapsed_ms(self):
            if self.elapsed_time is None:
                raise RuntimeError("Timer not stopped")
            return self.elapsed_time * 1000
    
    return Timer()


# ==================== 辅助工具 Fixtures ====================

@pytest.fixture
def mock_order_generator():
    """模拟订单生成器（用于批量测试）"""
    def generate_orders(count=10, stock_code="000001.SZ"):
        """生成指定数量的模拟订单"""
        orders = []
        for i in range(count):
            order = {
                'stock_code': stock_code,
                'side': 'BUY' if i % 2 == 0 else 'SELL',
                'order_type': 'LIMIT',
                'volume': 100,
                'price': 10.0 + i * 0.1
            }
            orders.append(order)
        return orders
    
    return generate_orders


# ==================== pytest Hooks ====================

def pytest_collection_modifyitems(config, items):
    """
    修改测试项，添加标记
    
    自动跳过集成测试（如果配置了 SKIP_INTEGRATION_TESTS）
    """
    if SKIP_INTEGRATION_TESTS:
        skip_integration = pytest.mark.skip(reason="集成测试已禁用（SKIP_INTEGRATION_TESTS=True）")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
    
    # 自动为未实现的接口添加 skip 标记
    skip_future = pytest.mark.skip(reason="功能尚未实现")
    for item in items:
        if "future" in item.keywords:
            item.add_marker(skip_future)


def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "integration: 标记为集成测试"
    )
    config.addinivalue_line(
        "markers", "future: 标记为未来实现的功能"
    )


def pytest_report_header(config):
    """添加测试报告头部信息"""
    return [
        f"gRPC Server: {GRPC_SERVER_ADDRESS}",
        f"Skip Integration Tests: {SKIP_INTEGRATION_TESTS}",
        f"Test Account: {TEST_ACCOUNT_ID}",
        f"Default Timeout: {DEFAULT_TIMEOUT}s"
    ]


# ==================== 测试结果统计 ====================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    outcome = yield
    rep = outcome.get_result()
    
    # 记录失败的测试
    if rep.when == "call" and rep.failed:
        logger = logging.getLogger(__name__)
        logger.error(f"❌ 测试失败: {item.nodeid}")
        if hasattr(rep, 'longrepr'):
            logger.error(f"   错误信息: {rep.longrepr}")
