# FastAPI + xtquant 量化交易代理服务

基于FastAPI框架构建的xtquant量化交易代理服务，提供RESTful API接口，封装xtquant的数据和交易功能。

## 项目结构
```
quant-qmt-proxy/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py              # 配置管理
│   ├── dependencies.py        # 依赖注入
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── data_models.py     # 数据相关模型
│   │   └── trading_models.py  # 交易相关模型
│   ├── routers/               # API路由
│   │   ├── __init__.py
│   │   ├── data.py           # 数据服务路由
│   │   ├── trading.py        # 交易服务路由
│   │   └── health.py         # 健康检查路由
│   ├── services/             # 业务服务层
│   │   ├── __init__.py
│   │   ├── data_service.py   # 数据服务
│   │   └── trading_service.py # 交易服务
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── exceptions.py     # 异常处理
│       └── helpers.py        # 辅助函数
├── requirements.txt          # 项目依赖
├── env.example              # 环境变量示例
├── run.py                   # 启动脚本
├── test_api.py              # API测试脚本
├── README.md                # 项目说明
└── xtquant/                 # xtquant包(已存在)
```

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

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp env.example .env
# 编辑 .env 文件，修改相关配置
```

### 3. 启动服务
```bash
# 方式1: 使用启动脚本
python run.py

# 方式2: 直接运行
python app/main.py

# 方式3: 使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. 运行测试
```bash
python test_api.py
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

## 配置说明

### 环境变量
- `APP_NAME`: 应用名称
- `APP_VERSION`: 应用版本
- `DEBUG`: 调试模式
- `HOST`: 服务主机
- `PORT`: 服务端口
- `LOG_LEVEL`: 日志级别
- `LOG_FILE`: 日志文件路径
- `XTQUANT_DATA_PATH`: xtquant数据路径
- `XTQUANT_CONFIG_PATH`: xtquant配置路径
- `SECRET_KEY`: 密钥
- `API_KEY_HEADER`: API密钥头

## 开发说明

### 项目特点
- 🚀 基于FastAPI框架，性能优异
- 📝 完整的类型注解和文档
- 🔒 统一的异常处理和错误响应
- 🧪 包含API测试脚本
- 📊 支持异步操作
- 🔧 灵活的配置管理
- 📝 详细的日志记录

### 扩展开发
1. 在 `app/services/` 中添加新的业务服务
2. 在 `app/models/` 中定义数据模型
3. 在 `app/routers/` 中添加API路由
4. 在 `app/utils/` 中添加工具函数

### 注意事项
- 当前版本使用模拟数据，实际使用时需要连接真实的xtquant服务
- 生产环境请修改默认的密钥和认证配置
- 建议使用HTTPS和更严格的CORS配置
- 可以根据需要添加数据库支持

## 许可证
MIT License
