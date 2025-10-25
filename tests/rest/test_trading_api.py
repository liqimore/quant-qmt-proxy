"""
交易服务接口测试

测试所有交易服务相关的 API 端点
"""

import pytest
import httpx
from tests.rest.client import RESTTestClient


class TestTradingAPI:
    """交易服务接口测试类"""
    
    def test_connect_account(self, http_client: httpx.Client):
        """测试连接交易账户"""
        from tests.rest.config import TEST_ACCOUNT_ID, TEST_ACCOUNT_PASSWORD, TEST_ACCOUNT_TYPE
        
        data = {
            "account_id": TEST_ACCOUNT_ID,
            "password": TEST_ACCOUNT_PASSWORD,
            "account_type": TEST_ACCOUNT_TYPE
        }
        
        response = http_client.post("/api/v1/trading/connect", json=data)
        assert response.status_code == 200
        
        result = response.json()
        # 响应可能在根级别或 data 字段中包含 session_id
        assert "session_id" in result or ("data" in result and "session_id" in result["data"])
    
    def test_get_account_info(self, http_client: httpx.Client, test_session: str):
        """测试获取账户信息"""
        response = http_client.get(f"/api/v1/trading/account/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "account" in result
    
    def test_get_positions(self, http_client: httpx.Client, test_session: str):
        """测试获取持仓信息"""
        response = http_client.get(f"/api/v1/trading/positions/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "positions" in result
    
    def test_get_asset(self, http_client: httpx.Client, test_session: str):
        """测试获取资产信息"""
        response = http_client.get(f"/api/v1/trading/asset/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "asset" in result
    
    def test_get_risk(self, http_client: httpx.Client, test_session: str):
        """测试获取风险信息"""
        response = http_client.get(f"/api/v1/trading/risk/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "risk" in result
    
    def test_get_strategies(self, http_client: httpx.Client, test_session: str):
        """测试获取策略列表"""
        response = http_client.get(f"/api/v1/trading/strategies/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "strategies" in result
    
    def test_get_orders(self, http_client: httpx.Client, test_session: str):
        """测试获取订单列表"""
        response = http_client.get(f"/api/v1/trading/orders/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "orders" in result
    
    def test_get_trades(self, http_client: httpx.Client, test_session: str):
        """测试获取成交记录"""
        response = http_client.get(f"/api/v1/trading/trades/{test_session}")
        
        # 如果账户未连接，应该返回400
        if response.status_code == 400:
            result = response.json()
            assert "账户未连接" in result.get("message", "")
        else:
            assert response.status_code == 200
            result = response.json()
            assert "data" in result or "trades" in result
    
    @pytest.mark.skip(reason="下单测试可能影响真实账户，默认跳过")
    def test_submit_order(self, http_client: httpx.Client, test_session: str):
        """测试提交订单（默认跳过）"""
        data = {
            "stock_code": "000001.SZ",
            "side": "BUY",
            "volume": 100,
            "price": 13.50,
            "order_type": "LIMIT"
        }
        
        response = http_client.post(f"/api/v1/trading/order/{test_session}", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "order_id" in result or ("data" in result and "order_id" in result["data"])
    
    @pytest.mark.skip(reason="撤单测试需要真实订单ID，默认跳过")
    def test_cancel_order(self, http_client: httpx.Client, test_session: str):
        """测试撤销订单（默认跳过）"""
        data = {"order_id": "order_1000"}
        
        response = http_client.post(f"/api/v1/trading/cancel/{test_session}", json=data)
        # 可能返回 200 或 404（订单不存在）
        assert response.status_code in [200, 404]
    
    def test_disconnect_account(self, http_client: httpx.Client):
        """测试断开账户连接"""
        from tests.rest.config import TEST_ACCOUNT_ID, TEST_ACCOUNT_PASSWORD, TEST_ACCOUNT_TYPE
        
        # 先连接
        connect_data = {
            "account_id": TEST_ACCOUNT_ID,
            "password": TEST_ACCOUNT_PASSWORD,
            "account_type": TEST_ACCOUNT_TYPE
        }
        
        connect_response = http_client.post("/api/v1/trading/connect", json=connect_data)
        assert connect_response.status_code == 200
        
        connect_result = connect_response.json()
        session_id = connect_result.get("session_id", "test_session")
        
        # 断开连接
        disconnect_response = http_client.post(f"/api/v1/trading/disconnect/{session_id}")
        assert disconnect_response.status_code == 200


class TestTradingAPIWithClient:
    """使用封装客户端的交易服务测试"""
    
    @pytest.fixture
    def client(self, base_url: str, api_key: str):
        """创建测试客户端"""
        with RESTTestClient(base_url=base_url, api_key=api_key) as client:
            yield client
    
    def test_connect_with_client(self, client: RESTTestClient):
        """使用客户端测试连接账户"""
        from tests.rest.config import TEST_ACCOUNT_ID, TEST_ACCOUNT_PASSWORD, TEST_ACCOUNT_TYPE
        
        response = client.connect(
            account_id=TEST_ACCOUNT_ID,
            password=TEST_ACCOUNT_PASSWORD,
            account_type=TEST_ACCOUNT_TYPE
        )
        
        result = client.assert_success(response)
        assert "session_id" in result or ("data" in result and "session_id" in result["data"])
    
    def test_account_info_with_client(self, client: RESTTestClient, test_session: str):
        """使用客户端测试获取账户信息"""
        response = client.get_account_info(session_id=test_session)
        
        # 如果账户未连接，assert_success会抛出异常，检查异常消息
        try:
            result = client.assert_success(response)
            assert "data" in result or "account" in result
        except AssertionError as e:
            # 如果是账户未连接错误，认为是预期行为
            assert "账户未连接" in str(e) or "400" in str(e)
    
    def test_positions_with_client(self, client: RESTTestClient, test_session: str):
        """使用客户端测试获取持仓"""
        response = client.get_positions(session_id=test_session)
        
        try:
            result = client.assert_success(response)
            assert "data" in result or "positions" in result
        except AssertionError as e:
            assert "账户未连接" in str(e) or "400" in str(e)
    
    def test_asset_with_client(self, client: RESTTestClient, test_session: str):
        """使用客户端测试获取资产"""
        response = client.get_asset(session_id=test_session)
        
        try:
            result = client.assert_success(response)
            assert "data" in result or "asset" in result
        except AssertionError as e:
            assert "账户未连接" in str(e) or "400" in str(e)
    
    def test_orders_with_client(self, client: RESTTestClient, test_session: str):
        """使用客户端测试获取订单"""
        response = client.get_orders(session_id=test_session)
        
        try:
            result = client.assert_success(response)
            assert "data" in result or "orders" in result
        except AssertionError as e:
            assert "账户未连接" in str(e) or "400" in str(e)
    
    def test_trades_with_client(self, client: RESTTestClient, test_session: str):
        """使用客户端测试获取成交"""
        response = client.get_trades(session_id=test_session)
        
        try:
            result = client.assert_success(response)
            assert "data" in result or "trades" in result
        except AssertionError as e:
            assert "账户未连接" in str(e) or "400" in str(e)
    
    def test_disconnect_with_client(self, client: RESTTestClient):
        """使用客户端测试断开连接"""
        from tests.rest.config import TEST_ACCOUNT_ID, TEST_ACCOUNT_PASSWORD, TEST_ACCOUNT_TYPE
        
        # 先连接
        connect_response = client.connect(
            account_id=TEST_ACCOUNT_ID,
            password=TEST_ACCOUNT_PASSWORD,
            account_type=TEST_ACCOUNT_TYPE
        )
        connect_result = client.assert_success(connect_response)
        session_id = connect_result.get("session_id", "test_session")
        
        # 断开连接
        disconnect_response = client.disconnect(session_id=session_id)
        client.assert_success(disconnect_response)


@pytest.mark.performance
class TestTradingAPIPerformance:
    """交易服务接口性能测试"""
    
    def test_query_positions_performance(self, http_client: httpx.Client, test_session: str, performance_timer):
        """测试查询持仓性能"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        performance_timer.start()
        response = http_client.get(f"/api/v1/trading/positions/{test_session}")
        elapsed = performance_timer.stop()
        
        # 如果账户未连接，跳过性能测试
        if response.status_code == 400:
            result = response.json()
            if "账户未连接" in result.get("message", ""):
                pytest.skip("账户未连接，跳过性能测试")
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["query_positions"], \
            f"查询持仓耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['query_positions']}ms"
    
    @pytest.mark.skip(reason="提交订单性能测试可能影响真实账户")
    def test_submit_order_performance(self, http_client: httpx.Client, test_session: str, performance_timer):
        """测试提交订单性能（默认跳过）"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        data = {
            "stock_code": "000001.SZ",
            "side": "BUY",
            "volume": 100,
            "price": 13.50,
            "order_type": "LIMIT"
        }
        
        performance_timer.start()
        response = http_client.post(f"/api/v1/trading/order/{test_session}", json=data)
        elapsed = performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["submit_order"], \
            f"提交订单耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['submit_order']}ms"


@pytest.mark.integration
class TestTradingAPIIntegration:
    """交易服务接口集成测试"""
    
    def test_complete_trading_workflow(self, http_client: httpx.Client):
        """测试完整的交易工作流（不包含下单）"""
        from tests.rest.config import TEST_ACCOUNT_ID, TEST_ACCOUNT_PASSWORD, TEST_ACCOUNT_TYPE
        
        # 1. 连接账户
        connect_data = {
            "account_id": TEST_ACCOUNT_ID,
            "password": TEST_ACCOUNT_PASSWORD,
            "account_type": TEST_ACCOUNT_TYPE
        }
        
        connect_response = http_client.post("/api/v1/trading/connect", json=connect_data)
        assert connect_response.status_code == 200
        
        connect_result = connect_response.json()
        session_id = connect_result.get("session_id", "test_session")
        
        try:
            # 2. 获取账户信息
            account_response = http_client.get(f"/api/v1/trading/account/{session_id}")
            assert account_response.status_code == 200
            
            # 3. 获取持仓
            positions_response = http_client.get(f"/api/v1/trading/positions/{session_id}")
            assert positions_response.status_code == 200
            
            # 4. 获取资产
            asset_response = http_client.get(f"/api/v1/trading/asset/{session_id}")
            assert asset_response.status_code == 200
            
            # 5. 获取订单
            orders_response = http_client.get(f"/api/v1/trading/orders/{session_id}")
            assert orders_response.status_code == 200
            
            # 6. 获取成交
            trades_response = http_client.get(f"/api/v1/trading/trades/{session_id}")
            assert trades_response.status_code == 200
            
        finally:
            # 7. 断开连接
            disconnect_response = http_client.post(f"/api/v1/trading/disconnect/{session_id}")
            assert disconnect_response.status_code == 200
