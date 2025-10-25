"""
健康检查接口测试

测试所有健康检查相关的 API 端点
"""

import pytest
import httpx
from tests.rest.client import RESTTestClient


class TestHealthAPI:
    """健康检查接口测试类"""
    
    def test_root_endpoint(self, http_client: httpx.Client):
        """测试根路径"""
        response = http_client.get("/")
        assert response.status_code == 200
    
    def test_info_endpoint(self, http_client: httpx.Client):
        """测试应用信息端点"""
        response = http_client.get("/info")
        assert response.status_code == 200
        
        result = response.json()
        # 响应格式: {"code": 200, "data": {...}, "success": true}
        if "data" in result:
            data = result["data"]
            assert "app_name" in data or "name" in data
        else:
            assert "name" in result or "app_name" in result
    
    def test_health_check(self, http_client: httpx.Client):
        """测试健康检查端点"""
        response = http_client.get("/health/")
        assert response.status_code == 200
        
        result = response.json()
        # 响应可能有data字段嵌套
        if "data" in result:
            assert "status" in result["data"]
        else:
            assert "status" in result
    
    def test_ready_check(self, http_client: httpx.Client):
        """测试就绪检查端点"""
        response = http_client.get("/health/ready")
        assert response.status_code == 200
        
        result = response.json()
        # 响应可能有data字段嵌套
        if "data" in result:
            assert "status" in result["data"] or "ready" in result["data"]
        else:
            assert "status" in result or "ready" in result
    
    def test_live_check(self, http_client: httpx.Client):
        """测试存活检查端点"""
        response = http_client.get("/health/live")
        assert response.status_code == 200
        
        result = response.json()
        # 响应可能有data字段嵌套
        if "data" in result:
            assert "status" in result["data"] or "alive" in result["data"]
        else:
            assert "status" in result or "alive" in result


class TestHealthAPIWithClient:
    """使用封装客户端的健康检查测试"""
    
    @pytest.fixture
    def client(self, base_url: str, api_key: str):
        """创建测试客户端"""
        with RESTTestClient(base_url=base_url, api_key=api_key) as client:
            yield client
    
    def test_root_with_client(self, client: RESTTestClient):
        """使用客户端测试根路径"""
        response = client.get_root()
        result = client.assert_success(response)
    
    def test_info_with_client(self, client: RESTTestClient):
        """使用客户端测试应用信息"""
        response = client.get_info()
        result = client.assert_success(response)
        # 检查data字段或根级别
        if "data" in result:
            assert "app_version" in result["data"] or "version" in result["data"]
        else:
            assert "version" in result or "app_version" in result
    
    def test_health_with_client(self, client: RESTTestClient):
        """使用客户端测试健康检查"""
        response = client.check_health()
        result = client.assert_success(response)
        # 检查data字段或根级别
        if "data" in result:
            assert "status" in result["data"]
        else:
            assert "status" in result
    
    def test_ready_with_client(self, client: RESTTestClient):
        """使用客户端测试就绪检查"""
        response = client.check_ready()
        result = client.assert_success(response)
    
    def test_live_with_client(self, client: RESTTestClient):
        """使用客户端测试存活检查"""
        response = client.check_live()
        result = client.assert_success(response)


@pytest.mark.performance
class TestHealthAPIPerformance:
    """健康检查接口性能测试"""
    
    def test_health_check_performance(self, http_client: httpx.Client, performance_timer):
        """测试健康检查性能"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        performance_timer.start()
        response = http_client.get("/health/")
        elapsed = performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["health_check"], \
            f"健康检查耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['health_check']}ms"
