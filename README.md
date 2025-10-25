# xtquant-proxy

> 持续开发中，请勿生产使用，可能存在跑不起来，数据错误等异常情况
> 
> dev-0.0.1 分支开发中，在0.0.1版本发布前，会定期同步开发进度至主线分支，发布后每个版本同步一次主线分支

<div align="center">

**基于 FastAPI 框架的 xtquant 量化交易代理服务**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

提供 RESTful API 接口，封装国金QMT xtquant SDK 的数据和交易功能

</div>

---

## ✨ 特性

- 🚀 **高性能**: 基于 FastAPI + uvicorn，支持异步操作
- 🔒 **安全可靠**: API Key 认证，交易拦截保护机制
- 📊 **功能完整**: 支持市场数据、财务数据、交易下单等完整功能
- 🎯 **三种模式**: mock/dev/prod 模式灵活切换
- 📝 **文档完善**: 自动生成 Swagger/ReDoc API 文档
- 🧪 **易于测试**: 包含完整的测试脚本
- ⚙️ **配置灵活**: 统一配置文件，环境变量切换

## 📁 项目结构

```
quant-qmt-proxy/
├── app/
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py              # 配置管理（单例模式）
│   ├── dependencies.py        # 依赖注入（单例服务）
│   ├── models/                # Pydantic数据模型
│   │   ├── data_models.py     # 数据相关模型
│   │   └── trading_models.py  # 交易相关模型
│   ├── routers/               # API路由
│   │   ├── data.py           # 数据服务API
│   │   ├── trading.py        # 交易服务API
│   │   └── health.py         # 健康检查API
│   ├── services/             # 业务服务层
│   │   ├── data_service.py   # 数据服务（xtdata封装）
│   │   └── trading_service.py # 交易服务（xttrader封装）
│   └── utils/                # 工具函数
│       ├── exceptions.py     # 自定义异常
│       └── helpers.py        # 辅助函数
├── xtquant/                  # xtquant SDK（国金QMT）
├── config.yml                # 统一配置文件
├── requirements.txt          # Python依赖
├── run.py                    # 启动脚本
├── test_fastapi_app.py       # 完整API测试
├── START.md                  # 启动说明
└── README.md                 # 项目文档
```

## 近期用例测试结果
<img width="1106" height="619" alt="image" src="https://github.com/user-attachments/assets/c0f56377-e74e-4d70-88bc-bd194b2cf430" />

## 主要功能模块

### 1. 数据服务 (Data Service)
- 📊 市场数据获取 (K线、分时、tick数据)
- 📈 历史数据查询
- 💰 财务数据下载
- 🏢 板块数据管理
- ⚖️ 指数权重查询
- 📅 交易日历查询
- 📋 合约信息查询

### 2. 交易服务 (Trading Service)  
- 🔐 账户连接管理
- 📊 账户信息查询
- 💼 持仓信息查询
- 📝 订单管理 (下单、撤单、查询)
- 💱 成交记录查询
- 💰 资产信息查询
- ⚠️ 风险信息查询
- 🤖 策略管理

### 3. 系统服务
- ❤️ 健康检查
- ⚙️ 配置管理
- 📝 日志记录
- 🚨 异常处理
- 🔒 API认证

## 🚀 快速开始

### 1. 前置要求

- Python 3.10+
- 国金QMT客户端（dev/prod模式需要）
- Windows系统（QMT仅支持Windows）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置QMT路径

编辑 `config.yml`，修改QMT安装路径：

```yaml
xtquant:
  qmt_userdata_path: "C:/quant/国金QMT交易端模拟/userdata_mini"
```

### 4. 启动服务

服务默认同时启动 **REST API** (端口 8000) 和 **gRPC** (端口 50051)。

#### Windows PowerShell

```powershell
# mock模式 - 不连接QMT，使用模拟数据（无需QMT）
$env:APP_MODE="mock"; python run.py

# dev模式 - 连接QMT，获取真实数据，禁止交易（默认，推荐开发使用）
$env:APP_MODE="dev"; python run.py

# prod模式 - 连接QMT，获取真实数据，允许交易（生产环境）
$env:APP_MODE="prod"; python run.py
```

