"""
订阅API测试
"""
import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import Mock, patch, AsyncMock
from app.main import app
from app.config import get_settings


@pytest.fixture(scope="session")
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture(scope="session")
def api_key():
    """测试用API密钥"""
    settings = get_settings()
    if settings.security.api_keys:
        return settings.security.api_keys[0]
    return "mock-api-key-001"


class TestSubscriptionAPI:
    """订阅API测试"""
    
    def test_create_subscription(self, client, api_key):
        """测试创建订阅"""
        # 准备请求数据
        request_data = {
            "symbols": ["000001.SZ", "600000.SH"],
            "adjust_type": "none",
            "subscription_type": "quote"
        }
        
        # 发送请求
        response = client.post(
            "/api/v1/data/subscription",
            json=request_data,
            headers={"X-API-Key": api_key}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "subscription_id" in data
        assert data["status"] == "active"
        assert "created_at" in data
        assert data["subscription_type"] == "quote"
        
        # 保存subscription_id供后续测试使用
        return data["subscription_id"]
    
    def test_create_subscription_without_api_key(self, client):
        """测试无API密钥创建订阅"""
        request_data = {
            "symbols": ["000001.SZ"],
            "adjust_type": "none",
            "subscription_type": "quote"
        }
        
        response = client.post(
            "/api/v1/data/subscription",
            json=request_data
        )
        
        # 应该返回401未授权
        assert response.status_code == 401
    
    def test_get_subscription_info(self, client, api_key):
        """测试获取订阅信息"""
        # 先创建一个订阅
        create_response = client.post(
            "/api/v1/data/subscription",
            json={
                "symbols": ["000001.SZ"],
                "adjust_type": "none",
                "subscription_type": "quote"
            },
            headers={"X-API-Key": api_key}
        )
        assert create_response.status_code == 200
        subscription_id = create_response.json()["subscription_id"]
        
        # 获取订阅信息
        response = client.get(
            f"/api/v1/data/subscription/{subscription_id}",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        info = response.json()
        assert info["subscription_id"] == subscription_id
        assert "symbols" in info
        assert "adjust_type" in info
        assert "active" in info
    
    def test_get_nonexistent_subscription(self, client, api_key):
        """测试获取不存在的订阅"""
        response = client.get(
            "/api/v1/data/subscription/nonexistent_id",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 404
    
    def test_list_subscriptions(self, client, api_key):
        """测试列出所有订阅"""
        # 创建几个订阅
        for i in range(2):
            client.post(
                "/api/v1/data/subscription",
                json={
                    "symbols": [f"00000{i}.SZ"],
                    "adjust_type": "none",
                    "subscription_type": "quote"
                },
                headers={"X-API-Key": api_key}
            )
        
        # 列出所有订阅
        response = client.get(
            "/api/v1/data/subscriptions",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
        assert "total" in data
        assert data["total"] >= 2
    
    def test_delete_subscription(self, client, api_key):
        """测试取消订阅"""
        # 创建订阅
        create_response = client.post(
            "/api/v1/data/subscription",
            json={
                "symbols": ["000001.SZ"],
                "adjust_type": "none",
                "subscription_type": "quote"
            },
            headers={"X-API-Key": api_key}
        )
        subscription_id = create_response.json()["subscription_id"]
        
        # 取消订阅
        response = client.delete(
            f"/api/v1/data/subscription/{subscription_id}",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # 验证订阅已不存在
        get_response = client.get(
            f"/api/v1/data/subscription/{subscription_id}",
            headers={"X-API-Key": api_key}
        )
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_subscription(self, client, api_key):
        """测试取消不存在的订阅（幂等操作）"""
        response = client.delete(
            "/api/v1/data/subscription/nonexistent_id",
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    
    def test_create_subscription_with_invalid_adjust_type(self, client, api_key):
        """测试使用无效复权类型创建订阅"""
        request_data = {
            "symbols": ["000001.SZ"],
            "adjust_type": "invalid",
            "subscription_type": "quote"
        }
        
        response = client.post(
            "/api/v1/data/subscription",
            json=request_data,
            headers={"X-API-Key": api_key}
        )
        
        # 应该返回验证错误
        assert response.status_code == 422
    
    def test_create_subscription_with_empty_symbols(self, client, api_key):
        """测试使用空股票列表创建订阅"""
        request_data = {
            "symbols": [],
            "adjust_type": "none",
            "subscription_type": "quote"
        }
        
        response = client.post(
            "/api/v1/data/subscription",
            json=request_data,
            headers={"X-API-Key": api_key}
        )
        
        # 应该返回422验证错误
        assert response.status_code == 422
        response_json = response.json()
        assert "detail" in response_json
        # Pydantic validation error will have a different structure
        if isinstance(response_json["detail"], list):
            # Pydantic validation error format
            assert any("symbols" in str(err) for err in response_json["detail"])
        else:
            # Our custom error format
            assert "股票代码列表不能为空" in str(response_json["detail"])


class TestWebSocketAPI:
    """WebSocket API测试"""
    
    def test_websocket_test_page(self, client):
        """测试WebSocket测试页面"""
        response = client.get("/ws/test")
        
        assert response.status_code == 200
        assert "WebSocket" in response.text
        assert "text/html" in response.headers.get("content-type", "")
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, client, api_key):
        """测试WebSocket连接（Mock模式）"""
        # 先创建订阅
        create_response = client.post(
            "/api/v1/data/subscription",
            json={
                "symbols": ["000001.SZ"],
                "adjust_type": "none",
                "subscription_type": "quote"
            },
            headers={"X-API-Key": api_key}
        )
        subscription_id = create_response.json()["subscription_id"]
        
        # 连接WebSocket
        with client.websocket_connect(f"/ws/quote/{subscription_id}") as websocket:
            # 接收连接确认
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["subscription_id"] == subscription_id
            
            # 接收至少一条行情数据
            data = websocket.receive_json()
            assert data["type"] == "quote"
            assert "data" in data
            assert "stock_code" in data["data"]
    
    @pytest.mark.asyncio
    async def test_websocket_invalid_subscription(self, client):
        """测试无效订阅ID的WebSocket连接"""
        with client.websocket_connect("/ws/quote/invalid_id") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
