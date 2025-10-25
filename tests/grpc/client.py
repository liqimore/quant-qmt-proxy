"""
gRPC 测试客户端封装

提供易用的 gRPC 测试客户端，简化测试代码
"""

import grpc
import logging
from typing import Optional, List
from generated import (
    common_pb2,
    data_pb2,
    data_pb2_grpc,
    trading_pb2,
    trading_pb2_grpc,
    health_pb2,
    health_pb2_grpc,
)


class GRPCTestClient:
    """
    gRPC 测试客户端
    
    封装了所有 gRPC 服务调用，提供统一的接口和错误处理
    """
    
    def __init__(self, host: str = 'localhost', port: int = 50051, timeout: int = 30):
        """
        初始化 gRPC 测试客户端
        
        Args:
            host: gRPC 服务器地址
            port: gRPC 服务器端口
            timeout: 默认超时时间（秒）
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.address = f'{host}:{port}'
        self.logger = logging.getLogger(__name__)
        
        # 创建 gRPC 通道
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
                ('grpc.keepalive_time_ms', 10000),
                ('grpc.keepalive_timeout_ms', 5000),
            ]
        )
        
        # 创建服务 stubs
        self.data_stub = data_pb2_grpc.DataServiceStub(self.channel)
        self.trading_stub = trading_pb2_grpc.TradingServiceStub(self.channel)
        self.health_stub = health_pb2_grpc.HealthStub(self.channel)
        
        self.logger.info(f"gRPC 客户端已连接: {self.address}")
    
    def close(self):
        """关闭 gRPC 通道"""
        self.channel.close()
        self.logger.info("gRPC 客户端已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
    
    # ==================== 健康检查服务 ====================
    
    def check_health(self, service: str = "") -> health_pb2.HealthCheckResponse:
        """
        检查服务健康状态
        
        Args:
            service: 服务名称（空字符串表示检查所有服务）
        
        Returns:
            HealthCheckResponse
        """
        request = health_pb2.HealthCheckRequest(service=service)
        return self.health_stub.Check(request, timeout=self.timeout)
    
    def watch_health(self, service: str = ""):
        """
        订阅服务健康状态（流式）
        
        Args:
            service: 服务名称
        
        Yields:
            HealthCheckResponse
        """
        request = health_pb2.HealthCheckRequest(service=service)
        for response in self.health_stub.Watch(request):
            yield response
    
    # ==================== 数据服务 ====================
    
    def get_market_data(
        self,
        stock_codes: List[str],
        start_date: str,
        end_date: str,
        period: str = "1d",
        fields: Optional[List[str]] = None,
        dividend_type: str = "none"
    ) -> data_pb2.MarketDataResponse:
        """
        获取市场数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (1m, 5m, 1d 等)
            fields: 字段列表
            dividend_type: 复权类型
        
        Returns:
            MarketDataResponse
        """
        request = data_pb2.MarketDataRequest(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period=period,
            fields=fields or [],
            dividend_type=dividend_type
        )
        return self.data_stub.GetMarketData(request, timeout=self.timeout)
    
    def get_sector_list(self) -> data_pb2.SectorListResponse:
        """
        获取板块列表
        
        Returns:
            SectorListResponse（包含板块信息，每个板块有 stock_list 字段）
        """
        from google.protobuf import empty_pb2
        request = empty_pb2.Empty()
        return self.data_stub.GetSectorList(request, timeout=self.timeout)
    
    def get_index_weight(
        self,
        index_code: str,
        date: Optional[str] = None
    ) -> data_pb2.IndexWeightResponse:
        """
        获取指数权重
        
        Args:
            index_code: 指数代码
            date: 日期 (YYYYMMDD)，None 表示最新
        
        Returns:
            IndexWeightResponse
        """
        request = data_pb2.IndexWeightRequest(
            index_code=index_code,
            date=date or ""
        )
        return self.data_stub.GetIndexWeight(request, timeout=self.timeout)
    
    def get_trading_calendar(self, year: int) -> data_pb2.TradingCalendarResponse:
        """
        获取交易日历
        
        Args:
            year: 年份
        
        Returns:
            TradingCalendarResponse
        """
        request = data_pb2.TradingCalendarRequest(year=year)
        return self.data_stub.GetTradingCalendar(request, timeout=self.timeout)
    
    def get_instrument_info(self, stock_code: str) -> data_pb2.InstrumentInfoResponse:
        """
        获取合约信息
        
        Args:
            stock_code: 股票代码
        
        Returns:
            InstrumentInfoResponse
        """
        request = data_pb2.InstrumentInfoRequest(stock_code=stock_code)
        return self.data_stub.GetInstrumentInfo(request, timeout=self.timeout)
    
    def get_financial_data(
        self,
        stock_codes: List[str],
        table_list: List[str],
        start_date: str,
        end_date: str
    ) -> data_pb2.FinancialDataResponse:
        """
        获取财务数据
        
        Args:
            stock_codes: 股票代码列表
            table_list: 财务报表列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            FinancialDataResponse
        """
        request = data_pb2.FinancialDataRequest(
            stock_codes=stock_codes,
            table_list=table_list,
            start_date=start_date,
            end_date=end_date
        )
        return self.data_stub.GetFinancialData(request, timeout=self.timeout)
    
    # ==================== 交易服务 ====================
    
    def connect(
        self,
        account_id: str,
        password: str,
        account_type: str = "SECURITY",
        client_id: Optional[str] = None
    ) -> trading_pb2.ConnectResponse:
        """
        连接交易账户
        
        Args:
            account_id: 账户ID
            password: 密码
            account_type: 账户类型
            client_id: 客户端ID
        
        Returns:
            ConnectResponse
        """
        request = trading_pb2.ConnectRequest(
            account_id=account_id,
            password=password,
            account_type=account_type,
            client_id=client_id or ""
        )
        return self.trading_stub.Connect(request, timeout=self.timeout)
    
    def disconnect(self, session_id: str) -> trading_pb2.DisconnectResponse:
        """
        断开账户连接
        
        Args:
            session_id: 会话ID
        
        Returns:
            DisconnectResponse
        """
        request = trading_pb2.DisconnectRequest(session_id=session_id)
        return self.trading_stub.Disconnect(request, timeout=self.timeout)
    
    def get_account_info(self, session_id: str) -> trading_pb2.ConnectResponse:
        """
        获取账户信息
        
        Args:
            session_id: 会话ID
        
        Returns:
            ConnectResponse（包含账户信息）
        """
        request = trading_pb2.DisconnectRequest(session_id=session_id)
        return self.trading_stub.GetAccountInfo(request, timeout=self.timeout)
    
    def get_positions(self, session_id: str) -> trading_pb2.PositionListResponse:
        """
        查询持仓
        
        Args:
            session_id: 会话ID
        
        Returns:
            PositionListResponse
        """
        request = trading_pb2.PositionRequest(session_id=session_id)
        return self.trading_stub.GetPositions(request, timeout=self.timeout)
    
    def get_orders(
        self,
        session_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> trading_pb2.OrderListResponse:
        """
        查询订单
        
        Args:
            session_id: 会话ID
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            OrderListResponse
        """
        request = trading_pb2.OrderListRequest(
            session_id=session_id,
            start_date=start_date or "",
            end_date=end_date or ""
        )
        return self.trading_stub.GetOrders(request, timeout=self.timeout)
    
    def submit_order(
        self,
        session_id: str,
        stock_code: str,
        side: str,
        volume: int,
        price: Optional[float] = None,
        order_type: str = "LIMIT",
        strategy_name: Optional[str] = None
    ) -> trading_pb2.OrderResponse:
        """
        提交订单
        
        Args:
            session_id: 会话ID
            stock_code: 股票代码
            side: 买卖方向 (BUY/SELL)
            volume: 数量
            price: 价格
            order_type: 订单类型 (LIMIT/MARKET)
            strategy_name: 策略名称
        
        Returns:
            OrderResponse
        """
        # 转换枚举
        order_side = trading_pb2.ORDER_SIDE_BUY if side.upper() == "BUY" else trading_pb2.ORDER_SIDE_SELL
        ord_type = trading_pb2.ORDER_TYPE_LIMIT if order_type.upper() == "LIMIT" else trading_pb2.ORDER_TYPE_MARKET
        
        request = trading_pb2.OrderRequest(
            session_id=session_id,
            stock_code=stock_code,
            side=order_side,
            order_type=ord_type,
            volume=volume,
            price=price or 0.0,
            strategy_name=strategy_name or ""
        )
        return self.trading_stub.SubmitOrder(request, timeout=self.timeout)
    
    def cancel_order(
        self,
        session_id: str,
        order_id: str
    ) -> trading_pb2.CancelOrderResponse:
        """
        撤销订单
        
        Args:
            session_id: 会话ID
            order_id: 订单ID
        
        Returns:
            CancelOrderResponse
        """
        request = trading_pb2.CancelOrderRequest(
            session_id=session_id,
            order_id=order_id
        )
        return self.trading_stub.CancelOrder(request, timeout=self.timeout)
    
    # ==================== 辅助方法 ====================
    
    def assert_success(self, response, response_type: str = "gRPC"):
        """
        断言 gRPC 响应成功
        
        Args:
            response: gRPC 响应对象
            response_type: 响应类型（用于日志）
        
        Raises:
            AssertionError: 如果响应失败
        """
        if hasattr(response, 'status'):
            status = response.status
            assert status.code == 0, \
                f"{response_type} 请求失败: code={status.code}, message={status.message}"
        elif hasattr(response, 'success'):
            assert response.success, \
                f"{response_type} 请求失败: {getattr(response, 'message', 'Unknown error')}"
    
    def log_response(self, response, name: str = "gRPC"):
        """
        记录 gRPC 响应信息
        
        Args:
            response: gRPC 响应对象
            name: 请求名称
        """
        if hasattr(response, 'status'):
            status = response.status
            # 检查 status 是否有 code 属性（common.Status 类型）
            if hasattr(status, 'code'):
                if status.code == 0:
                    self.logger.info(f"{name} - 成功")
                else:
                    self.logger.error(f"{name} - 失败: code={status.code}, message={status.message}")
            else:
                # health check 的 status 是 int 枚举
                self.logger.info(f"{name} - status={status}")
        elif hasattr(response, 'success'):
            if response.success:
                self.logger.info(f"{name} - 成功")
            else:
                self.logger.error(f"{name} - 失败: {getattr(response, 'message', 'Unknown')}")
