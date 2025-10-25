"""
REST API 测试共享 fixtures

本文件定义了所有 REST API 测试共享的 fixtures 和配置
"""

import pytest
import logging
import httpx
from typing import Dict, Any, Generator
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 导入测试配置
from tests.rest.config import (
    BASE_URL,
    API_KEY,
    DEFAULT_TIMEOUT,
    CONNECT_TIMEOUT,
    READ_TIMEOUT,
    SKIP_INTEGRATION_TESTS,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE,
    TEST_ACCOUNT_ID,
    TEST_ACCOUNT_PASSWORD,
    TEST_ACCOUNT_TYPE,
)


# ==================== 日志配置 ====================

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """配置测试日志"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("开始 REST API 测试")
    logger.info("=" * 80)
    yield
    logger.info("=" * 80)
    logger.info("REST API 测试完成")
    logger.info("=" * 80)


# ==================== HTTP 客户端 Fixtures ====================

@pytest.fixture(scope="session")
def base_url() -> str:
    """REST API 基础 URL"""
    return BASE_URL


@pytest.fixture(scope="session")
def api_key() -> str:
    """API 认证密钥"""
    return API_KEY


@pytest.fixture(scope="session")
def api_headers(api_key: str) -> Dict[str, str]:
    """API 请求头"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def http_client(base_url: str, api_headers: Dict[str, str]) -> Generator[httpx.Client, None, None]:
    """
    HTTP 客户端（会话级别，所有测试共享）
    
    使用 scope="session" 以提高测试性能，复用连接
    """
    logger = logging.getLogger(__name__)
    logger.info(f"创建 HTTP 客户端: {base_url}")
    
    client = httpx.Client(
        base_url=base_url,
        headers=api_headers,
        timeout=httpx.Timeout(
            connect=CONNECT_TIMEOUT,
            read=READ_TIMEOUT,
            write=DEFAULT_TIMEOUT,
            pool=DEFAULT_TIMEOUT
        ),
        limits=httpx.Limits(
            max_connections=100,
            max_keepalive_connections=20
        )
    )
    
    yield client
    
    logger.info("关闭 HTTP 客户端")
    client.close()


@pytest.fixture(scope="function")
def http_client_per_test(base_url: str, api_headers: Dict[str, str]) -> Generator[httpx.Client, None, None]:
    """
    HTTP 客户端（函数级别，每个测试独立）
    
    用于需要隔离的测试
    """
    client = httpx.Client(
        base_url=base_url,
        headers=api_headers,
        timeout=DEFAULT_TIMEOUT
    )
    
    yield client
    
    client.close()


# ==================== 健康检查 Fixtures ====================

@pytest.fixture(scope="session", autouse=True)
def check_rest_server_health(http_client: httpx.Client):
    """
    检查 REST API 服务器健康状态
    
    在所有测试开始前自动执行
    """
    if SKIP_INTEGRATION_TESTS:
        return
    
    logger = logging.getLogger(__name__)
    
    try:
        response = http_client.get("/health/", timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ REST API 服务器健康检查通过")
        else:
            logger.warning(f"⚠️ REST API 服务器状态异常: {response.status_code}")
            pytest.skip("REST API 服务器不可用")
    except httpx.ConnectError:
        logger.error("❌ 健康检查失败: 无法连接到服务器")
        pytest.skip("无法连接到 REST API 服务器")
    except Exception as e:
        logger.error(f"❌ 健康检查失败: {e}")
        pytest.skip("REST API 服务器健康检查失败")


# ==================== 交易会话 Fixtures ====================

@pytest.fixture(scope="function")
def test_session(http_client: httpx.Client) -> Generator[str, None, None]:
    """
    测试交易会话（函数级别 - 每个测试独立）
    
    自动连接账户，测试完成后自动断开
    """
    if SKIP_INTEGRATION_TESTS:
        pytest.skip("集成测试已禁用（SKIP_INTEGRATION_TESTS=True）")
        return
    
    logger = logging.getLogger(__name__)
    
    # 连接账户
    connect_data = {
        "account_id": TEST_ACCOUNT_ID,
        "password": TEST_ACCOUNT_PASSWORD,
        "account_type": TEST_ACCOUNT_TYPE
    }
    
    try:
        response = http_client.post("/api/v1/trading/connect", json=connect_data)
        
        if response.status_code == 200:
            result = response.json()
            # 从响应中获取 session_id，可能在根级别或 data 字段中
            session_id = result.get("session_id")
            if not session_id and "data" in result:
                session_id = result["data"].get("session_id")
            
            if session_id:
                logger.info(f"✅ 测试账户连接成功: {session_id}")
                yield session_id
                
                # 清理：断开连接
                try:
                    disconnect_response = http_client.post(f"/api/v1/trading/disconnect/{session_id}")
                    if disconnect_response.status_code == 200:
                        logger.info(f"✅ 测试账户已断开: {session_id}")
                except Exception as e:
                    logger.warning(f"⚠️ 断开连接时出错: {e}")
            else:
                logger.error(f"❌ 响应中未找到 session_id: {result}")
                pytest.skip("响应中未找到 session_id")
        else:
            logger.error(f"❌ 连接请求失败: HTTP {response.status_code}, {response.text}")
            pytest.skip("连接测试账户失败")
    except Exception as e:
        logger.error(f"❌ 连接异常: {e}")
        pytest.skip("连接测试账户时发生错误")


# ==================== 测试数据 Fixtures ====================

@pytest.fixture
def sample_stock_codes():
    """示例股票代码"""
    from tests.rest.config import TEST_STOCK_CODES
    return TEST_STOCK_CODES


@pytest.fixture
def sample_index_codes():
    """示例指数代码"""
    from tests.rest.config import TEST_INDEX_CODES
    return TEST_INDEX_CODES


@pytest.fixture
def sample_sector_names():
    """示例板块名称"""
    from tests.rest.config import TEST_SECTOR_NAMES
    return TEST_SECTOR_NAMES


@pytest.fixture
def sample_date_range():
    """示例日期范围"""
    from tests.rest.config import TEST_START_DATE, TEST_END_DATE
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
def assert_response_success():
    """断言响应成功"""
    def _assert(response: httpx.Response, expected_status: int = 200):
        """断言 HTTP 响应成功"""
        assert response.status_code == expected_status, \
            f"请求失败: HTTP {response.status_code}, {response.text[:200]}"
        
        if response.status_code == 200:
            result = response.json()
            # 某些端点可能没有 success 字段
            if "success" in result:
                assert result.get("success") is not False, \
                    f"API 返回失败: {result.get('message', 'Unknown error')}"
        
        return response
    
    return _assert


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


def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "integration: 标记为集成测试（需要真实服务）"
    )
    config.addinivalue_line(
        "markers", "slow: 标记为慢速测试"
    )
    config.addinivalue_line(
        "markers", "performance: 标记为性能测试"
    )


def pytest_report_header(config):
    """添加测试报告头部信息"""
    return [
        f"REST API Server: {BASE_URL}",
        f"Skip Integration Tests: {SKIP_INTEGRATION_TESTS}",
        f"Test Account: {TEST_ACCOUNT_ID}",
        f"Default Timeout: {DEFAULT_TIMEOUT}s"
    ]
