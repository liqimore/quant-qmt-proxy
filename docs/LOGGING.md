# 日志系统使用指南

## 概述

项目已升级为完整的文件日志系统，基于 `loguru` 库实现，支持：

- ✅ 自动输出到文件（默认 `logs/app.log`）
- ✅ 错误日志单独记录（`logs/error.log`）
- ✅ 日志文件自动轮转（超过10MB自动切分）
- ✅ 旧日志自动压缩保存（zip格式）
- ✅ 日志保留30天后自动删除
- ✅ 可配置日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- ✅ 开发模式同时输出到控制台和文件
- ✅ 生产模式可配置仅输出到文件
- ✅ REST API 和 gRPC 使用统一日志配置

## 配置说明

### 全局配置（config.yml）

```yaml
# 日志配置
logging:
  file: "logs/app.log"              # 主日志文件
  error_file: "logs/error.log"      # 错误日志文件（仅ERROR及以上级别）
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
  rotation: "10 MB"                 # 日志文件轮转大小
  retention: "30 days"              # 日志保留时间
  compression: "zip"                # 压缩格式
  console_output: true              # 是否同时输出到控制台
  backtrace: true                   # 是否显示完整堆栈跟踪
  diagnose: false                   # 是否显示诊断信息
```

### 模式特定配置

可以在不同的运行模式（mock/dev/prod）中覆盖全局配置：

```yaml
modes:
  dev:
    log_level: "DEBUG"              # 开发模式使用DEBUG级别
    # 其他日志配置继承全局配置
  
  prod:
    log_level: "INFO"               # 生产模式使用INFO级别
    logging:
      console_output: false         # 生产模式不输出到控制台
      diagnose: false               # 生产模式不启用诊断
```

## 日志级别说明

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| **DEBUG** | 详细的调试信息 | 开发调试、问题排查 |
| **INFO** | 一般信息 | 正常运行的关键节点 |
| **WARNING** | 警告信息 | 需要注意但不影响运行 |
| **ERROR** | 错误信息 | 程序仍可继续运行的错误 |
| **CRITICAL** | 严重错误 | 可能导致程序崩溃的错误 |

## 日志文件结构

```
logs/
├── app.log              # 主日志文件（所有级别）
├── app.log.zip          # 压缩的历史日志
├── error.log            # 错误日志（ERROR及以上）
└── error.log.zip        # 压缩的历史错误日志
```

## 使用方法

### 1. 基本使用（推荐）

```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 2. 使用内置日志函数

```python
from app.utils.logger import (
    log_api_request,
    log_api_response,
    log_grpc_request,
    log_grpc_response,
    log_xtquant_call,
    log_exception,
    log_performance
)

# 记录API请求
log_api_request("GET", "/api/data/kline", {"stock_code": "000001.SZ"})

# 记录API响应
log_api_response("/api/data/kline", 200, 123.45)

# 记录gRPC请求
log_grpc_request("DataService", "GetKline", {"stock_code": "000001.SZ"})

# 记录异常
try:
    # 业务代码
    pass
except Exception as e:
    log_exception(e, "处理数据时发生错误")

# 记录性能
log_performance("数据查询", 1234.5, threshold_ms=1000)
```

### 3. 直接使用 loguru

```python
from loguru import logger

logger.info("这是一条信息日志")
logger.error("这是一条错误日志")

# 带上下文信息
logger.bind(user_id=123, request_id="abc").info("用户操作")

# 异常日志（自动捕获堆栈）
try:
    1 / 0
except Exception:
    logger.exception("发生除零错误")
```

## 配置参数详解

### rotation（日志轮转）

控制何时创建新的日志文件：

- `"10 MB"` - 文件大小超过10MB时轮转
- `"500 KB"` - 文件大小超过500KB时轮转
- `"1 day"` - 每天轮转
- `"12:00"` - 每天中午12点轮转
- `"1 week"` - 每周轮转

### retention（日志保留）

控制日志文件保留多久：

- `"30 days"` - 保留30天
- `"1 week"` - 保留1周
- `"2 months"` - 保留2个月
- `10` - 保留最近10个文件

### compression（压缩格式）

旧日志的压缩格式：

- `"zip"` - ZIP压缩（推荐，Windows兼容性好）
- `"gz"` - GZIP压缩
- `"tar.gz"` - TAR.GZ压缩
- `"bz2"` - BZIP2压缩

## 环境变量控制

通过 `APP_MODE` 环境变量切换不同的日志配置：

```bash
# Windows PowerShell
$env:APP_MODE="dev"    # 开发模式 - DEBUG级别
$env:APP_MODE="prod"   # 生产模式 - INFO级别

