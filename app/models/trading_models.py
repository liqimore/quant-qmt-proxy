"""
交易相关模型
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class AccountType(str, Enum):
    """账户类型"""
    FUTURE = "FUTURE"
    SECURITY = "SECURITY"
    CREDIT = "CREDIT"
    FUTURE_OPTION = "FUTURE_OPTION"
    STOCK_OPTION = "STOCK_OPTION"
    HUGANGTONG = "HUGANGTONG"
    INCOME_SWAP = "INCOME_SWAP"
    NEW3BOARD = "NEW3BOARD"
    SHENGANGTONG = "SHENGANGTONG"


class OrderSide(str, Enum):
    """订单方向"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """订单类型"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class AccountInfo(BaseModel):
    """账户信息"""
    account_id: str
    account_type: AccountType
    account_name: str
    status: str
    balance: float
    available_balance: float
    frozen_balance: float
    market_value: float
    total_asset: float


class PositionInfo(BaseModel):
    """持仓信息"""
    stock_code: str
    stock_name: str
    volume: int
    available_volume: int
    frozen_volume: int
    cost_price: float
    market_price: float
    market_value: float
    profit_loss: float
    profit_loss_ratio: float


class OrderRequest(BaseModel):
    """下单请求"""
    stock_code: str = Field(..., description="股票代码")
    side: OrderSide = Field(..., description="买卖方向")
    order_type: OrderType = Field(OrderType.LIMIT, description="订单类型")
    volume: int = Field(..., description="数量")
    price: Optional[float] = Field(None, description="价格")
    strategy_name: Optional[str] = Field(None, description="策略名称")
    
    @field_validator('volume')
    def validate_volume(cls, v):
        if v <= 0:
            raise ValueError('数量必须大于0')
        return v
    
    @field_validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('价格必须大于0')
        return v


class OrderResponse(BaseModel):
    """订单响应"""
    order_id: str
    stock_code: str
    side: str
    order_type: str
    volume: int
    price: Optional[float]
    status: str
    submitted_time: datetime
    filled_volume: int = 0
    filled_amount: float = 0.0
    average_price: Optional[float] = None


class CancelOrderRequest(BaseModel):
    """撤单请求"""
    order_id: str = Field(..., description="订单ID")


class TradeInfo(BaseModel):
    """成交信息"""
    trade_id: str
    order_id: str
    stock_code: str
    side: str
    volume: int
    price: float
    amount: float
    trade_time: datetime
    commission: float


class AssetInfo(BaseModel):
    """资产信息"""
    total_asset: float
    market_value: float
    cash: float
    frozen_cash: float
    available_cash: float
    profit_loss: float
    profit_loss_ratio: float


class RiskInfo(BaseModel):
    """风险信息"""
    position_ratio: float
    cash_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float


class StrategyInfo(BaseModel):
    """策略信息"""
    strategy_name: str
    strategy_type: str
    status: str
    created_time: datetime
    last_update_time: datetime
    parameters: Dict[str, Any]


class ConnectRequest(BaseModel):
    """连接请求"""
    account_id: str = Field(..., description="账户ID")
    password: Optional[str] = Field(None, description="密码")
    client_id: Optional[int] = Field(None, description="客户端ID")


class ConnectResponse(BaseModel):
    """连接响应"""
    success: bool
    message: str
    session_id: Optional[str] = None
    account_info: Optional[AccountInfo] = None
