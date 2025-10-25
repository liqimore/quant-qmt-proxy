"""
全局测试配置和共享 fixtures

本文件定义了整个测试框架的全局配置和共享 fixtures
"""

import pytest
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ==================== 全局日志配置 ====================

@pytest.fixture(scope="session", autouse=True)
def configure_global_logging():
    """配置全局测试日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('tests/test_results.log')
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("=" * 100)
    logger.info("QMT Proxy 测试框架启动")
    logger.info("=" * 100)
    yield
    logger.info("=" * 100)
    logger.info("QMT Proxy 测试框架完成")
    logger.info("=" * 100)


# ==================== 全局测试数据 fixtures ====================

@pytest.fixture(scope="session")
def global_stock_codes():
    """全局示例股票代码"""
    return [
        "000001.SZ",  # 平安银行
        "600000.SH",  # 浦发银行
        "000002.SZ",  # 万科A
        "600519.SH",  # 贵州茅台
    ]


@pytest.fixture(scope="session")
def global_index_codes():
    """全局示例指数代码"""
    return [
        "000001.SH",  # 上证指数
        "000300.SH",  # 沪深300
        "399001.SZ",  # 深证成指
        "399006.SZ",  # 创业板指
    ]


@pytest.fixture(scope="session")
def global_sector_names():
    """全局示例板块名称"""
    return [
        "银行",
        "证券",
        "保险",
    ]


# ==================== pytest 钩子函数 ====================

def pytest_configure(config):
    """pytest 全局配置钩子"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "rest: REST API 测试"
    )
    config.addinivalue_line(
        "markers", "grpc: gRPC 测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试（需要真实服务）"
    )
    config.addinivalue_line(
        "markers", "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "future: 未来实现的功能"
    )


def pytest_collection_modifyitems(config, items):
    """
    修改测试收集项
    
    自动为测试添加标记
    """
    for item in items:
        # 根据路径自动添加标记
        if "rest" in str(item.fspath):
            item.add_marker(pytest.mark.rest)
        if "grpc" in str(item.fspath):
            item.add_marker(pytest.mark.grpc)


def pytest_report_header(config):
    """添加测试报告头部信息"""
    return [
        "QMT Proxy 测试框架",
        "=" * 80,
        "测试类型: REST API + gRPC",
        "Python 版本: " + sys.version.split()[0],
    ]


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
            logger.error(f"   错误信息: {str(rep.longrepr)[:200]}")
