# gRPC 测试用例说明

本目录包含针对 QMT Proxy gRPC 接口的完整测试套件。

## 📁 文件结构

```
tests/grpc/
├── __init__.py                      # 测试模块初始化
├── config.py                        # 测试配置文件
├── conftest.py                      # 共享 fixtures
├── client.py                        # gRPC 客户端封装
├── test_health_grpc_service.py     # 健康检查服务测试
├── test_data_grpc_service.py       # 数据服务测试用例
├── test_trading_grpc_service.py    # 交易服务测试用例
└── README.md                        # 本文件
```

## 🎯 测试覆盖范围

### 健康检查服务测试 (test_health_grpc_service.py)

#### ✅ 已实现接口测试 (2个)
1. **check_health()** - 健康检查
   - 全局健康检查
   - 特定服务健康检查

2. **watch_health()** - 健康状态订阅（流式）
   - 实时健康状态监控

### 数据服务测试 (test_data_grpc_service.py)

#### ✅ 已实现接口测试 (9个)
1. **get_market_data()** - 获取行情数据
   - 单只股票查询
   - 多只股票批量查询
   - 不同周期查询（1分钟、5分钟、日线等）
   - 复权数据查询（前复权、后复权、不复权）

2. **get_financial_data()** - 获取财务数据
   - 单张财务报表查询
   - 多张报表批量查询

3. **get_sector_list()** - 获取板块列表
   - 所有板块查询
   - 按类型查询（行业、概念、地域）

4. **get_stock_list_in_sector()** - 获取板块成分股
   - 板块成分股查询

5. **get_index_weight()** - 获取指数权重
   - 指定日期查询
   - 最新权重查询

6. **get_trading_calendar()** - 获取交易日历
   - 按年份查询
   - 当前年份查询

7. **get_instrument_info()** - 获取合约信息
   - 单个合约查询
   - 批量合约查询

8. **get_etf_info()** - 获取ETF信息
   - ETF基础信息查询

#### 🔄 流式接口测试（未来实现）
- **subscribe_market_data()** - 订阅实时行情（服务端流）
- **unsubscribe_market_data()** - 取消订阅

#### ⏳ 未实现接口占位
- Level2数据接口
- 数据下载接口
- 板块管理接口
- 节假日数据接口
- 可转债接口
- 新股申购接口

### 交易服务测试 (test_trading_grpc_service.py)

#### ✅ 已实现接口测试 (6个)
1. **connect()** - 连接交易账户
   - 成功连接测试
   - 无效凭证测试

2. **disconnect()** - 断开账户
   - 正常断开测试
   - 无效会话测试

3. **get_account_info()** - 获取账户信息
   - 账户资产查询

4. **order_stock()** - 提交订单
   - 买入订单
   - 卖出订单
   - 限价单
   - 市价单

5. **cancel_order_stock()** - 撤销订单
   - 撤销已提交订单
   - 撤销不存在订单（错误处理）

6. **query_stock_positions()** - 查询持仓
   - 空持仓查询
   - 有持仓查询
   - 数据结构验证

7. **query_stock_orders()** - 查询订单
   - 查询所有订单
   - 按日期范围查询
   - 订单结构验证

#### 🔄 流式接口测试（未来实现）
- **submit_batch_orders()** - 批量提交订单（客户端流）
- **subscribe_order_status()** - 订阅订单状态（双向流）

#### ⏳ 未实现接口占位
- 资产查询接口
- 成交查询接口
- 异步交易接口
- 信用交易接口
- 资金划拨接口
- 银证转账接口
- 新股申购接口
- 约券接口

## 🚀 运行测试

### 前置条件

1. **安装依赖**
   ```bash
   pip install pytest pytest-asyncio grpcio grpcio-tools protobuf
   ```

2. **生成 protobuf 代码**
   ```bash
   python scripts/generate_proto.py
   ```

3. **启动 gRPC 服务器**
   ```bash
   # 方式1: 仅 gRPC
   python run_grpc.py

   # 方式2: 混合模式 (REST + gRPC)
   python run_hybrid.py
   ```

### 运行所有测试

```bash
# 运行所有 gRPC 测试
pytest tests/grpc/ -v

# 运行所有测试（包括跳过的）
pytest tests/grpc/ -v -rs

# 运行所有测试并显示详细输出
pytest tests/grpc/ -v -s
```

### 运行特定测试

```bash
# 只运行数据服务测试
pytest tests/grpc/test_data_grpc_service.py -v

# 只运行交易服务测试
pytest tests/grpc/test_trading_grpc_service.py -v

# 运行特定测试类
pytest tests/grpc/test_data_grpc_service.py::TestDataGrpcService::TestImplementedApis -v

# 运行特定测试方法
pytest tests/grpc/test_data_grpc_service.py::TestDataGrpcService::TestImplementedApis::test_get_market_data_single_stock -v
```

