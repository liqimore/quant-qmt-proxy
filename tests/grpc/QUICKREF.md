# gRPC 测试快速参考

## 🚀 快速命令

### 运行测试

```bash
# 运行所有 gRPC 测试
pytest tests/grpc/ -v

# 运行数据服务测试
pytest tests/grpc/test_data_grpc_service.py -v

# 运行交易服务测试
pytest tests/grpc/test_trading_grpc_service.py -v

# 运行特定测试类
pytest tests/grpc/test_data_grpc_service.py::TestDataGrpcService::TestImplementedApis -v

# 运行特定测试方法
pytest tests/grpc/ -k "test_get_market_data" -v

# 显示详细输出
pytest tests/grpc/ -v -s

# 显示跳过的测试
pytest tests/grpc/ -v -rs

# 只运行失败的测试
pytest tests/grpc/ --lf -v

# 停在第一个失败
pytest tests/grpc/ -x -v
```

### 按标记运行

```bash
# 运行性能测试
pytest tests/grpc/ -v -m performance

# 跳过慢速测试
pytest tests/grpc/ -v -m "not slow"

# 只运行集成测试
pytest tests/grpc/ -v -m integration

# 运行数据服务相关测试
pytest tests/grpc/ -v -m data

# 运行交易服务相关测试
pytest tests/grpc/ -v -m trading
```

### 覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/grpc/ --cov=app.grpc_services --cov-report=html

# 查看报告
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### 测试报告

```bash
# 生成 HTML 报告
pip install pytest-html
pytest tests/grpc/ -v --html=report.html --self-contained-html

# 生成 JUnit XML 报告（CI/CD）
pytest tests/grpc/ -v --junitxml=junit.xml
```

### 性能分析

```bash
# 显示最慢的 10 个测试
pytest tests/grpc/ -v --durations=10

# 显示所有测试的执行时间
pytest tests/grpc/ -v --durations=0
```

## 📋 常用参数

| 参数 | 说明 |
|------|------|
| `-v` | 详细输出 |
| `-s` | 显示 print 输出 |
| `-x` | 遇到第一个失败就停止 |
| `-k EXPRESSION` | 运行匹配表达式的测试 |
| `-m MARKEXPR` | 运行匹配标记的测试 |
| `--lf` | 只运行上次失败的测试 |
| `--ff` | 先运行失败的测试 |
| `--tb=short` | 短格式的错误信息 |
| `--tb=long` | 长格式的错误信息 |
| `--collect-only` | 只收集测试，不运行 |
| `-rs` | 显示跳过测试的原因 |

## 🔧 配置修改

### tests/grpc/config.py

```python
# gRPC 服务器地址
GRPC_SERVER_HOST = "localhost"
GRPC_SERVER_PORT = 50051

# 是否跳过集成测试
SKIP_INTEGRATION_TESTS = False  # 改为 False 运行真实测试

# 测试账户
TEST_ACCOUNT_ID = "your_account"
TEST_ACCOUNT_PASSWORD = "your_password"
```

## 🐛 调试技巧

### 1. 使用 pdb 调试

```python
def test_debug():
    import pdb; pdb.set_trace()
    # 测试代码...
```

运行：
```bash
pytest tests/grpc/test_data_grpc_service.py::test_debug -v -s
```

### 2. 查看详细日志

```python
import logging
logger = logging.getLogger(__name__)
logger.info("调试信息")
```

运行：
```bash
pytest tests/grpc/ -v -s --log-cli-level=DEBUG
```

### 3. 只运行特定测试

```bash
# 使用节点 ID
pytest tests/grpc/test_data_grpc_service.py::TestDataGrpcService::TestImplementedApis::test_get_market_data_single_stock -v

# 使用 -k 模糊匹配
pytest tests/grpc/ -k "market_data and single" -v
```

## 📊 测试状态

### 当前状态（proto 文件未生成）

- ✅ 测试框架已完成
- ✅ 测试用例已编写
- ⏳ 等待 proto 文件生成
- ⏳ 等待实现 gRPC 服务
- ⏳ 取消测试代码注释

### 运行测试前的准备

1. 生成 proto 文件
2. 运行 `python scripts/generate_proto.py`
3. 启动 gRPC 服务器
4. 取消测试代码中的注释
5. 配置测试参数

## 🎯 测试检查清单

- [ ] proto 文件已创建
- [ ] protobuf 代码已生成
- [ ] gRPC 服务器已实现
- [ ] gRPC 服务器正在运行
- [ ] 测试配置已更新
- [ ] 测试代码注释已取消
- [ ] 依赖已安装（grpcio, protobuf, pytest）

## 📞 获取帮助

```bash
# 查看 pytest 帮助
pytest --help

# 查看可用的 fixtures
pytest tests/grpc/ --fixtures

# 查看可用的标记
pytest tests/grpc/ --markers

# 查看测试收集情况
pytest tests/grpc/ --collect-only
```

---

**最后更新**: 2025-10-25
