# xtquant-proxy 使用说明

## 🎯 项目概述

本项目是基于FastAPI框架构建的xtquant量化交易代理服务，提供RESTful API接口，封装xtquant的数据和交易功能。

## 🔧 核心特性

### 1. 多模式支持
- **mock模式**: 使用模拟数据，适合开发和测试
- **real模式**: 使用真实xtquant接口，允许真实交易
- **dev模式**: 使用真实xtquant接口但不下单，适合开发调试

### 2. 多环境配置
- **开发环境**: 默认使用模拟数据
- **测试环境**: 使用真实数据但不下单
- **生产环境**: 使用真实数据并允许下单

### 3. 完整的API接口
- 数据服务：市场数据、财务数据、板块数据等
- 交易服务：账户管理、订单管理、持仓查询等
- 系统服务：健康检查、配置管理等

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务

#### 开发环境（推荐）
```bash
python start.py --env dev
```

#### 测试环境
```bash
python start.py --env test
```

#### 生产环境
```bash
python start.py --env prod
```

### 3. 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📋 配置说明

### 环境配置文件

#### config_dev.yml (开发环境)
```yaml
xtquant:
  mode: "mock"  # 使用模拟数据
  trading:
    allow_real_trading: false
```

#### config_test.yml (测试环境)
```yaml
xtquant:
  mode: "dev"  # 使用真实数据但不下单
  trading:
    allow_real_trading: false
```

#### config_prod.yml (生产环境)
```yaml
xtquant:
  mode: "real"  # 使用真实数据并允许下单
  trading:
    allow_real_trading: true
```

### 主要配置项
- `xtquant.mode`: 接口模式 (mock/real/dev)
- `xtquant.trading.allow_real_trading`: 是否允许真实交易
- `security.api_keys`: API密钥列表
- `logging.level`: 日志级别

## 🔌 API使用示例

### 1. 获取市场数据
```bash
curl -X POST "http://localhost:8000/api/v1/data/market" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_codes": ["000001.SZ"],
    "start_date": "20240101",
    "end_date": "20240110",
    "period": "1d"
  }'
```

### 2. 连接交易账户
```bash
curl -X POST "http://localhost:8000/api/v1/trading/connect" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "your_account_id",
    "password": "your_password"
  }'
```

### 3. 提交订单
```bash
curl -X POST "http://localhost:8000/api/v1/trading/order/session_id" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001.SZ",
    "side": "BUY",
    "volume": 1000,
    "price": 13.20
  }'
```

## 🛠️ 开发指南

### 1. 添加新的API接口
1. 在 `app/models/` 中定义数据模型
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/routers/` 中添加API路由

### 2. 扩展xtquant功能
1. 在相应的服务类中添加新方法
2. 根据配置模式决定使用真实接口还是模拟数据
3. 添加适当的错误处理和日志记录

### 3. 自定义配置
1. 修改对应的YAML配置文件
2. 在 `app/config.py` 中添加新的配置项
3. 更新相关的服务类以使用新配置

## ⚠️ 注意事项

1. **安全配置**: 生产环境请修改默认的密钥和API密钥
2. **xtquant依赖**: 真实模式需要正确安装和配置xtquant包
3. **网络配置**: 建议使用HTTPS和适当的CORS配置
4. **日志管理**: 生产环境建议配置日志轮转和监控
5. **错误处理**: 所有API都有统一的错误响应格式

## 🔍 故障排除

### 1. xtquant模块导入失败
- 检查xtquant包是否正确安装
- 确认Python路径配置正确
- 查看系统依赖是否满足要求

### 2. 配置文件加载失败
- 检查YAML文件格式是否正确
- 确认文件路径和权限
- 查看环境变量设置

### 3. API认证失败
- 检查API密钥是否正确
- 确认请求头格式
- 查看配置中的API密钥列表

## 📞 技术支持

如有问题，请查看：
1. API文档: http://localhost:8000/docs
2. 日志文件: logs/app.log
3. 健康检查: http://localhost:8000/health/
4. 应用信息: http://localhost:8000/info
