"""
gRPC订阅服务测试
"""
import pytest
import grpc
from unittest.mock import Mock, patch
import asyncio

from generated import data_pb2, data_pb2_grpc
from app.grpc_services.data_grpc_service import DataGrpcService
from app.services.data_service import DataService
from app.config import get_settings


@pytest.fixture
def settings():
    """获取配置"""
    return get_settings()


@pytest.fixture
def data_service(settings):
    """创建数据服务实例"""
    return DataService(settings)


@pytest.fixture
def grpc_service(data_service):
    """创建gRPC服务实例"""
    return DataGrpcService(data_service)


@pytest.fixture
def grpc_context():
    """Mock gRPC上下文"""
    context = Mock(spec=grpc.ServicerContext)
    context.is_active.return_value = True
    return context


class TestSubscriptionGrpc:
    """gRPC订阅服务测试"""
    
    def test_subscribe_quote_mock_mode(self, grpc_service, grpc_context):
        """测试订阅行情（Mock模式）"""
        # 创建订阅请求
        request = data_pb2.SubscriptionRequest(
            symbols=["000001.SZ", "600000.SH"],
            adjust_type="none",
            subscription_type=data_pb2.SUBSCRIPTION_QUOTE
        )
        
        # 调用订阅方法（流式返回）
        response_stream = grpc_service.SubscribeQuote(request, grpc_context)
        
        # 接收几条数据
        count = 0
        for quote_update in response_stream:
            assert isinstance(quote_update, data_pb2.QuoteUpdate)
            assert quote_update.stock_code in ["000001.SZ", "600000.SH"]
            assert quote_update.last_price > 0
            
            count += 1
            if count >= 3:  # 接收3条后退出
                break
        
        assert count >= 3
    
    def test_unsubscribe_quote(self, grpc_service, grpc_context):
        """测试取消订阅"""
        # 先创建订阅
        subscribe_request = data_pb2.SubscriptionRequest(
            symbols=["000001.SZ"],
            adjust_type="none",
            subscription_type=data_pb2.SUBSCRIPTION_QUOTE
        )
        
        response_stream = grpc_service.SubscribeQuote(subscribe_request, grpc_context)
        
        # 获取第一条数据以确保订阅建立
        quote_update = next(iter(response_stream))
        assert quote_update is not None
        
        # 注意：实际的subscription_id需要从订阅管理器获取
        # 这里为了测试简化，直接使用mock
        from app.dependencies import get_subscription_manager
        
        settings = get_settings()
        manager = get_subscription_manager(settings)
        subscriptions = manager.list_subscriptions()
        
        if subscriptions:
            subscription_id = subscriptions[0]["subscription_id"]
            
            # 取消订阅
            unsubscribe_request = data_pb2.UnsubscribeRequest(
                subscription_id=subscription_id
            )
            
            response = grpc_service.UnsubscribeQuote(unsubscribe_request, grpc_context)
            
            assert response.success is True
            assert "取消" in response.message
    
    def test_get_subscription_info(self, grpc_service, grpc_context):
        """测试获取订阅信息"""
        from app.dependencies import get_subscription_manager
        
        settings = get_settings()
        manager = get_subscription_manager(settings)
        
        # 创建一个订阅
        subscription_id = manager.subscribe_quote(
            symbols=["000001.SZ"],
            adjust_type="none"
        )
        
        # 获取订阅信息
        request = data_pb2.SubscriptionInfoRequest(
            subscription_id=subscription_id
        )
        
        response = grpc_service.GetSubscriptionInfo(request, grpc_context)
        
        assert response.subscription_id == subscription_id
        assert len(response.symbols) > 0
        assert response.adjust_type == "none"
        assert response.active is True
        
        # 清理
        manager.unsubscribe(subscription_id)
    
    def test_get_nonexistent_subscription_info(self, grpc_service, grpc_context):
        """测试获取不存在的订阅信息"""
        request = data_pb2.SubscriptionInfoRequest(
            subscription_id="nonexistent_id"
        )
        
        response = grpc_service.GetSubscriptionInfo(request, grpc_context)
        
        # 应该设置NOT_FOUND状态码
        grpc_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    
    def test_list_subscriptions(self, grpc_service, grpc_context):
        """测试列出所有订阅"""
        from app.dependencies import get_subscription_manager
        from google.protobuf import empty_pb2
        
        settings = get_settings()
        manager = get_subscription_manager(settings)
        
        # 创建几个订阅
        sub_ids = []
        for i in range(2):
            sub_id = manager.subscribe_quote(
                symbols=[f"00000{i}.SZ"],
                adjust_type="none"
            )
            sub_ids.append(sub_id)
        
        # 列出所有订阅
        request = empty_pb2.Empty()
        response = grpc_service.ListSubscriptions(request, grpc_context)
        
        assert len(response.subscriptions) >= 2
        
        # 清理
        for sub_id in sub_ids:
            manager.unsubscribe(sub_id)
    
    def test_subscribe_with_adjust_type(self, grpc_service, grpc_context):
        """测试带复权类型的订阅"""
        request = data_pb2.SubscriptionRequest(
            symbols=["000001.SZ"],
            adjust_type="front",
            subscription_type=data_pb2.SUBSCRIPTION_QUOTE
        )
        
        response_stream = grpc_service.SubscribeQuote(request, grpc_context)
        
        # 验证能够接收数据
        quote_update = next(iter(response_stream))
        assert quote_update is not None
        assert quote_update.stock_code == "000001.SZ"
    
    @pytest.mark.skipif(
        get_settings().xtquant.mode.value == "mock",
        reason="全推订阅在Mock模式下不可用"
    )
    def test_subscribe_whole_quote(self, grpc_service, grpc_context):
        """测试全推订阅（需要真实模式且启用whole_quote）"""
        from app.dependencies import get_subscription_manager
        
        settings = get_settings()
        
        # 检查是否启用全推
        if not settings.xtquant.data.whole_quote_enabled:
            pytest.skip("全推订阅未启用")
        
        request = data_pb2.WholeQuoteRequest(
            markets=["SH", "SZ"]
        )
        
        response_stream = grpc_service.SubscribeWholeQuote(request, grpc_context)
        
        # 接收几条数据
        count = 0
        for quote_update in response_stream:
            assert isinstance(quote_update, data_pb2.QuoteUpdate)
            assert len(quote_update.stock_code) > 0
            
            count += 1
            if count >= 5:
                break
        
        assert count >= 5
    
    def test_subscribe_with_empty_symbols(self, grpc_service, grpc_context):
        """测试空股票列表的订阅（应该返回INVALID_ARGUMENT）"""
        request = data_pb2.SubscriptionRequest(
            symbols=[],
            adjust_type="none",
            subscription_type=data_pb2.SUBSCRIPTION_QUOTE
        )
        
        # 调用订阅方法
        response_stream = grpc_service.SubscribeQuote(request, grpc_context)
        
        # 尝试获取第一条数据（应该立即返回空）
        count = 0
        for _ in response_stream:
            count += 1
            if count >= 1:
                break
        
        # 验证上下文被设置为INVALID_ARGUMENT
        grpc_context.set_code.assert_called()
        call_args = grpc_context.set_code.call_args_list
        # 检查是否有INVALID_ARGUMENT的调用
        assert any(
            call[0][0] == grpc.StatusCode.INVALID_ARGUMENT 
            for call in call_args
        ), f"Expected INVALID_ARGUMENT, but got {call_args}"


