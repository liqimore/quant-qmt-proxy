"""
交易服务层
"""
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import xtquant.xttrader as xttrader
    from xtquant import xtconstant
    XTQUANT_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入xtquant模块: {e}")
    XTQUANT_AVAILABLE = False
    # 创建模拟模块以避免导入错误
    class MockModule:
        def __getattr__(self, name):
            def mock_function(*args, **kwargs):
                raise NotImplementedError(f"xtquant模块未正确安装，无法调用 {name}")
            return mock_function
    
    xttrader = MockModule()
    xtconstant = MockModule()

from app.models.trading_models import (
    AccountInfo, PositionInfo, OrderRequest, OrderResponse,
    CancelOrderRequest, TradeInfo, AssetInfo, RiskInfo,
    StrategyInfo, ConnectRequest, ConnectResponse,
    AccountType, OrderSide, OrderType, OrderStatus
)
from app.utils.exceptions import TradingServiceException
from app.utils.helpers import validate_stock_code
from app.config import Settings, XTQuantMode


class TradingService:
    """交易服务类"""
    
    def __init__(self, settings: Settings):
        """初始化交易服务"""
        self.settings = settings
        self._initialized = False
        self._connected_accounts = {}
        self._orders = {}
        self._trades = {}
        self._order_counter = 1000
        self._try_initialize()
    
    def _try_initialize(self):
        """尝试初始化xttrader"""
        if not XTQUANT_AVAILABLE:
            print("xtquant模块不可用，使用模拟交易")
            self._initialized = False
            return
        
        if self.settings.xtquant.mode == XTQuantMode.MOCK:
            print("使用模拟交易模式")
            self._initialized = False
            return
        
        try:
            # 初始化xttrader
            # xttrader.connect()
            self._initialized = True
            print(f"xttrader初始化成功，模式: {self.settings.xtquant.mode.value}")
        except Exception as e:
            print(f"xttrader初始化失败: {e}")
            self._initialized = False
    
    def _should_use_real_trading(self) -> bool:
        """
        判断是否使用真实交易
        只有在 prod 模式且配置允许时才允许真实交易
        """
        return (
            XTQUANT_AVAILABLE and 
            self._initialized and 
            self.settings.xtquant.mode == XTQuantMode.PROD and
            self.settings.xtquant.trading.allow_real_trading
        )
    
    def _should_use_real_data(self) -> bool:
        """
        判断是否连接xtquant获取真实数据（但不一定允许交易）
        dev 和 prod 模式都连接 xtquant
        """
        return (
            XTQUANT_AVAILABLE and 
            self._initialized and 
            self.settings.xtquant.mode in [XTQuantMode.DEV, XTQuantMode.PROD]
        )
    
    def connect_account(self, request: ConnectRequest) -> ConnectResponse:
        """连接交易账户"""
        try:
            # 调用xttrader连接账户
            # account = xttrader.connect(request.account_id, request.password, request.client_id)
            
            # 模拟连接成功
            account_info = AccountInfo(
                account_id=request.account_id,
                account_type=AccountType.SECURITY,
                account_name=f"账户{request.account_id}",
                status="CONNECTED",
                balance=1000000.0,
                available_balance=950000.0,
                frozen_balance=50000.0,
                market_value=800000.0,
                total_asset=1800000.0
            )
            
            session_id = f"session_{request.account_id}_{datetime.now().timestamp()}"
            self._connected_accounts[session_id] = {
                "account_info": account_info,
                "connected_time": datetime.now()
            }
            
            return ConnectResponse(
                success=True,
                message="账户连接成功",
                session_id=session_id,
                account_info=account_info
            )
            
        except Exception as e:
            return ConnectResponse(
                success=False,
                message=f"账户连接失败: {str(e)}"
            )
    
    def disconnect_account(self, session_id: str) -> bool:
        """断开交易账户"""
        try:
            if session_id in self._connected_accounts:
                del self._connected_accounts[session_id]
                return True
            return False
        except Exception as e:
            raise TradingServiceException(f"断开账户失败: {str(e)}")
    
    def get_account_info(self, session_id: str) -> AccountInfo:
        """获取账户信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        return self._connected_accounts[session_id]["account_info"]
    
    def get_positions(self, session_id: str) -> List[PositionInfo]:
        """获取持仓信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 调用xttrader获取持仓
            # positions = xttrader.query_stock_positions(session_id)
            
            # 模拟持仓数据
            mock_positions = [
                PositionInfo(
                    stock_code="000001.SZ",
                    stock_name="平安银行",
                    volume=10000,
                    available_volume=10000,
                    frozen_volume=0,
                    cost_price=12.50,
                    market_price=13.20,
                    market_value=132000.0,
                    profit_loss=7000.0,
                    profit_loss_ratio=0.056
                ),
                PositionInfo(
                    stock_code="000002.SZ",
                    stock_name="万科A",
                    volume=5000,
                    available_volume=5000,
                    frozen_volume=0,
                    cost_price=18.80,
                    market_price=19.50,
                    market_value=97500.0,
                    profit_loss=3500.0,
                    profit_loss_ratio=0.037
                )
            ]
            
            return mock_positions
            
        except Exception as e:
            raise TradingServiceException(f"获取持仓信息失败: {str(e)}")
    
    def submit_order(self, session_id: str, request: OrderRequest) -> OrderResponse:
        """提交订单"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if not validate_stock_code(request.stock_code):
                raise TradingServiceException(f"无效的股票代码: {request.stock_code}")
            
            # 🔒 关键拦截点：检查是否允许真实交易
            if not self._should_use_real_trading():
                print(f"⚠️  当前模式[{self.settings.xtquant.mode.value}]不允许真实交易，返回模拟订单")
                return self._get_mock_order_response(request)
            
            # ✅ 允许真实交易，调用xttrader提交订单
            print(f"📊 真实交易模式：提交订单 {request.stock_code} {request.side.value} {request.volume}股")
            
            order_id = xttrader.order_stock(
                session_id,
                request.stock_code,
                request.side.value,
                request.volume,
                request.price,
                request.order_type.value
            )
            
            order_response = OrderResponse(
                order_id=order_id,
                stock_code=request.stock_code,
                side=request.side.value,
                order_type=request.order_type.value,
                volume=request.volume,
                price=request.price,
                status=OrderStatus.SUBMITTED.value,
                submitted_time=datetime.now()
            )
            
            self._orders[order_id] = order_response
            
            return order_response
            
        except Exception as e:
            raise TradingServiceException(f"提交订单失败: {str(e)}")
    
    def _get_mock_order_response(self, request: OrderRequest) -> OrderResponse:
        """生成模拟订单响应"""
        order_id = f"mock_order_{self._order_counter}"
        self._order_counter += 1
        
        order_response = OrderResponse(
            order_id=order_id,
            stock_code=request.stock_code,
            side=request.side.value,
            order_type=request.order_type.value,
            volume=request.volume,
            price=request.price,
            status=OrderStatus.SUBMITTED.value,
            submitted_time=datetime.now()
        )
        
        self._orders[order_id] = order_response
        return order_response
    
    def cancel_order(self, session_id: str, request: CancelOrderRequest) -> bool:
        """撤销订单"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            if request.order_id not in self._orders:
                raise TradingServiceException("订单不存在")
            
            # 🔒 关键拦截点：检查是否允许真实交易
            if not self._should_use_real_trading():
                print(f"⚠️  当前模式[{self.settings.xtquant.mode.value}]不允许真实交易，返回模拟撤单结果")
                # 模拟撤单成功
                if request.order_id in self._orders:
                    self._orders[request.order_id].status = OrderStatus.CANCELLED.value
                    return True
                return False
            
            # ✅ 允许真实交易，调用xttrader撤销订单
            print(f"📊 真实交易模式：撤销订单 {request.order_id}")
            success = xttrader.cancel_order_stock(session_id, request.order_id)
            
            if success and request.order_id in self._orders:
                self._orders[request.order_id].status = OrderStatus.CANCELLED.value
            
            return success
            
        except Exception as e:
            raise TradingServiceException(f"撤销订单失败: {str(e)}")
    
    def get_orders(self, session_id: str) -> List[OrderResponse]:
        """获取订单列表"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 调用xttrader获取订单
            # orders = xttrader.query_stock_orders(session_id)
            
            # 返回模拟订单数据
            return list(self._orders.values())
            
        except Exception as e:
            raise TradingServiceException(f"获取订单列表失败: {str(e)}")
    
    def get_trades(self, session_id: str) -> List[TradeInfo]:
        """获取成交记录"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 调用xttrader获取成交记录
            # trades = xttrader.query_stock_trades(session_id)
            
            # 模拟成交数据
            mock_trades = [
                TradeInfo(
                    trade_id="trade_001",
                    order_id="order_1001",
                    stock_code="000001.SZ",
                    side="BUY",
                    volume=1000,
                    price=13.20,
                    amount=13200.0,
                    trade_time=datetime.now(),
                    commission=13.20
                )
            ]
            
            return mock_trades
            
        except Exception as e:
            raise TradingServiceException(f"获取成交记录失败: {str(e)}")
    
    def get_asset_info(self, session_id: str) -> AssetInfo:
        """获取资产信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 调用xttrader获取资产信息
            # asset = xttrader.query_stock_asset(session_id)
            
            # 模拟资产数据
            return AssetInfo(
                total_asset=1800000.0,
                market_value=800000.0,
                cash=950000.0,
                frozen_cash=50000.0,
                available_cash=900000.0,
                profit_loss=50000.0,
                profit_loss_ratio=0.028
            )
            
        except Exception as e:
            raise TradingServiceException(f"获取资产信息失败: {str(e)}")
    
    def get_risk_info(self, session_id: str) -> RiskInfo:
        """获取风险信息"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 这里可以添加风险计算逻辑
            return RiskInfo(
                position_ratio=0.44,  # 持仓比例
                cash_ratio=0.56,      # 现金比例
                max_drawdown=0.05,    # 最大回撤
                var_95=0.02,          # 95% VaR
                var_99=0.03           # 99% VaR
            )
            
        except Exception as e:
            raise TradingServiceException(f"获取风险信息失败: {str(e)}")
    
    def get_strategies(self, session_id: str) -> List[StrategyInfo]:
        """获取策略列表"""
        if session_id not in self._connected_accounts:
            raise TradingServiceException("账户未连接")
        
        try:
            # 模拟策略数据
            mock_strategies = [
                StrategyInfo(
                    strategy_name="MA策略",
                    strategy_type="TREND_FOLLOWING",
                    status="RUNNING",
                    created_time=datetime.now(),
                    last_update_time=datetime.now(),
                    parameters={"period": 20, "threshold": 0.02}
                ),
                StrategyInfo(
                    strategy_name="均值回归策略",
                    strategy_type="MEAN_REVERSION",
                    status="STOPPED",
                    created_time=datetime.now(),
                    last_update_time=datetime.now(),
                    parameters={"lookback": 10, "entry_threshold": 0.05}
                )
            ]
            
            return mock_strategies
            
        except Exception as e:
            raise TradingServiceException(f"获取策略列表失败: {str(e)}")
    
    def is_connected(self, session_id: str) -> bool:
        """检查账户是否连接"""
        return session_id in self._connected_accounts
