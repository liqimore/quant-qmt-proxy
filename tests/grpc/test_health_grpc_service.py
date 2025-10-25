"""
健康检查服务测试

测试 gRPC 健康检查接口
"""

import pytest
import grpc
from tests.grpc.client import GRPCTestClient
from generated import health_pb2


class TestHealthGrpcService:
    """健康检查服务测试类"""
    
    @pytest.fixture
    def client(self):
        """创建 gRPC 测试客户端"""
        from tests.grpc.config import GRPC_SERVER_HOST, GRPC_SERVER_PORT
        with GRPCTestClient(host=GRPC_SERVER_HOST, port=GRPC_SERVER_PORT) as client:
            yield client
    
    def test_health_check(self, client: GRPCTestClient):
        """测试健康检查"""
        response = client.check_health(service="")
        
        assert response.status == health_pb2.HealthCheckResponse.SERVING, \
            f"服务状态异常: {response.status}"
    
    def test_health_check_specific_service(self, client: GRPCTestClient):
        """测试特定服务健康检查"""
        # 测试数据服务
        response = client.check_health(service="DataService")
        assert response.status in [
            health_pb2.HealthCheckResponse.SERVING,
            health_pb2.HealthCheckResponse.UNKNOWN
        ]
        
        # 测试交易服务
        response = client.check_health(service="TradingService")
        assert response.status in [
            health_pb2.HealthCheckResponse.SERVING,
            health_pb2.HealthCheckResponse.UNKNOWN
        ]
    
    @pytest.mark.skip(reason="流式健康检查测试需要特殊处理")
    def test_health_watch(self, client: GRPCTestClient):
        """测试健康状态订阅（流式）"""
        count = 0
        for response in client.watch_health(service=""):
            assert response.status == health_pb2.HealthCheckResponse.SERVING
            count += 1
            if count >= 3:  # 只接收 3 个响应
                break


class TestHealthGrpcServiceWithClient:
    """使用封装客户端的健康检查测试"""
    
    @pytest.fixture
    def client(self):
        """创建 gRPC 测试客户端"""
        from tests.grpc.config import GRPC_SERVER_HOST, GRPC_SERVER_PORT
        with GRPCTestClient(host=GRPC_SERVER_HOST, port=GRPC_SERVER_PORT) as client:
            yield client
    
    def test_health_check_with_logging(self, client: GRPCTestClient):
        """测试健康检查（带日志）"""
        response = client.check_health()
        client.log_response(response, "健康检查")
        
        assert response.status == health_pb2.HealthCheckResponse.SERVING


@pytest.mark.performance
class TestHealthGrpcServicePerformance:
    """健康检查服务性能测试"""
    
    @pytest.fixture
    def client(self):
        """创建 gRPC 测试客户端"""
        from tests.grpc.config import GRPC_SERVER_HOST, GRPC_SERVER_PORT
        with GRPCTestClient(host=GRPC_SERVER_HOST, port=GRPC_SERVER_PORT) as client:
            yield client
    
    def test_health_check_performance(self, client: GRPCTestClient, performance_timer):
        """测试健康检查性能"""
        performance_timer.start()
        response = client.check_health()
        elapsed = performance_timer.stop()
        
        assert response.status == health_pb2.HealthCheckResponse.SERVING
        assert performance_timer.elapsed_ms() < 100, \
            f"健康检查耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 100ms"
