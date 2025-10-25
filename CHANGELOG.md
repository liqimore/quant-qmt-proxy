# 更新日志

## [未发布] - 2025-10-25

### 🚀 改进
- **统一启动方式**: 现在 `run.py` 默认同时启动 REST API 和 gRPC 服务
- **简化项目结构**: 删除 `run_grpc.py` 和 `run_hybrid.py`，只保留一个启动文件
- **优化启动逻辑**: 配置只加载和打印一次，避免重复信息

### 🔧 技术优化
- 使用环境变量 `_CONFIG_LOADED` 标记配置已加载，避免在 uvicorn reload 模式下重复打印
- gRPC 服务在独立线程中启动，与 FastAPI 共享同一进程空间
- 保留热重载功能，方便开发调试

### 📝 变更说明

#### 之前的启动方式
```powershell
# REST API only
python run.py

# gRPC only  
python run_grpc.py

# 混合模式 (REST + gRPC)
python run_hybrid.py
```

#### 现在的启动方式
```powershell
# 默认同时启动 REST API + gRPC
python run.py

# 通过环境变量切换模式
$env:APP_MODE="dev"; python run.py
```

### 🎯 服务端口
- **REST API**: http://0.0.0.0:8000
- **gRPC**: 0.0.0.0:50051
- **API文档**: http://0.0.0.0:8000/docs

### ✨ 优势
1. **更简单**: 只需一个命令即可启动所有服务
2. **更高效**: 配置只加载一次，避免重复初始化
3. **更清晰**: 启动日志简洁明了，不再有重复信息
4. **更统一**: 不需要选择启动哪个文件

### 📚 文档更新
- ✅ 更新 `README.md` 启动说明
- ✅ 更新 `START.md` 快速启动指南
- ✅ 优化配置加载逻辑，减少冗余日志

### ⚠️ 破坏性变更
- 删除了 `run_grpc.py` 和 `run_hybrid.py` 文件
- 如果有脚本引用这些文件，需要修改为使用 `run.py`

### 📊 启动日志对比

#### 优化前
```
🚀 加载配置，运行模式: dev
✅ 配置加载成功
   - xtquant模式: dev
   - 连接xtquant: True
   - 允许真实交易: False
...
🚀 加载配置，运行模式: dev  # 重复
✅ 配置加载成功              # 重复
   - xtquant模式: dev        # 重复
...
```

#### 优化后
```
🚀 加载配置，运行模式: dev
✅ 配置加载成功
   - xtquant模式: dev
   - 连接xtquant: True
   - 允许真实交易: False
======================================================================
🚀 启动 xtquant-proxy 服务
...
(无重复的配置加载信息)
```
