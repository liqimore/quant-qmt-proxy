"""
gRPC 服务器
"""
import grpc
from concurrent import futures
import logging
import sys

from generated import data_pb2_grpc, trading_pb2_grpc, health_pb2_grpc
from app.grpc_services.data_grpc_service import DataGrpcService
from app.grpc_services.trading_grpc_service import TradingGrpcService
from app.grpc_services.health_grpc_service import HealthGrpcService
from app.services.data_service import DataService
from app.services.trading_service import TradingService
from app.config import get_settings


def serve():
    """启动 gRPC 服务器"""
    settings = get_settings()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # 获取 gRPC 配置
    grpc_host = getattr(settings, 'grpc_host', '0.0.0.0')
    grpc_port = getattr(settings, 'grpc_port', 50051)
    max_workers = getattr(settings, 'grpc_max_workers', 10)
    
    # 创建服务器
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.so_reuseport', 1),
            ('grpc.max_connection_idle_ms', 30000),
        ]
    )
    
    # 创建服务实例
    logger.info("正在初始化服务...")
    data_service = DataService(settings)
    trading_service = TradingService(settings)
    
    # 注册服务
    logger.info("正在注册 gRPC 服务...")
    data_pb2_grpc.add_DataServiceServicer_to_server(
        DataGrpcService(data_service), 
        server
    )
    trading_pb2_grpc.add_TradingServiceServicer_to_server(
        TradingGrpcService(trading_service), 
        server
    )
    health_pb2_grpc.add_HealthServicer_to_server(
        HealthGrpcService(), 
        server
    )
    
    # 绑定端口
    server_address = f'{grpc_host}:{grpc_port}'
    server.add_insecure_port(server_address)
    
    # 启动服务器
    server.start()
    logger.info(f"=" * 70)
    logger.info(f"🚀 gRPC 服务器已启动")
    logger.info(f"   地址: {server_address}")
    logger.info(f"   工作线程: {max_workers}")
    logger.info(f"   模式: {settings.xtquant.mode.value}")
    logger.info(f"=" * 70)
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("\n正在关闭 gRPC 服务器...")
        server.stop(grace=5)
        logger.info("gRPC 服务器已关闭")


if __name__ == '__main__':
    serve()
