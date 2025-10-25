# REST API 测试说明

本目录包含针对 QMT Proxy REST API 接口的完整测试套件。

## 📁 文件结构

```
tests/rest/
├── __init__.py                      # 测试模块初始化
├── config.py                        # 测试配置文件
├── conftest.py                      # 共享 fixtures
├── client.py                        # HTTP 客户端封装
├── test_health_api.py              # 健康检查接口测试
├── test_data_api.py                # 数据服务接口测试
├── test_trading_api.py             # 交易服务接口测试
└── README.md                        # 本文件
```

## 🎯 测试覆盖范围

### 健康检查接口 (test_health_api.py)

- `GET /` - 根路径
- `GET /info` - 应用信息
- `GET /health/` - 健康检查
- `GET /health/ready` - 就绪检查
- `GET /health/live` - 存活检查

### 数据服务接口 (test_data_api.py)

- `POST /api/v1/data/market` - 获取市场数据
- `GET /api/v1/data/sectors` - 获取板块列表
- `POST /api/v1/data/sector` - 获取板块股票
- `POST /api/v1/data/index-weight` - 获取指数权重
- `GET /api/v1/data/trading-calendar/{year}` - 获取交易日历
- `GET /api/v1/data/instrument/{stock_code}` - 获取合约信息
- `POST /api/v1/data/financial` - 获取财务数据

### 交易服务接口 (test_trading_api.py)

- `POST /api/v1/trading/connect` - 连接交易账户
- `POST /api/v1/trading/disconnect/{session_id}` - 断开账户
- `GET /api/v1/trading/account/{session_id}` - 获取账户信息
- `GET /api/v1/trading/positions/{session_id}` - 获取持仓信息
- `GET /api/v1/trading/asset/{session_id}` - 获取资产信息
- `GET /api/v1/trading/risk/{session_id}` - 获取风险信息
- `GET /api/v1/trading/strategies/{session_id}` - 获取策略列表
- `GET /api/v1/trading/orders/{session_id}` - 获取订单列表
- `GET /api/v1/trading/trades/{session_id}` - 获取成交记录
- `POST /api/v1/trading/order/{session_id}` - 提交订单
- `POST /api/v1/trading/cancel/{session_id}` - 撤销订单

## 🚀 运行测试

### 前置条件

1. **安装依赖**
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

2. **启动 REST API 服务器**
   ```bash
   # 方式1: 仅 REST
   python run.py

   # 方式2: 混合模式 (REST + gRPC)
   python run_hybrid.py
   ```

### 运行所有测试

```bash
# 运行所有 REST 测试
pytest tests/rest/ -v

# 运行所有测试并显示详细输出
pytest tests/rest/ -v -s

# 运行所有测试（包括跳过的）
pytest tests/rest/ -v -rs
```

### 运行特定测试

```bash
# 只运行健康检查测试
pytest tests/rest/test_health_api.py -v

# 只运行数据服务测试
pytest tests/rest/test_data_api.py -v

# 只运行交易服务测试
pytest tests/rest/test_trading_api.py -v

# 运行特定测试类
pytest tests/rest/test_data_api.py::TestDataAPI -v

# 运行特定测试方法
pytest tests/rest/test_data_api.py::TestDataAPI::test_get_market_data -v
```

### 运行性能测试

```bash
# 运行性能测试
pytest tests/rest/ -v -k "performance"

# 查看最慢的 10 个测试
pytest tests/rest/ -v --durations=10
```

### 查看测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/rest/ --cov=app --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

## 🔧 配置测试

编辑 `tests/rest/config.py` 文件来修改测试配置：

```python
# REST API 服务器地址
BASE_URL = "http://localhost:8000"

# API 认证密钥
API_KEY = "dev-api-key-001"

# 测试账户（用于集成测试）
TEST_ACCOUNT_ID = "your_account"
TEST_ACCOUNT_PASSWORD = "your_password"

# 是否跳过集成测试
# false: 运行完整集成测试（需要真实账户连接）
# true: 使用模拟数据，测试将收到预期的 400 错误
SKIP_INTEGRATION_TESTS = False  # 默认运行集成测试
```

