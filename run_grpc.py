"""
启动 gRPC 服务器
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from app.grpc_server import serve

if __name__ == '__main__':
    serve()
