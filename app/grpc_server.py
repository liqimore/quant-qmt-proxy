"""
gRPC 服务器
"""
import grpc
from concurrent import futures
import sys

from generated import data_pb2_grpc, trading_pb2_grpc, health_pb2_grpc
from app.grpc_services.data_grpc_service import DataGrpcService
from app.grpc_services.trading_grpc_service import TradingGrpcService
from app.grpc_services.health_grpc_service import HealthGrpcService
from app.config import get_settings
from app.utils.logger import configure_logging, logger


def serve():
    """启动 gRPC 服务器"""
    settings = get_settings()
    
    # 初始化日志系统
    configure_logging(
        log_level=settings.logging.level,
        log_file=settings.logging.file or "logs/app.log",
        error_log_file=settings.logging.error_file or "logs/error.log",
        log_format=settings.logging.format,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        compression=settings.logging.compression
    )
    
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
    
    # 使用依赖注入中的单例服务实例
    from app.dependencies import get_data_service, get_trading_service
    data_service = get_data_service(settings)
    trading_service = get_trading_service(settings)
    
    # 注册服务
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
    logger.info(f"gRPC 服务已就绪 (工作线程: {max_workers})")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("gRPC 服务正在关闭...")
        server.stop(grace=5)
        logger.info("gRPC 服务已关闭")


if __name__ == '__main__':
    serve()
