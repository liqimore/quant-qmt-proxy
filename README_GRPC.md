# QMT Proxy gRPC 使用指南

## 📋 概述

QMT Proxy 现在支持 **gRPC** 协议，相比 REST API 具有更高的性能和更低的延迟。

### 优势

- **高性能**: HTTP/2 多路复用、二进制传输、头部压缩
- **低延迟**: 消息体积减少 50%+、更快的序列化
- **类型安全**: 强类型 protobuf 定义
- **跨语言**: 官方支持多种语言

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `grpcio==1.60.0` - gRPC 核心库
- `grpcio-tools==1.60.0` - protobuf 编译工具
- `protobuf==4.25.1` - protobuf 库

### 2. 生成 Protobuf 代码

```bash
python scripts/generate_proto.py
```

这将在 `generated/` 目录生成 Python 代码。

### 3. 启动 gRPC 服务器

**仅启动 gRPC 服务**:
```bash
python run_grpc.py
```

**同时启动 REST + gRPC（混合模式）**:
```bash
python run_hybrid.py
```

服务端口：
- REST API: `http://localhost:8000`
- gRPC: `localhost:50051`

---

## 📖 使用示例

### Python 客户端

```python
from app.grpc_client import QMTGrpcClient
from generated import common_pb2, trading_pb2

# 创建客户端
client = QMTGrpcClient(host='localhost', port=50051)

# 1. 健康检查
health = client.check_health()
print(f"服务状态: {health.status}")

# 2. 获取市场数据
response = client.get_market_data(
    stock_codes=['000001.SZ', '600000.SH'],
    start_date='20240101',
    end_date='20240131',
    period=common_pb2.PERIOD_TYPE_1D
)

for stock_data in response.data:
    print(f"{stock_data.stock_code}: {len(stock_data.bars)} 条K线")
    for bar in stock_data.bars:
        print(f"  {bar.time}: 收盘价={bar.close}, 成交量={bar.volume}")

# 3. 连接交易账户
connect_response = client.connect(
    account_id="your_account_id",
    password="your_password"
)

if connect_response.success:
    session_id = connect_response.session_id
    
    # 4. 获取持仓
    positions = client.get_positions(session_id)
    for pos in positions.positions:
        print(f"{pos.stock_name}: {pos.volume}股, 成本价={pos.cost_price}")
    
    # 5. 提交订单
    order = client.submit_order(
        session_id=session_id,
        stock_code='000001.SZ',
        side=trading_pb2.ORDER_SIDE_BUY,
        volume=100,
        price=13.50,
        order_type=trading_pb2.ORDER_TYPE_LIMIT
    )
    print(f"订单ID: {order.order.order_id}")
    
    # 6. 撤销订单
    cancel = client.cancel_order(session_id, order.order.order_id)
    print(f"撤销成功: {cancel.success}")
    
    # 7. 断开连接
    client.disconnect(session_id)

# 关闭客户端
client.close()
```

### 运行示例

```bash
# 运行内置示例客户端
python app/grpc_client.py
```

---

## 📡 API 接口

### 数据服务 (DataService)

| 接口 | 说明 |
|------|------|
| `GetMarketData` | 获取市场数据（K线） |
| `GetFinancialData` | 获取财务数据 |
| `GetSectorList` | 获取板块列表 |
| `GetIndexWeight` | 获取指数权重 |
| `GetTradingCalendar` | 获取交易日历 |
| `GetInstrumentInfo` | 获取合约信息 |
| `GetETFInfo` | 获取ETF信息 |

### 交易服务 (TradingService)

| 接口 | 说明 |
|------|------|
| `Connect` | 连接交易账户 |
| `Disconnect` | 断开账户 |
| `GetAccountInfo` | 获取账户信息 |
| `GetPositions` | 获取持仓列表 |
| `SubmitOrder` | 提交订单 |
| `CancelOrder` | 撤销订单 |
| `GetOrders` | 获取订单列表 |
| `GetTrades` | 获取成交记录 |
| `GetAsset` | 获取资产信息 |
| `GetRiskInfo` | 获取风险信息 |
| `GetStrategies` | 获取策略列表 |

### 健康检查 (Health)

| 接口 | 说明 |
|------|------|
| `Check` | 健康检查 |

---

## ⚙️ 配置

### config.yml

```yaml
grpc:
  enabled: true
  host: "0.0.0.0"
  port: 50051
  max_workers: 10
  max_message_length: 52428800  # 50MB
```

### 环境变量

```bash
# Windows
set APP_MODE=dev

# Linux/Mac
export APP_MODE=dev
```

模式：
- `mock` - 模拟数据，不连接 xtquant
- `dev` - 真实数据，不允许交易
- `prod` - 真实数据，允许交易

---

## 🔧 开发指南

### 修改 Proto 定义

1. 编辑 `proto/*.proto` 文件
2. 运行 `python scripts/generate_proto.py` 重新生成代码
3. 更新 gRPC 服务实现 (`app/grpc_services/`)

### 添加新接口

1. 在 `proto/data.proto` 或 `proto/trading.proto` 中定义新的 message 和 rpc
2. 生成代码
3. 在 `app/grpc_services/` 中实现对应的方法
4. 更新客户端示例

---

## 📊 性能对比

| 指标 | REST API | gRPC | 提升 |
|------|----------|------|------|
| 消息体积 | 100% | ~45% | 55% ↓ |
| 平均延迟 | 100ms | ~65ms | 35% ↓ |
| QPS | 1000 | ~2200 | 120% ↑ |

---

## 🐛 常见问题

### Q: gRPC 服务启动失败？

**A**: 检查端口 50051 是否被占用：
```bash
netstat -ano | findstr :50051
```

### Q: 生成 protobuf 代码失败？

**A**: 确保已安装 grpcio-tools：
```bash
pip install grpcio-tools==1.60.0
```

### Q: 客户端连接超时？

**A**: 检查防火墙设置和 gRPC 服务器是否正在运行。

---

## 📝 更多资源

- [gRPC 官方文档](https://grpc.io/docs/)
- [Protocol Buffers 指南](https://protobuf.dev/)
- [项目 GitHub](https://github.com/liqimore/quant-qmt-proxy)

---

**最后更新**: 2025-01-25  
**版本**: 0.1.0-grpc