#### Linux/Mac Bash

```bash
# mock模式
APP_MODE=mock python run.py

# dev模式（默认）
APP_MODE=dev python run.py

# prod模式
APP_MODE=prod python run.py
```

启动后可访问：
- **REST API**: http://localhost:8000
- **gRPC**: localhost:50051
- **API文档**: http://localhost:8000/docs

### 5. 访问服务

- 📄 **Swagger UI**: http://localhost:8000/docs
- 📚 **ReDoc**: http://localhost:8000/redoc
- ❤️ **健康检查**: http://localhost:8000/health/
- 🔌 **gRPC**: localhost:50051 (需要 gRPC 客户端)

### 6. 运行测试

```bash
python test_fastapi_app.py
```

## API接口说明

### 数据服务接口
- `POST /api/v1/data/market` - 获取市场数据
- `POST /api/v1/data/financial` - 获取财务数据
- `GET /api/v1/data/sectors` - 获取板块列表
- `POST /api/v1/data/sector` - 获取板块股票
- `POST /api/v1/data/index-weight` - 获取指数权重
- `GET /api/v1/data/trading-calendar/{year}` - 获取交易日历
- `GET /api/v1/data/instrument/{stock_code}` - 获取合约信息

### 交易服务接口
- `POST /api/v1/trading/connect` - 连接交易账户
- `POST /api/v1/trading/disconnect/{session_id}` - 断开账户
- `GET /api/v1/trading/account/{session_id}` - 获取账户信息
- `GET /api/v1/trading/positions/{session_id}` - 获取持仓信息
- `POST /api/v1/trading/order/{session_id}` - 提交订单
- `POST /api/v1/trading/cancel/{session_id}` - 撤销订单
- `GET /api/v1/trading/orders/{session_id}` - 获取订单列表
- `GET /api/v1/trading/trades/{session_id}` - 获取成交记录
- `GET /api/v1/trading/asset/{session_id}` - 获取资产信息
- `GET /api/v1/trading/risk/{session_id}` - 获取风险信息
- `GET /api/v1/trading/strategies/{session_id}` - 获取策略列表

### 系统接口
- `GET /health/` - 健康检查
- `GET /health/ready` - 就绪检查
- `GET /health/live` - 存活检查
- `GET /` - 根路径
- `GET /info` - 应用信息

## ⚙️ 运行模式说明

项目支持三种运行模式，通过环境变量 `APP_MODE` 切换：

| 模式 | 连接xtquant | 真实交易 | 使用场景 |
|------|------------|---------|---------|
| **mock** | ❌ 否 | ❌ 禁止 | 开发测试，无需QMT客户端 |
| **dev** | ✅ 是 | ❌ 禁止 | 开发调试，获取真实数据但不下单 |
| **prod** | ✅ 是 | ✅ 允许 | 生产环境，真实交易 |

### 模式特性

#### mock模式
- 不需要运行QMT客户端
- 使用模拟数据响应API请求
- 适合前端开发、接口测试
- 订单ID前缀: `mock_order_*`

#### dev模式（推荐开发使用）
- 需要运行QMT客户端
- 获取真实的市场数据、财务数据
- **交易请求被拦截**，返回模拟订单
- 适合策略开发、回测验证
- 订单ID前缀: `mock_order_*`

#### prod模式（谨慎使用）
- 需要运行QMT客户端
- 获取真实数据
- **允许真实交易下单**
- 适合生产环境、实盘交易
- 订单ID: xttrader返回的真实订单号

### 配置文件

所有配置集中在 `config.yml` 文件中：

```yaml
# 模式配置
modes:
  mock:
    xtquant_mode: "mock"
    allow_real_trading: false
    connect_xtquant: false
    
  dev:
    xtquant_mode: "dev"
    allow_real_trading: false  # 🔒 拦截交易
    connect_xtquant: true
    
  prod:
    xtquant_mode: "prod"
    allow_real_trading: true   # ⚠️ 允许真实交易
    connect_xtquant: true
```

### 安全机制

