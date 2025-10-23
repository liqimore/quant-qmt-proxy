# 启动说明

## 快速启动

### Windows PowerShell

```powershell
# mock模式 - 不连接QMT，使用模拟数据
$env:APP_MODE="mock"; python run.py

# dev模式 - 连接QMT，获取真实数据，禁止交易（默认）
$env:APP_MODE="dev"; python run.py

# prod模式 - 连接QMT，获取真实数据，允许交易
$env:APP_MODE="prod"; python run.py
```

### Linux/Mac Bash

```bash
# mock模式
APP_MODE=mock python run.py

# dev模式（默认）
APP_MODE=dev python run.py

# prod模式
APP_MODE=prod python run.py
```

## 模式说明

| 模式 | 连接xtquant | 真实交易 | 使用场景 |
|------|------------|---------|---------|
| **mock** | ❌ 否 | ❌ 禁止 | 开发测试，无需QMT |
| **dev** | ✅ 是 | ❌ 禁止 | 开发调试，获取真实数据但不下单 |
| **prod** | ✅ 是 | ✅ 允许 | 生产环境，真实交易 |

## 配置文件

所有配置集中在 `config.yml` 文件中，通过环境变量 `APP_MODE` 选择对应的配置段。

## 测试

```powershell
# 确保服务已启动，然后运行测试
python test_fastapi_app.py
```