# Linux/Mac
export APP_MODE=dev
export APP_MODE=prod
```

## 生产环境建议

```yaml
modes:
  prod:
    log_level: "INFO"           # 不要使用DEBUG，避免日志过多
    logging:
      console_output: false     # 关闭控制台输出
      rotation: "50 MB"         # 适当增加轮转大小
      retention: "90 days"      # 根据需求调整保留时间
      compression: "zip"        # 压缩节省空间
      diagnose: false           # 关闭诊断信息
```

## 日志查看

### Windows 用户

#### 方法1：使用提供的批处理文件（推荐）

```bash
# 查看应用日志
view_app_log.bat

# 查看错误日志
view_error_log.bat
```

#### 方法2：使用 PowerShell 脚本

```bash
# 查看最后 50 行日志
.\view_logs.ps1

# 查看最后 100 行日志
.\view_logs.ps1 -Lines 100

# 实时跟踪日志（类似 tail -f）
.\view_logs.ps1 -Follow

# 查看错误日志
.\view_logs.ps1 -ErrorLog
```

#### 方法3：使用 PowerShell（手动指定编码）

```powershell
# 查看应用日志
Get-Content logs\app.log -Encoding UTF8 -Tail 50

# 实时跟踪日志
Get-Content logs\app.log -Encoding UTF8 -Wait -Tail 50

# 查看错误日志
Get-Content logs\error.log -Encoding UTF8
```

**注意**：必须使用 `-Encoding UTF8` 参数，否则中文会显示为乱码。

### Linux/Mac 用户

### Linux/Mac 用户

```bash
# 实时查看日志
tail -f logs/app.log

# 查看最后100行
tail -n 100 logs/app.log

# 查看错误日志
tail -f logs/error.log
```

### 搜索日志

#### Windows

```powershell
# 搜索包含 "ERROR" 的日志
Select-String -Path logs\app.log -Pattern "ERROR" -Encoding UTF8

# 搜索特定股票代码的日志
Select-String -Path logs\app.log -Pattern "000001.SZ" -Encoding UTF8
```

#### Linux/Mac

```bash
# 搜索包含 "ERROR" 的日志
grep "ERROR" logs/app.log

# 搜索特定股票代码的日志
grep "000001.SZ" logs/app.log
```

## 常见问题

### Q: 日志文件在哪里？

A: 默认在项目根目录的 `logs/` 文件夹中，包括：
- `logs/app.log` - 主日志
- `logs/error.log` - 错误日志

### Q: Windows 下日志文件中文显示乱码怎么办？

A: 日志文件使用 UTF-8 编码，查看时需要指定编码：

**解决方案1（推荐）**：使用提供的批处理文件
```bash
view_app_log.bat      # 查看应用日志
view_error_log.bat    # 查看错误日志
```

**解决方案2**：使用 PowerShell 脚本
```bash
.\view_logs.ps1
```

**解决方案3**：手动指定编码
```powershell
Get-Content logs\app.log -Encoding UTF8 -Tail 50
```

**解决方案4**：使用支持 UTF-8 的编辑器查看
- VS Code（推荐）
- Notepad++
- Sublime Text

**不推荐**：Windows 记事本可能无法正确显示 UTF-8 编码

### Q: 如何修改日志级别？

A: 在 `config.yml` 中修改对应模式的 `log_level` 配置，或通过环境变量切换运行模式。

### Q: 日志文件太大怎么办？

A: 日志会自动轮转，超过配置的大小（默认10MB）会自动创建新文件，旧文件会被压缩。

### Q: 如何在生产环境关闭控制台输出？

A: 在 `config.yml` 的 `prod` 模式下设置：
```yaml
modes:
  prod:
    logging:
      console_output: false
```

### Q: 如何延长日志保留时间？

A: 在 `config.yml` 中修改 `retention` 配置：
```yaml
logging:
  retention: "90 days"  # 保留90天
```

## 性能优化

日志系统已启用以下性能优化：

1. **异步写入** (`enqueue=True`) - 日志写入不阻塞主线程
2. **自动压缩** - 旧日志自动压缩，节省磁盘空间
3. **按级别分文件** - 错误日志单独记录，便于快速定位问题
4. **可配置控制台输出** - 生产环境可关闭控制台输出，提升性能

## 更多资源

- [Loguru 官方文档](https://loguru.readthedocs.io/)
- [项目配置文件](../config.yml)
- [日志工具模块](../app/utils/logger.py)