class TestSubscriptionManager:
    """订阅管理器单元测试"""
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        from app.services.subscription_manager import SubscriptionManager
        
        settings = get_settings()
        manager = SubscriptionManager(settings)
        
        assert manager is not None
        assert manager.max_queue_size == settings.xtquant.data.max_queue_size
        assert manager.max_subscriptions == settings.xtquant.data.max_subscriptions
    
    def test_subscribe_and_unsubscribe(self):
        """测试订阅和取消订阅"""
        from app.services.subscription_manager import SubscriptionManager
        
        settings = get_settings()
        manager = SubscriptionManager(settings)
        
        # 创建订阅
        sub_id = manager.subscribe_quote(
            symbols=["000001.SZ"],
            adjust_type="none"
        )
        
        assert sub_id is not None
        assert sub_id.startswith("sub_")
        
        # 验证订阅存在
        info = manager.get_subscription_info(sub_id)
        assert info is not None
        assert info["subscription_id"] == sub_id
        
        # 取消订阅
        result = manager.unsubscribe(sub_id)
        assert result is True
        
        # 验证订阅已删除
        info = manager.get_subscription_info(sub_id)
        assert info is None
    
    def test_multiple_subscriptions(self):
        """测试多个订阅"""
        from app.services.subscription_manager import SubscriptionManager
        
        settings = get_settings()
        manager = SubscriptionManager(settings)
        
        # 创建多个订阅
        sub_ids = []
        for i in range(5):
            sub_id = manager.subscribe_quote(
                symbols=[f"00000{i}.SZ"],
                adjust_type="none"
            )
            sub_ids.append(sub_id)
        
        # 验证所有订阅
        all_subs = manager.list_subscriptions()
        assert len(all_subs) >= 5
        
        # 清理
        for sub_id in sub_ids:
            manager.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_stream_quotes_mock(self):
        """测试行情流（Mock模式）"""
        from app.services.subscription_manager import SubscriptionManager
        
        settings = get_settings()
        manager = SubscriptionManager(settings)
        
        # 创建订阅
        sub_id = manager.subscribe_quote(
            symbols=["000001.SZ"],
            adjust_type="none"
        )
        
        # 流式接收数据
        count = 0
        async for quote_data in manager.stream_quotes(sub_id):
            assert "stock_code" in quote_data
            assert quote_data["stock_code"] == "000001.SZ"
            
            count += 1
            if count >= 3:
                break
        
        assert count >= 3
        
        # 清理
        manager.unsubscribe(sub_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