#### 交易拦截保护
- dev模式自动拦截所有交易请求
- 通过 `_should_use_real_trading()` 方法判断
- 仅当 `mode=prod` 且 `allow_real_trading=true` 时允许真实交易
- 日志记录所有拦截操作

## 🔧 技术架构

### 核心技术栈
- **FastAPI**: 现代高性能Web框架
- **Pydantic**: 数据验证和序列化
- **uvicorn**: ASGI服务器
- **xtquant**: 国金QMT Python SDK

### 设计模式
- **依赖注入**: 使用FastAPI的Depends系统
- **单例模式**: 服务实例全局唯一，避免重复初始化
- **策略模式**: 不同模式下的不同行为
- **拦截器模式**: 交易请求拦截保护

### 关键优化
- ✅ 配置单例加载，避免重复读取
- ✅ 服务单例管理，复用数据连接
- ✅ xtdata连接超时保护（5秒）
- ✅ 异步操作支持
- ✅ 自动API文档生成

## � 开发建议

### 本地开发流程
1. 使用 **mock模式** 进行前端开发和接口测试
2. 使用 **dev模式** 连接真实QMT进行策略开发
3. 充分测试后切换到 **prod模式** 进行实盘交易

### API认证
默认使用API Key认证，请求头格式：
```
Authorization: Bearer your-api-key
```

dev模式可用的API Key（在config.yml中配置）：
- `dev-api-key-001`
- `dev-api-key-002`

### 扩展开发
1. 在 `app/services/` 中添加新的业务服务
2. 在 `app/models/` 中定义Pydantic数据模型
3. 在 `app/routers/` 中添加API路由
4. 在 `app/dependencies.py` 中注册依赖注入

### 日志查看
```bash
# 查看实时日志
tail -f logs/app.log

# Windows PowerShell
Get-Content logs/app.log -Wait -Tail 50
```

## ⚠️ 注意事项

### 安全警告
- ⚠️ **生产环境必须修改默认API Key**
- ⚠️ **prod模式会真实下单，请谨慎使用**
- ⚠️ **建议使用HTTPS和更严格的CORS配置**
- ⚠️ **不要将包含真实账号密码的配置文件提交到Git**

### 已知限制
- xtquant仅支持Windows系统
- 需要QMT客户端正在运行（dev/prod模式）
- xtdata连接有5秒超时限制
- 连接失败会自动降级到模拟模式

### 性能建议
- 使用单例模式避免重复初始化
- xtdata连接成功后会复用
- 建议配置Redis缓存（可选）
- 考虑添加数据库持久化（可选）

## 🐛 故障排查

### 服务启动失败
1. 检查Python版本 >= 3.10
2. 确认所有依赖已安装: `pip install -r requirements.txt`
3. 检查端口8000是否被占用

### xtdata连接失败
1. 确认QMT客户端正在运行
2. 检查 `config.yml` 中的QMT路径是否正确
3. 查看日志文件: `logs/app.log`
4. 尝试重启QMT客户端

### API返回401错误
1. 检查请求头是否包含 `Authorization: Bearer xxx`
2. 确认API Key在config.yml的当前模式配置中
3. 检查API Key是否正确

### 交易被拦截
- 这是正常行为！dev模式会拦截所有交易请求
- 如需真实交易，切换到prod模式
- 检查订单ID前缀区分模拟/真实订单

## 📝 更新日志

### v1.0.0 (2024-10-23)
- ✅ 统一配置文件，支持环境变量切换模式
- ✅ 实现交易拦截保护机制
- ✅ 优化配置加载（单例模式）
- ✅ 添加xtdata连接超时保护
- ✅ 完善API测试脚本
- ✅ 更新文档和启动说明

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/liqimore/quant-qmt-proxy.git
cd quant-qmt-proxy

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_fastapi_app.py
```

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- refactor: 代码重构
- test: 测试相关

## 📄 许可证

MIT License

## 🔗 相关链接

- [FastAPI官方文档](https://fastapi.tiangolo.com/)  
- [项目仓库](https://github.com/liqimore/quant-qmt-proxy)

---

<div align="center">

**如果觉得项目有帮助，请给个 ⭐ Star 支持一下！**

</div>