**重要说明**:
- 当 `SKIP_INTEGRATION_TESTS=False` 时，测试会实际连接账户并进行真实操作
- 当 `SKIP_INTEGRATION_TESTS=True` 时，测试使用模拟 session_id，会收到 "账户未连接" 的 400 错误（这是预期行为）

## 📝 测试开发指南

### 编写新测试用例

```python
import pytest
from httpx import Client

class TestNewFeature:
    """测试新功能"""
    
    def test_new_endpoint(self, http_client: Client):
        """测试新端点"""
        response = http_client.get("/api/v1/new-endpoint")
        
        assert response.status_code == 200
        result = response.json()
        assert result.get("success") is True
        # 添加更多断言...
```

### 使用 fixtures

```python
def test_with_session(self, http_client: Client, test_session: str):
    """使用测试会话"""
    response = http_client.get(f"/api/v1/trading/account/{test_session}")
    assert response.status_code == 200
```

### 测试标记

使用 pytest 标记来组织测试：

```python
@pytest.mark.slow
def test_slow_operation(self):
    """标记为慢速测试"""
    pass

@pytest.mark.integration
def test_real_connection(self):
    """标记为集成测试"""
    pass

@pytest.mark.performance
def test_performance(self):
    """标记为性能测试"""
    pass
```

运行特定标记的测试：
```bash
pytest tests/rest/ -v -m "not slow"      # 跳过慢速测试
pytest tests/rest/ -v -m integration     # 只运行集成测试
pytest tests/rest/ -v -m performance     # 只运行性能测试
```

## 🐛 调试测试

### 查看详细输出

```bash
# 显示 print 输出
pytest tests/rest/ -v -s

# 显示更详细的错误信息
pytest tests/rest/ -v --tb=long

# 在第一个失败时停止
pytest tests/rest/ -v -x
```

### 使用调试器

```python
def test_debug_example(self):
    """调试示例"""
    import pdb; pdb.set_trace()  # 设置断点
    # ... 测试代码 ...
```

然后运行：
```bash
pytest tests/rest/test_data_api.py::test_debug_example -v -s
```

## 📊 测试报告

### 生成 HTML 报告

```bash
# 安装 pytest-html
pip install pytest-html

# 生成报告
pytest tests/rest/ -v --html=report.html --self-contained-html
```

### 生成 JUnit XML 报告（CI/CD）

```bash
pytest tests/rest/ -v --junitxml=junit.xml
```

## ⚡ 性能基准

### 预期性能指标

| 操作 | 目标延迟 | 说明 |
|------|---------|------|
| 健康检查 | < 100ms | 简单状态查询 |
| 单股行情查询 | < 500ms | 小数据量查询 |
| 批量行情查询 | < 2s | 50只股票 |
| 财务数据查询 | < 1s | 单只股票，多张表 |
| 提交订单 | < 1s | 单笔订单 |
| 查询持仓 | < 500ms | 当前持仓 |
| 查询订单 | < 500ms | 当日订单 |

## 🔍 常见问题

### Q1: 测试失败提示连接超时

**A:** 确保 REST API 服务器已启动：
```bash
python run.py
```

并检查配置文件中的服务器地址是否正确。

### Q2: 认证失败

**A:** 检查 `config.py` 中的 `API_KEY` 是否与服务器配置一致。

### Q3: 所有测试都被跳过

**A:** 检查 `config.py` 中的 `SKIP_INTEGRATION_TESTS` 设置。

### Q4: 导入模块失败

**A:** 确保项目根目录在 Python 路径中：
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📚 相关文档

- [pytest 官方文档](https://docs.pytest.org/)
- [httpx 文档](https://www.python-httpx.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [项目总体测试文档](../README.md)

## 🤝 贡献指南

1. 为新功能编写测试
2. 确保所有测试通过
3. 更新测试文档
4. 提交 Pull Request

---

**最后更新**: 2025-10-25  
**维护者**: Development Team
