"""
gRPC 客户端示例
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import grpc
from generated import data_pb2, data_pb2_grpc, trading_pb2, trading_pb2_grpc, common_pb2, health_pb2, health_pb2_grpc
from google.protobuf import empty_pb2


class QMTGrpcClient:
    """QMT gRPC 客户端"""
    
    def __init__(self, host: str = 'localhost', port: int = 50051):
        """
        初始化客户端
        
        Args:
            host: gRPC 服务器地址
            port: gRPC 服务器端口
        """
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        
        # 创建 stub
        self.data_stub = data_pb2_grpc.DataServiceStub(self.channel)
        self.trading_stub = trading_pb2_grpc.TradingServiceStub(self.channel)
        self.health_stub = health_pb2_grpc.HealthStub(self.channel)
    
    # ==================== 健康检查 ====================
    
    def check_health(self, service: str = ""):
        """健康检查"""
        request = health_pb2.HealthCheckRequest(service=service)
        response = self.health_stub.Check(request)
        return response
    
    # ==================== 数据服务 ====================
    
    def get_market_data(
        self, 
        stock_codes: list, 
        start_date: str, 
        end_date: str,
        period: int = common_pb2.PERIOD_TYPE_1D,
        fields: list = None,
        adjust_type: str = "none"
    ):
        """获取市场数据"""
        request = data_pb2.MarketDataRequest(
            stock_codes=stock_codes,
            start_date=start_date,
            end_date=end_date,
            period=period,
            fields=fields or ['open', 'high', 'low', 'close', 'volume'],
            adjust_type=adjust_type
        )
        
        response = self.data_stub.GetMarketData(request)
        return response
    
    def get_financial_data(
        self,
        stock_codes: list,
        table_list: list,
        start_date: str = "",
        end_date: str = ""
    ):
        """获取财务数据"""
        request = data_pb2.FinancialDataRequest(
            stock_codes=stock_codes,
            table_list=table_list,
            start_date=start_date,
            end_date=end_date
        )
        
        response = self.data_stub.GetFinancialData(request)
        return response
    
    def get_sector_list(self):
        """获取板块列表"""
        request = empty_pb2.Empty()
        response = self.data_stub.GetSectorList(request)
        return response
    
    def get_index_weight(self, index_code: str, date: str = ""):
        """获取指数权重"""
        request = data_pb2.IndexWeightRequest(
            index_code=index_code,
            date=date
        )
        
        response = self.data_stub.GetIndexWeight(request)
        return response
    
    def get_trading_calendar(self, year: int):
        """获取交易日历"""
        request = data_pb2.TradingCalendarRequest(year=year)
        response = self.data_stub.GetTradingCalendar(request)
        return response
    
    def get_instrument_info(self, stock_code: str):
        """获取合约信息"""
        request = data_pb2.InstrumentInfoRequest(stock_code=stock_code)
        response = self.data_stub.GetInstrumentInfo(request)
        return response
    
    def get_etf_info(self, etf_code: str):
        """获取ETF信息"""
        request = data_pb2.ETFInfoRequest(etf_code=etf_code)
        response = self.data_stub.GetETFInfo(request)
        return response
    
    # ==================== 交易服务 ====================
    
    def connect(self, account_id: str, password: str = "", client_id: int = 0):
        """连接账户"""
        request = trading_pb2.ConnectRequest(
            account_id=account_id,
            password=password,
            client_id=client_id
        )
        
        response = self.trading_stub.Connect(request)
        return response
    
    def disconnect(self, session_id: str):
        """断开账户"""
        request = trading_pb2.DisconnectRequest(session_id=session_id)
        response = self.trading_stub.Disconnect(request)
        return response
    
    def get_account_info(self, session_id: str):
        """获取账户信息"""
        request = trading_pb2.DisconnectRequest(session_id=session_id)
        response = self.trading_stub.GetAccountInfo(request)
        return response
    
    def get_positions(self, session_id: str):
        """获取持仓列表"""
        request = trading_pb2.PositionRequest(session_id=session_id)
        response = self.trading_stub.GetPositions(request)
        return response
    
    def submit_order(
        self,
        session_id: str,
        stock_code: str,
        side: int,
        volume: int,
        price: float,
        order_type: int = trading_pb2.ORDER_TYPE_LIMIT,
        strategy_name: str = ""
    ):
        """提交订单"""
        request = trading_pb2.OrderRequest(
            session_id=session_id,
            stock_code=stock_code,
            side=side,
            order_type=order_type,
            volume=volume,
            price=price,
            strategy_name=strategy_name
        )
        
        response = self.trading_stub.SubmitOrder(request)
        return response
    
    def cancel_order(self, session_id: str, order_id: str):
        """撤销订单"""
        request = trading_pb2.CancelOrderRequest(
            session_id=session_id,
            order_id=order_id
        )
        
        response = self.trading_stub.CancelOrder(request)
        return response
    
    def get_orders(self, session_id: str, start_date: str = "", end_date: str = ""):
        """获取订单列表"""
        request = trading_pb2.OrderListRequest(
            session_id=session_id,
            start_date=start_date,
            end_date=end_date
        )
        
        response = self.trading_stub.GetOrders(request)
        return response
    
    def get_trades(self, session_id: str):
        """获取成交记录"""
        request = trading_pb2.TradeListRequest(session_id=session_id)
        response = self.trading_stub.GetTrades(request)
        return response
    
    def get_asset(self, session_id: str):
        """获取资产信息"""
        request = trading_pb2.AssetRequest(session_id=session_id)
        response = self.trading_stub.GetAsset(request)
        return response
    
    def get_risk_info(self, session_id: str):
        """获取风险信息"""
        request = trading_pb2.RiskInfoRequest(session_id=session_id)
        response = self.trading_stub.GetRiskInfo(request)
        return response
    
    def get_strategies(self, session_id: str):
        """获取策略列表"""
        request = trading_pb2.StrategyListRequest(session_id=session_id)
        response = self.trading_stub.GetStrategies(request)
        return response
    
    def close(self):
        """关闭连接"""
        self.channel.close()


# 使用示例
if __name__ == '__main__':
    # 创建客户端
    client = QMTGrpcClient(host='localhost', port=50051)
    
    print("=" * 70)
    print("QMT gRPC 客户端示例")
    print("=" * 70)
    
    try:
        # 1. 健康检查
        print("\n【1. 健康检查】")
        health_response = client.check_health()
        print(f"服务状态: {health_response.status}")
        
        # 2. 获取市场数据
        print("\n【2. 获取市场数据】")
        market_response = client.get_market_data(
            stock_codes=['000001.SZ'],
            start_date='20240101',
            end_date='20240131'
        )
        print(f"状态码: {market_response.status.code}")
        print(f"状态信息: {market_response.status.message}")
        print(f"股票数量: {len(market_response.data)}")
        if market_response.data:
            first_stock = market_response.data[0]
            print(f"股票代码: {first_stock.stock_code}")
            print(f"K线数量: {len(first_stock.bars)}")
            if first_stock.bars:
                print(f"首条K线: 时间={first_stock.bars[0].time}, 收盘价={first_stock.bars[0].close}")
        
        # 3. 获取板块列表
        print("\n【3. 获取板块列表】")
        sector_response = client.get_sector_list()
        print(f"状态码: {sector_response.status.code}")
        print(f"板块数量: {len(sector_response.sectors)}")
        if sector_response.sectors:
            print(f"第一个板块: {sector_response.sectors[0].sector_name}")
        
        # 4. 连接交易账户
        print("\n【4. 连接交易账户】")
        connect_response = client.connect(
            account_id="mock_account_001",
            password="mock_password"
        )
        print(f"连接成功: {connect_response.success}")
        print(f"消息: {connect_response.message}")
        
        if connect_response.success:
            session_id = connect_response.session_id
            print(f"Session ID: {session_id}")
            
            # 5. 获取持仓
            print("\n【5. 获取持仓】")
            position_response = client.get_positions(session_id)
            print(f"状态码: {position_response.status.code}")
            print(f"持仓数量: {len(position_response.positions)}")
            for pos in position_response.positions:
                print(f"  - {pos.stock_name}({pos.stock_code}): {pos.volume}股, 成本价={pos.cost_price}")
            
            # 6. 获取资产
            print("\n【6. 获取资产】")
            asset_response = client.get_asset(session_id)
            print(f"状态码: {asset_response.status.code}")
            print(f"总资产: {asset_response.asset.total_asset}")
            print(f"可用现金: {asset_response.asset.available_cash}")
            print(f"持仓市值: {asset_response.asset.market_value}")
            
            # 7. 断开连接
            print("\n【7. 断开连接】")
            disconnect_response = client.disconnect(session_id)
            print(f"断开成功: {disconnect_response.success}")
        
    except grpc.RpcError as e:
        print(f"\n❌ gRPC 错误: {e.code()}")
        print(f"   详情: {e.details()}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭客户端
        client.close()
        print("\n" + "=" * 70)
        print("客户端已关闭")
        print("=" * 70)
