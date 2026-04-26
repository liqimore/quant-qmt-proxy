# xtquant-proxy

> **开发状态**: `v0.0.1` 迭代中 | 当前已支持 gRPC / REST / WebSocket、多环境 `mock / dev / prod` 和本地 `xtquant` 代理能力；后续将继续补充更多 xtquant 能力、真实联调体验和客户端示例

<div align="center">

基于 FastAPI、gRPC 和 WebSocket 的 xtquant / QMT 代理服务

[![Python](https://img.shields.io/badge/Python-3.10--3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![gRPC](https://img.shields.io/badge/gRPC-1.76+-orange.svg)](https://grpc.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#快速开始) | [核心特性](#核心特性) | [环境配置](#环境配置) | [运行模式](#运行模式) | [测试](#测试)

</div>

## 核心特性

- 统一代理 `xtquant / QMT`，同时提供 gRPC、REST 和 WebSocket 三种接入方式
- 提供 `mock / dev / prod` 三环境切换，便于本地开发、模拟账号联调和真实环境接入
- 支持账户会话、资产、持仓、订单、成交、下单、撤单等交易能力
- 支持历史 K 线、历史 tick、full tick、财务数据、合约详情、指数权重、板块列表和 L2 数据查询
- 支持普通行情订阅与 whole quote 订阅，可通过 WebSocket 或 gRPC 流式消费
- 提供完整的本地自动化测试基座，便于在真实 QMT 接入前完成大部分验证

## 近期测试
已通过 miniQMT模拟客户端 全量用例，真实环境全量功能待验证
<img width="1279" height="546" alt="Snipaste_2026-04-26_19-50-27" src="https://github.com/user-attachments/assets/88f2419a-de11-48b4-9556-c3e0899a9622" />
<img width="1265" height="376" alt="Snipaste_2026-04-26_19-53-35" src="https://github.com/user-attachments/assets/7b517615-2db3-4697-849c-89a753e184f6" />

## 快速开始

### 1. 环境要求

- Windows
- Python `3.10 - 3.13`
- `mock` 模式不需要 QMT
- `dev / prod` 模式需要本机已登录可用的 MiniQMT / QMT

### 2. 安装依赖

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

如果 `python` 命令不可用，可以改用：

```cmd
py -3.13 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

### 3. 启动本地 mock

```cmd
set APP_MODE=mock
set APP_SERVERS=all
python run.py
```

也可以使用启动脚本：

```cmd
python start.py --mode mock --servers all
```

### 4. 访问接口

- REST API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- gRPC: `localhost:50051`

### 5. 运行本地 mock 测试

```cmd
python -m pytest tests\unit -q --xt-mode=mock
```

## 环境配置

配置文件按用途分为三类：

- `config.yml`：仓库默认配置
- `config.local.yml`：本机运行时覆盖配置
- `config.test.local.yml`：本机真实环境测试覆盖配置

通常建议：

- `mock`：直接通过环境变量启动
- `dev / prod` 运行：使用 `config.local.yml`
- `dev / prod` pytest：使用 `config.test.local.yml`
- 仓库默认 `config.yml` 不预置本机 QMT 路径，请在本地覆盖配置中填写

### mock 配置

本地 mock 不需要额外配置文件：

```cmd
set APP_MODE=mock
set APP_SERVERS=all
python run.py
```

只启动 REST / WebSocket：

```cmd
set APP_MODE=mock
set APP_SERVERS=rest
python run.py
```

只启动 gRPC：

```cmd
set APP_MODE=mock
set APP_SERVERS=grpc
python run.py
```

### dev / prod 运行配置

先复制运行时本地配置：

```cmd
copy config.local.example.yml config.local.yml
```

示例：

```yaml
xtquant:
  qmt_userdata_path: "C:\\path\\to\\your\\QMT\\userdata"
  trading:
    enable_prod_orders: false
    accounts:
      - name: "sim-dev"
        account_id: "你的模拟账号"
        account_type: "STOCK"
        account_kind: "simulated"
        allowed_modes: ["dev"]
        enabled: true

      - name: "prod-main"
        account_id: "你的真实账号"
        account_type: "STOCK"
        account_kind: "real"
        allowed_modes: ["prod"]
        enabled: true
```

说明：

- `qmt_userdata_path` 要填 QMT 的用户数据目录，不是安装根目录
- MiniQMT 通常使用 `userdata_mini`
- 券商 QMT / 投研端通常使用 `userdata`
- `dev` 只能使用 `simulated` 账号
- `prod` 只能使用 `real` 账号
- 未登记账号会在建会话时被拒绝
- 如果要让外部模块在 `prod` 下真实下单，需要显式开启 `xtquant.trading.enable_prod_orders: true`

启动示例：

```cmd
set APP_MODE=dev
set APP_SERVERS=all
python run.py
```

```cmd
set APP_MODE=prod
set APP_SERVERS=all
python run.py
```

### dev / prod 测试配置

如果要跑真实 xtquant 测试，再复制测试专用配置：

```cmd
copy config.test.local.example.yml config.test.local.yml
```

这个文件主要用于：

- `testing.default_account_profile`
- `testing.enable_prod_readonly_tests`
- `testing.prod_unlock_token`
- `testing.qmt_userdata_path`
- `xtquant.trading.accounts`

## 运行模式

| 模式 | xtquant | 账号要求 | 自动化下单 |
| --- | --- | --- | --- |
| `mock` | 不连接 | 无 | 本地假实现 |
| `dev` | 真实 xtquant | 显式登记的 `simulated` 账号 | 允许 |
| `prod` | 真实 xtquant | 显式登记的 `real` 账号 | 测试用例中只读 |

说明：

- `mock` 适合本地开发和默认测试
- `dev` 适合模拟账号联调，走真实 xtquant 接口
- `prod` 自动化测试默认只读，用于验证真实账号查询、订阅和拒单行为
- `prod` 自动化只读只约束测试用例；真实部署后，外部模块是否能下单仍由 `xtquant.trading.enable_prod_orders` 控制

同时支持三种服务装配方式：

- `APP_SERVERS=all`：同时启动 REST 和 gRPC
- `APP_SERVERS=rest`：只启动 REST / WebSocket
- `APP_SERVERS=grpc`：只启动 gRPC

## 接口概览

### REST

数据接口：

- `POST /api/v1/data/kline-history`
- `POST /api/v1/data/tick-history`
- `POST /api/v1/data/full-tick`
- `POST /api/v1/data/financial`
- `GET /api/v1/data/instrument/{symbol}`
- `POST /api/v1/data/trading-calendar`
- `POST /api/v1/data/index-weight`
- `GET /api/v1/data/sectors`
- `POST /api/v1/data/l2/quote`
- `POST /api/v1/data/l2/order`
- `POST /api/v1/data/l2/transaction`
- `POST /api/v1/data/subscriptions/quote`
- `POST /api/v1/data/subscriptions/whole-quote`
- `GET /api/v1/data/subscriptions`
- `GET /api/v1/data/subscriptions/{subscription_id}`
- `DELETE /api/v1/data/subscriptions/{subscription_id}`

交易接口：

- `POST /api/v1/trading/sessions`
- `GET /api/v1/trading/sessions/{session_id}`
- `DELETE /api/v1/trading/sessions/{session_id}`
- `GET /api/v1/trading/sessions/{session_id}/asset`
- `GET /api/v1/trading/sessions/{session_id}/positions`
- `GET /api/v1/trading/sessions/{session_id}/orders`
- `GET /api/v1/trading/sessions/{session_id}/trades`
- `POST /api/v1/trading/sessions/{session_id}/orders`
- `POST /api/v1/trading/sessions/{session_id}/cancel`

健康接口：

- `GET /`
- `GET /health/`
- `GET /health/ready`
- `GET /health/live`

### gRPC

数据服务：

- `GetKlineHistory`
- `GetTickHistory`
- `GetFullTickSnapshot`
- `GetFinancialData`
- `GetInstrumentDetail`
- `GetTradingCalendar`
- `GetIndexWeight`
- `GetSectorList`
- `GetL2Quote`
- `GetL2Order`
- `GetL2Transaction`
- `StreamQuote`
- `StreamWholeQuote`

交易服务：

- `OpenSession`
- `CloseSession`
- `GetSession`
- `GetStockAsset`
- `GetStockPositions`
- `GetStockOrders`
- `GetStockTrades`
- `SubmitStockOrder`
- `CancelStockOrder`
- `StreamTradingEvents`

### WebSocket

- `GET /ws/quote/{subscription_id}`

## 测试

默认测试只跑本地 `mock`：

```cmd
python -m pytest tests\unit -q --xt-mode=mock
```

按模块运行：

```cmd
python -m pytest tests\unit\test_rest_api_interfaces.py -q --xt-mode=mock
python -m pytest tests\unit\test_rest_websocket.py -q --xt-mode=mock
python -m pytest tests\unit\test_grpc_api_interfaces.py -q --xt-mode=mock
python -m pytest tests\unit\test_health_and_auth.py -q --xt-mode=mock
python -m pytest tests\unit\test_trading_service.py -q --xt-mode=mock
```

### dev 测试

```cmd
python -m pytest tests\unit -q --xt-mode=dev --xt-account-profile=sim-dev --xt-enable-live-streams
```

### prod 测试

```cmd
set QMT_TEST_PROD_UNLOCK_TOKEN=your-token
python -m pytest tests\unit -q --xt-mode=prod --xt-account-profile=prod-main --xt-enable-prod-tests
```

说明：

- `prod` pytest 只验证查询、订阅、鉴权和拒单
- `prod` pytest 不会真实下单 / 撤单
- 真实 `prod` 放单请通过你自己的外部模块或手工联调验证

## 项目结构

```text
quant-qmt-proxy/
├── app/                # 应用代码
├── proto/              # protobuf 定义
├── generated/          # protobuf 生成代码
├── tests/              # 测试
├── xtquant/            # 本地 xtquant SDK
├── scripts/            # 辅助脚本
├── config.yml          # 默认配置
├── config.local.example.yml
├── config.test.local.example.yml
├── run.py              # 启动入口
└── start.py            # 启动脚本
```

## 文档约定

涉及 xtquant / QMT 的接口签名、生命周期、返回结构和调用方式时，以两类来源为准：

- 官方文档：[start_now](https://dict.thinktrader.net/nativeApi/start_now.html)、[xttrader](https://dict.thinktrader.net/nativeApi/xttrader.html)、[xtdata](https://dict.thinktrader.net/nativeApi/xtdata.html)
- 仓库内本地 `xtquant` 源码

## 贡献

欢迎提交 Issue 和 Pull Request。

如果修改了 `proto/*.proto`，请同步执行：

```cmd
python scripts\generate_proto.py --mode generate
```

## 许可证

MIT License，详见 [LICENSE](LICENSE)。