### 运行性能测试

```bash
# 运行性能测试
pytest tests/grpc/ -v -k "performance"

# 运行并发测试
pytest tests/grpc/ -v -k "concurrent"
```

### 查看测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/grpc/ --cov=app.grpc_services --cov-report=html

# 查看覆盖率报告
# 打开 htmlcov/index.html
```

## 🔧 配置测试

编辑 `tests/grpc/config.py` 文件来修改测试配置：

```python
# gRPC 服务器地址
GRPC_SERVER_HOST = "localhost"
GRPC_SERVER_PORT = 50051

# 测试账户（用于集成测试）
TEST_ACCOUNT_ID = "your_account"
TEST_ACCOUNT_PASSWORD = "your_password"

# 是否跳过集成测试
SKIP_INTEGRATION_TESTS = True  # 改为 False 以运行真实测试
```

## 📝 测试开发指南

### 编写新测试用例

1. **在 test_data_grpc_service.py 中添加数据服务测试**

```python
def test_new_data_feature(self, data_stub):
    """测试新的数据功能"""
    request = data_pb2.NewFeatureRequest(
        parameter1="value1",
        parameter2="value2"
    )
    
    response = data_stub.NewFeature(request)
    
    assert response.status.code == 0
    # 添加更多断言...
```

2. **在 test_trading_grpc_service.py 中添加交易服务测试**

```python
def test_new_trading_feature(self, trading_stub, test_session):
    """测试新的交易功能"""
    request = trading_pb2.NewFeatureRequest(
        session_id=test_session,
        parameter1="value1"
    )
    
    response = trading_stub.NewFeature(request)
    
    assert response.status.code == 0
    # 添加更多断言...
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

@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature(self):
    """标记为跳过的测试"""
    pass
```

运行特定标记的测试：
```bash
pytest tests/grpc/ -v -m "not slow"  # 跳过慢速测试
pytest tests/grpc/ -v -m integration  # 只运行集成测试
```

## 🐛 调试测试

### 查看详细输出

```bash
# 显示 print 输出
pytest tests/grpc/ -v -s

# 显示更详细的错误信息
pytest tests/grpc/ -v --tb=long

# 在第一个失败时停止
pytest tests/grpc/ -v -x
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
pytest tests/grpc/test_data_grpc_service.py::test_debug_example -v -s
```

## 📊 测试报告

### 生成 HTML 报告

```bash
# 安装 pytest-html
pip install pytest-html

# 生成报告
pytest tests/grpc/ -v --html=report.html --self-contained-html
```

### 生成 JUnit XML 报告（CI/CD）

```bash
pytest tests/grpc/ -v --junitxml=junit.xml
```

## ⚡ 性能基准

### 预期性能指标

| 操作 | 目标延迟 | 说明 |
|------|---------|------|
| 单股行情查询 | < 50ms | 小数据量查询 |
| 批量行情查询 | < 500ms | 50只股票 |
| 财务数据查询 | < 200ms | 单只股票，多张表 |
| 提交订单 | < 100ms | 单笔订单 |
| 查询持仓 | < 50ms | 当前持仓 |
| 查询订单 | < 100ms | 当日订单 |

### 运行性能基准测试

```bash
pytest tests/grpc/ -v -k "performance" --durations=10
```

## 🔍 常见问题

### Q1: 测试失败提示 "grpc" 模块找不到

**A:** 安装 gRPC 依赖：
```bash
pip install grpcio grpcio-tools
```

### Q2: 测试失败提示找不到 protobuf 模块

**A:** 生成 protobuf 代码：
```bash
python scripts/generate_proto.py
```

### Q3: 连接超时

**A:** 确保 gRPC 服务器已启动：
```bash
python run_grpc.py
```

并检查配置文件中的服务器地址是否正确。

### Q4: 所有测试都被跳过

**A:** 检查 `config.py` 中的 `SKIP_INTEGRATION_TESTS` 设置，以及测试代码中的 `@pytest.mark.skip` 标记。

## 📚 相关文档

- [pytest 官方文档](https://docs.pytest.org/)
- [gRPC Python 教程](https://grpc.io/docs/languages/python/)
- [Protocol Buffers 指南](https://protobuf.dev/)
- [项目 gRPC 迁移计划](../../PLAN_GRPC.md)
- [项目接口实现清单](../../PLAN.md)

## 🤝 贡献指南

1. 为新功能编写测试
2. 确保所有测试通过
3. 更新测试文档
4. 提交 Pull Request

## 📄 许可证

本测试套件遵循项目主许可证。

---

**最后更新**: 2025-10-25  
**维护者**: Development Team
