# xtquant-proxy

> 🚧 **开发状态**: v0.0.1 开发中 | 当前版本仅供学习和测试使用，请勿用于生产环境

<div align="center">

**基于 FastAPI + gRPC 的 xtquant 量化交易代理服务**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![gRPC](https://img.shields.io/badge/gRPC-1.60+-orange.svg)](https://grpc.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

提供 **RESTful API** 和 **gRPC** 双协议接口，封装国金 QMT xtquant SDK 的数据和交易功能

[快速开始](#-快速开始) • [API 文档](#-api接口说明) • [技术架构](#-技术架构) • [测试覆盖](#-测试覆盖)

</div>

---

## ✨ 核心特性

### 🎯 双协议支持
- 🌐 **REST API**: 基于 FastAPI，提供 HTTP/HTTPS 接口，自动生成 Swagger 文档
- ⚡ **gRPC**: 高性能 RPC 框架，支持流式调用和双向通信
- 🔄 **统一服务**: 两种协议共享相同的业务逻辑层，一次部署同时服务

### 🛡️ 安全可靠
- 🔐 **API Key 认证**: 多环境 API Key 管理
- 🚦 **交易拦截**: dev 模式自动拦截真实交易，保护账户安全
- 📝 **完整日志**: 基于 Loguru 的结构化日志，支持日志轮转和压缩
- 🔒 **异常保护**: 全局异常处理，xtdata 连接超时保护

### 📊 功能完整
- 📈 **市场数据**: K线、分时、tick、财务数据、板块数据
- 💼 **交易功能**: 下单、撤单、持仓查询、订单管理
- ❤️ **健康检查**: REST 和 gRPC 双协议健康检查
- 🎯 **三种模式**: mock/dev/prod 灵活切换

### ⚙️ 配置灵活
- 📋 **统一配置**: config.yml 集中管理所有配置
- 🔄 **环境切换**: 通过 APP_MODE 环境变量一键切换模式
- 🎨 **单例模式**: 配置和服务单例加载，避免重复初始化

---

## 📁 项目结构

```
quant-qmt-proxy/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── grpc_server.py          # gRPC 服务器入口
│   ├── grpc_client.py          # gRPC 客户端封装
│   ├── config.py               # 配置管理（单例）
│   ├── dependencies.py         # 依赖注入（单例服务）
│   ├── models/                 # Pydantic 数据模型
│   │   ├── data_models.py      # 数据相关模型
│   │   └── trading_models.py   # 交易相关模型
│   ├── routers/                # REST API 路由
│   │   ├── data.py             # 数据服务 API
│   │   ├── trading.py          # 交易服务 API
│   │   └── health.py           # 健康检查 API
│   ├── grpc_services/          # gRPC 服务实现
│   │   ├── data_grpc_service.py      # 数据服务 gRPC
│   │   ├── trading_grpc_service.py   # 交易服务 gRPC
│   │   └── health_grpc_service.py    # 健康检查 gRPC
│   ├── services/               # 业务服务层（REST 和 gRPC 共享）
│   │   ├── data_service.py     # 数据服务（xtdata 封装）
│   │   └── trading_service.py  # 交易服务（xttrader 封装）
│   └── utils/                  # 工具函数
│       ├── exceptions.py       # 自定义异常
│       ├── helpers.py          # 辅助函数
│       └── logger.py           # 日志配置
├── proto/                      # Protocol Buffers 定义
│   ├── common.proto            # 公共消息定义
│   ├── data.proto              # 数据服务定义
│   ├── trading.proto           # 交易服务定义
│   └── health.proto            # 健康检查定义
├── generated/                  # protobuf 生成的 Python 代码
│   ├── data_pb2.py             # 数据服务消息
│   ├── data_pb2_grpc.py        # 数据服务 stub
│   ├── trading_pb2.py          # 交易服务消息
│   ├── trading_pb2_grpc.py     # 交易服务 stub
│   └── ...
├── tests/                      # 测试套件
│   ├── rest/                   # REST API 测试
│   │   ├── test_data_api.py
│   │   ├── test_trading_api.py
│   │   └── test_health_api.py
│   └── grpc/                   # gRPC 测试
│       ├── test_data_grpc_service.py
│       ├── test_trading_grpc_service.py
│       └── test_health_grpc_service.py
├── xtquant/                    # xtquant SDK（国金 QMT）
├── scripts/                    # 工具脚本
│   └── generate_proto.py       # protobuf 代码生成脚本
├── docs/                       # 项目文档（本地保存，git 忽略）
├── logs/                       # 日志文件目录
├── config.yml                  # 统一配置文件
├── requirements.txt            # Python 依赖
├── run.py                      # 启动脚本（同时启动 REST + gRPC）
└── README.md                   # 项目说明
```

---

## 近期用例测试结果
<img width="1106" height="619" alt="image" src="https://github.com/user-attachments/assets/c0f56377-e74e-4d70-88bc-bd194b2cf430" />

## 🚀 快速开始

### 1. 前置要求

- **Python 3.10+**
- **国金 QMT 客户端**（dev/prod 模式需要）
- **Windows 系统**（QMT 仅支持 Windows）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 QMT 路径

编辑 `config.yml`，修改 QMT 安装路径：

```yaml
xtquant:
  qmt_userdata_path: "C:/quant/国金QMT交易端模拟/userdata_mini"
```

### 4. 启动服务

服务默认同时启动 **REST API** (端口 8000) 和 **gRPC** (端口 50051)。

```powershell
# mock 模式 - 不连接 QMT，使用模拟数据（无需 QMT）
$env:APP_MODE="mock"; python run.py

# dev 模式 - 连接 QMT，获取真实数据，禁止交易（默认，推荐开发使用）
$env:APP_MODE="dev"; python run.py

# prod 模式 - 连接 QMT，获取真实数据，允许交易（生产环境）
$env:APP_MODE="prod"; python run.py
```

### 5. 访问服务

启动后可访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **REST API** | http://localhost:8000 | RESTful API 主入口 |
| **gRPC** | localhost:50051 | gRPC 服务端口 |
| **Swagger UI** | http://localhost:8000/docs | 交互式 API 文档 |
| **ReDoc** | http://localhost:8000/redoc | API 文档（阅读友好） |
| **健康检查** | http://localhost:8000/health/ | 服务健康状态 |

### 6. 运行测试

```bash
# REST API 测试
pytest tests/rest/ -v

# gRPC 测试
pytest tests/grpc/ -v

# 所有测试
pytest tests/ -v
```

---

## 🎯 运行模式说明

项目支持三种运行模式，通过环境变量 `APP_MODE` 切换：

| 模式 | 连接 xtquant | 真实交易 | 使用场景 |
|------|------------|---------|---------|
| **mock** | ❌ 否 | ❌ 禁止 | 开发测试，无需 QMT 客户端 |
| **dev** | ✅ 是 | ❌ 禁止 | 开发调试，获取真实数据但不下单 |
| **prod** | ✅ 是 | ✅ 允许 | 生产环境，真实交易 |

### 模式特性

#### 🎭 mock 模式
- ✅ 不需要运行 QMT 客户端
- ✅ 使用模拟数据响应 API 请求
- ✅ 适合前端开发、接口测试
- 📝 订单 ID 前缀: `mock_order_*`

#### 🔧 dev 模式（推荐开发使用）
- ✅ 需要运行 QMT 客户端
- ✅ 获取真实的市场数据、财务数据
- ✅ **交易请求被拦截**，返回模拟订单
- ✅ 适合策略开发、回测验证
- 📝 订单 ID 前缀: `mock_order_*`
- 🔒 日志记录所有拦截操作

#### 🚀 prod 模式（谨慎使用）
- ✅ 需要运行 QMT 客户端
- ✅ 获取真实数据
- ⚠️ **允许真实交易下单**
- ⚠️ 适合生产环境、实盘交易
- 📝 订单 ID: xttrader 返回的真实订单号

---

## 📡 API 接口说明

### REST API 接口

#### 数据服务 (`/api/v1/data/`)
- `POST /api/v1/data/market` - 获取市场行情数据
- `POST /api/v1/data/financial` - 获取财务数据
- `GET /api/v1/data/sectors` - 获取板块列表
- `POST /api/v1/data/sector` - 获取板块成分股
- `POST /api/v1/data/index-weight` - 获取指数权重
- `GET /api/v1/data/trading-calendar/{year}` - 获取交易日历
- `GET /api/v1/data/instrument/{stock_code}` - 获取合约信息

#### 交易服务 (`/api/v1/trading/`)
- `POST /api/v1/trading/connect` - 连接交易账户
- `POST /api/v1/trading/disconnect/{session_id}` - 断开账户
- `GET /api/v1/trading/account/{session_id}` - 获取账户信息
- `GET /api/v1/trading/positions/{session_id}` - 获取持仓信息
- `POST /api/v1/trading/order/{session_id}` - 提交订单
- `POST /api/v1/trading/cancel/{session_id}` - 撤销订单
- `GET /api/v1/trading/orders/{session_id}` - 获取订单列表
- `GET /api/v1/trading/trades/{session_id}` - 获取成交记录

#### 系统服务 (`/health/`)
- `GET /health/` - 健康检查
- `GET /health/ready` - 就绪检查
- `GET /health/live` - 存活检查

### gRPC 接口

#### 数据服务 (DataService)
- `GetMarketData()` - 获取市场数据
- `GetFinancialData()` - 获取财务数据
- `GetSectorList()` - 获取板块列表
- `GetStockListInSector()` - 获取板块成分股
- `GetIndexWeight()` - 获取指数权重
- `GetTradingCalendar()` - 获取交易日历
- `GetInstrumentDetail()` - 获取合约信息

#### 交易服务 (TradingService)
- `Connect()` - 连接交易账户
- `Disconnect()` - 断开连接
- `GetAccountInfo()` - 获取账户信息
- `GetPositions()` - 获取持仓
- `SubmitOrder()` - 提交订单
- `CancelOrder()` - 撤销订单
- `GetOrders()` - 查询订单
- `GetTrades()` - 查询成交

#### 健康检查服务 (HealthService)
- `Check()` - 健康检查
- `Watch()` - 健康状态订阅（流式）

---

## 🔧 技术架构

### 核心技术栈
- **FastAPI**: 现代高性能 Web 框架
- **gRPC**: 高性能 RPC 框架
- **Protocol Buffers**: 数据序列化协议
- **Pydantic**: 数据验证和序列化
- **uvicorn**: ASGI 服务器
- **Loguru**: 结构化日志库
- **xtquant**: 国金 QMT Python SDK

### 设计模式
- ✅ **依赖注入**: 使用 FastAPI 的 Depends 系统
- ✅ **单例模式**: 服务实例全局唯一，避免重复初始化
- ✅ **策略模式**: 不同模式下的不同行为
- ✅ **拦截器模式**: 交易请求拦截保护
- ✅ **适配器模式**: REST 和 gRPC 共享业务逻辑

### 架构优势
- 🎯 **分层架构**: Router → Service → SDK，职责清晰
- 🔄 **代码复用**: REST 和 gRPC 共享同一套业务服务
- ⚡ **高性能**: gRPC 二进制传输，FastAPI 异步处理
- 🛡️ **可靠性**: 完整的异常处理和日志记录
- 📈 **可扩展**: 易于添加新接口和功能

---

## 🧪 测试覆盖

### REST API 测试 (tests/rest/)
- ✅ 健康检查测试
- ✅ 数据服务测试（市场数据、财务数据、板块数据）
- ✅ 交易服务测试（下单、撤单、持仓查询）

### gRPC 测试 (tests/grpc/)
- ✅ 健康检查服务测试（Check、Watch）
- ✅ 数据服务测试（9 个接口）
- ✅ 交易服务测试（8 个接口）

### 测试特性
- 🎯 使用 pytest 框架
- 🔄 支持 mock/dev/prod 三种模式测试
- 📊 详细的测试报告和日志
- 🚀 CI/CD 集成就绪

---

## 📊 功能实现进度

### 已实现功能 ✅

#### 数据模块 (9/50+)
- ✅ 市场数据获取（K线、分时、tick）
- ✅ 财务数据查询
- ✅ 板块数据管理
- ✅ 指数权重查询
- ✅ 交易日历查询
- ✅ 合约信息查询
- ✅ ETF 信息查询（占位）

#### 交易模块 (6/60+)
- ✅ 账户连接管理
- ✅ 下单/撤单
- ✅ 持仓查询
- ✅ 订单查询
- ✅ 交易模式拦截

#### 系统模块
- ✅ 配置管理（单例模式）
- ✅ 日志系统（Loguru）
- ✅ 健康检查（REST + gRPC）
- ✅ API 认证
- ✅ 异常处理

### 待实现功能 🚧

#### 高优先级 (P0)
- ❌ 资产查询接口（真实数据）
- ❌ 成交查询接口（真实数据）
- ❌ 异步下单/撤单
- ❌ 交易回调推送（WebSocket）

#### 中优先级 (P1)
- ❌ Level2 行情数据
- ❌ 实时行情订阅（WebSocket）
- ❌ 数据下载管理
- ❌ 新股申购功能

#### 低优先级 (P2)
- ❌ 信用交易（融资融券）
- ❌ 资金管理（银证转账）
- ❌ 约券功能
- ❌ 板块管理

**接口覆盖率**: 15/125+ ≈ 12%

---

## 📝 配置说明

### config.yml 结构

```yaml
app:
  name: "xtquant-proxy"
  version: "1.0.0"

# gRPC 配置
grpc:
  enabled: true
  host: "0.0.0.0"
  port: 50051
  max_workers: 10

# 日志配置
logging:
  file: "logs/app.log"
  error_file: "logs/error.log"
  rotation: "10 MB"
  retention: "30 days"
  compression: "zip"

# xtquant 配置
xtquant:
  qmt_userdata_path: "C:/quant/国金QMT交易端模拟/userdata_mini"

# 运行模式配置
modes:
  mock:
    connect_xtquant: false
    allow_real_trading: false
    
  dev:
    connect_xtquant: true
    allow_real_trading: false  # 🔒 拦截交易
    
  prod:
    connect_xtquant: true
    allow_real_trading: true   # ⚠️ 允许真实交易
```

---

## 💡 开发建议

### 本地开发流程
1. 使用 **mock 模式** 进行前端开发和接口测试
2. 使用 **dev 模式** 连接真实 QMT 进行策略开发
3. 充分测试后切换到 **prod 模式** 进行实盘交易

### API 认证
默认使用 API Key 认证，请求头格式：
```
X-API-Key: your-api-key
```

dev 模式可用的 API Key（在 config.yml 中配置）：
- `dev-api-key-001`
- `dev-api-key-002`

### 日志查看

```powershell
# 查看应用日志
Get-Content logs/app.log -Wait -Tail 50

# 查看错误日志
Get-Content logs/error.log -Wait -Tail 50
```

### 扩展开发
1. 在 `app/services/` 中添加新的业务服务
2. 在 `app/models/` 中定义 Pydantic 数据模型
3. 在 `app/routers/` 中添加 REST API 路由
4. 在 `proto/` 中定义 gRPC 服务和消息
5. 运行 `python scripts/generate_proto.py` 生成代码
6. 在 `app/grpc_services/` 中实现 gRPC 服务
7. 在 `tests/` 中添加测试用例

---

## ⚠️ 注意事项

### 安全警告
- ⚠️ **生产环境必须修改默认 API Key**
- ⚠️ **prod 模式会真实下单，请谨慎使用**
- ⚠️ **建议使用 HTTPS 和更严格的 CORS 配置**
- ⚠️ **不要将包含真实账号密码的配置文件提交到 Git**

### 已知限制
- **xtquant 仅支持 Windows 系统**
- 需要 QMT 客户端正在运行（dev/prod 模式）
- xtdata 连接有 5 秒超时限制
- 连接失败会自动降级到模拟模式
- gRPC 最大消息大小限制为 50MB

### 性能建议
- ✅ 使用单例模式避免重复初始化
- ✅ xtdata 连接成功后会复用
- ✅ gRPC 使用连接池提升性能
- 📋 考虑添加 Redis 缓存（可选）
- 📋 考虑添加数据库持久化（可选）

---

## 🐛 故障排查

### 服务启动失败
1. 检查 Python 版本 >= 3.10
2. 确认所有依赖已安装: `pip install -r requirements.txt`
3. 检查端口 8000 和 50051 是否被占用
4. 查看启动日志: `logs/app.log`

### xtdata 连接失败
1. 确认 QMT 客户端正在运行
2. 检查 `config.yml` 中的 QMT 路径是否正确
3. 查看错误日志: `logs/error.log`
4. 尝试重启 QMT 客户端

### API 返回 401 错误
1. 检查请求头是否包含 `X-API-Key: xxx`
2. 确认 API Key 在 config.yml 的当前模式配置中
3. 检查 API Key 是否正确

### gRPC 连接失败
1. 确认 gRPC 服务已启动（查看启动日志）
2. 检查端口 50051 是否被占用
3. 确认客户端使用正确的地址: `localhost:50051`
4. 检查防火墙设置

### 交易被拦截
- 这是正常行为！dev 模式会拦截所有交易请求
- 如需真实交易，切换到 prod 模式
- 检查订单 ID 前缀区分模拟/真实订单

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/liqimore/quant-qmt-proxy.git
cd quant-qmt-proxy

# 安装依赖
pip install -r requirements.txt

# 生成 protobuf 代码
python scripts/generate_proto.py

# 运行测试
pytest tests/ -v
```

### 提交规范
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🔗 相关链接

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [gRPC Python 文档](https://grpc.io/docs/languages/python/)
- [Protocol Buffers 文档](https://developers.google.com/protocol-buffers)
- [项目仓库](https://github.com/liqimore/quant-qmt-proxy)
- [QMT 官方文档](https://dict.thinktrader.net/nativeApi/start_now.html)

---

<div align="center">

**如果觉得项目有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by [liqimore](https://github.com/liqimore)

</div>
