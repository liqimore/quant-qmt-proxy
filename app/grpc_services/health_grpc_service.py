"""
gRPC 健康检查服务实现
"""
import grpc

# 导入生成的 protobuf 代码
from generated import health_pb2, health_pb2_grpc


class HealthGrpcService(health_pb2_grpc.HealthServicer):
    """gRPC 健康检查服务实现"""
    
    def Check(
        self, 
        request: health_pb2.HealthCheckRequest, 
        context: grpc.ServicerContext
    ) -> health_pb2.HealthCheckResponse:
        """健康检查"""
        # 这里可以添加实际的健康检查逻辑
        # 例如检查数据库连接、xtquant连接等
        
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )
