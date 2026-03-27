import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_TYPE_UNSPECIFIED: _ClassVar[AccountType]
    ACCOUNT_TYPE_FUTURE: _ClassVar[AccountType]
    ACCOUNT_TYPE_SECURITY: _ClassVar[AccountType]
    ACCOUNT_TYPE_CREDIT: _ClassVar[AccountType]
    ACCOUNT_TYPE_FUTURE_OPTION: _ClassVar[AccountType]
    ACCOUNT_TYPE_STOCK_OPTION: _ClassVar[AccountType]

class OrderSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_SIDE_UNSPECIFIED: _ClassVar[OrderSide]
    ORDER_SIDE_BUY: _ClassVar[OrderSide]
    ORDER_SIDE_SELL: _ClassVar[OrderSide]

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_TYPE_UNSPECIFIED: _ClassVar[OrderType]
    ORDER_TYPE_MARKET: _ClassVar[OrderType]
    ORDER_TYPE_LIMIT: _ClassVar[OrderType]
    ORDER_TYPE_STOP: _ClassVar[OrderType]
    ORDER_TYPE_STOP_LIMIT: _ClassVar[OrderType]

class OrderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_STATUS_UNSPECIFIED: _ClassVar[OrderStatus]
    ORDER_STATUS_PENDING: _ClassVar[OrderStatus]
    ORDER_STATUS_SUBMITTED: _ClassVar[OrderStatus]
    ORDER_STATUS_PARTIAL_FILLED: _ClassVar[OrderStatus]
    ORDER_STATUS_FILLED: _ClassVar[OrderStatus]
    ORDER_STATUS_CANCELLED: _ClassVar[OrderStatus]
    ORDER_STATUS_REJECTED: _ClassVar[OrderStatus]
ACCOUNT_TYPE_UNSPECIFIED: AccountType
ACCOUNT_TYPE_FUTURE: AccountType
ACCOUNT_TYPE_SECURITY: AccountType
ACCOUNT_TYPE_CREDIT: AccountType
ACCOUNT_TYPE_FUTURE_OPTION: AccountType
ACCOUNT_TYPE_STOCK_OPTION: AccountType
ORDER_SIDE_UNSPECIFIED: OrderSide
ORDER_SIDE_BUY: OrderSide
ORDER_SIDE_SELL: OrderSide
ORDER_TYPE_UNSPECIFIED: OrderType
ORDER_TYPE_MARKET: OrderType
ORDER_TYPE_LIMIT: OrderType
ORDER_TYPE_STOP: OrderType
ORDER_TYPE_STOP_LIMIT: OrderType
ORDER_STATUS_UNSPECIFIED: OrderStatus
ORDER_STATUS_PENDING: OrderStatus
ORDER_STATUS_SUBMITTED: OrderStatus
ORDER_STATUS_PARTIAL_FILLED: OrderStatus
ORDER_STATUS_FILLED: OrderStatus
ORDER_STATUS_CANCELLED: OrderStatus
ORDER_STATUS_REJECTED: OrderStatus

class ConnectRequest(_message.Message):
    __slots__ = ("account_id", "password", "client_id")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    password: str
    client_id: int
    def __init__(self, account_id: _Optional[str] = ..., password: _Optional[str] = ..., client_id: _Optional[int] = ...) -> None: ...

class AccountInfo(_message.Message):
    __slots__ = ("account_id", "account_type", "account_name", "status", "balance", "available_balance", "frozen_balance", "market_value", "total_asset")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_BALANCE_FIELD_NUMBER: _ClassVar[int]
    FROZEN_BALANCE_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ASSET_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    account_type: AccountType
    account_name: str
    status: str
    balance: float
    available_balance: float
    frozen_balance: float
    market_value: float
    total_asset: float
    def __init__(self, account_id: _Optional[str] = ..., account_type: _Optional[_Union[AccountType, str]] = ..., account_name: _Optional[str] = ..., status: _Optional[str] = ..., balance: _Optional[float] = ..., available_balance: _Optional[float] = ..., frozen_balance: _Optional[float] = ..., market_value: _Optional[float] = ..., total_asset: _Optional[float] = ...) -> None: ...

class ConnectResponse(_message.Message):
    __slots__ = ("success", "message", "session_id", "account_info", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_INFO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    session_id: str
    account_info: AccountInfo
    status: _common_pb2.Status
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., session_id: _Optional[str] = ..., account_info: _Optional[_Union[AccountInfo, _Mapping]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class DisconnectRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class DisconnectResponse(_message.Message):
    __slots__ = ("success", "message", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    status: _common_pb2.Status
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class PositionRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class PositionInfo(_message.Message):
    __slots__ = ("stock_code", "stock_name", "volume", "available_volume", "frozen_volume", "cost_price", "market_price", "market_value", "profit_loss", "profit_loss_ratio")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    STOCK_NAME_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_VOLUME_FIELD_NUMBER: _ClassVar[int]
    FROZEN_VOLUME_FIELD_NUMBER: _ClassVar[int]
    COST_PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_PRICE_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_FIELD_NUMBER: _ClassVar[int]
    PROFIT_LOSS_FIELD_NUMBER: _ClassVar[int]
    PROFIT_LOSS_RATIO_FIELD_NUMBER: _ClassVar[int]
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
    def __init__(self, stock_code: _Optional[str] = ..., stock_name: _Optional[str] = ..., volume: _Optional[int] = ..., available_volume: _Optional[int] = ..., frozen_volume: _Optional[int] = ..., cost_price: _Optional[float] = ..., market_price: _Optional[float] = ..., market_value: _Optional[float] = ..., profit_loss: _Optional[float] = ..., profit_loss_ratio: _Optional[float] = ...) -> None: ...

class PositionListResponse(_message.Message):
    __slots__ = ("positions", "status")
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedCompositeFieldContainer[PositionInfo]
    status: _common_pb2.Status
    def __init__(self, positions: _Optional[_Iterable[_Union[PositionInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class OrderRequest(_message.Message):
    __slots__ = ("session_id", "stock_code", "side", "order_type", "volume", "price", "strategy_name")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    stock_code: str
    side: OrderSide
    order_type: OrderType
    volume: int
    price: float
    strategy_name: str
    def __init__(self, session_id: _Optional[str] = ..., stock_code: _Optional[str] = ..., side: _Optional[_Union[OrderSide, str]] = ..., order_type: _Optional[_Union[OrderType, str]] = ..., volume: _Optional[int] = ..., price: _Optional[float] = ..., strategy_name: _Optional[str] = ...) -> None: ...

class OrderInfo(_message.Message):
    __slots__ = ("order_id", "stock_code", "side", "order_type", "volume", "price", "status", "submitted_time", "filled_volume", "filled_amount", "average_price")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_TIME_FIELD_NUMBER: _ClassVar[int]
    FILLED_VOLUME_FIELD_NUMBER: _ClassVar[int]
    FILLED_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    stock_code: str
    side: OrderSide
    order_type: OrderType
    volume: int
    price: float
    status: OrderStatus
    submitted_time: str
    filled_volume: int
    filled_amount: float
    average_price: float
    def __init__(self, order_id: _Optional[str] = ..., stock_code: _Optional[str] = ..., side: _Optional[_Union[OrderSide, str]] = ..., order_type: _Optional[_Union[OrderType, str]] = ..., volume: _Optional[int] = ..., price: _Optional[float] = ..., status: _Optional[_Union[OrderStatus, str]] = ..., submitted_time: _Optional[str] = ..., filled_volume: _Optional[int] = ..., filled_amount: _Optional[float] = ..., average_price: _Optional[float] = ...) -> None: ...

class OrderResponse(_message.Message):
    __slots__ = ("order", "status")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    order: OrderInfo
    status: _common_pb2.Status
    def __init__(self, order: _Optional[_Union[OrderInfo, _Mapping]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class CancelOrderRequest(_message.Message):
    __slots__ = ("session_id", "order_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    order_id: str
    def __init__(self, session_id: _Optional[str] = ..., order_id: _Optional[str] = ...) -> None: ...

class CancelOrderResponse(_message.Message):
    __slots__ = ("success", "message", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    status: _common_pb2.Status
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class OrderListRequest(_message.Message):
    __slots__ = ("session_id", "start_date", "end_date")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    start_date: str
    end_date: str
    def __init__(self, session_id: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class OrderListResponse(_message.Message):
    __slots__ = ("orders", "status")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[OrderInfo]
    status: _common_pb2.Status
    def __init__(self, orders: _Optional[_Iterable[_Union[OrderInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class TradeListRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class TradeInfo(_message.Message):
    __slots__ = ("trade_id", "order_id", "stock_code", "side", "volume", "price", "amount", "trade_time", "commission")
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TRADE_TIME_FIELD_NUMBER: _ClassVar[int]
    COMMISSION_FIELD_NUMBER: _ClassVar[int]
    trade_id: str
    order_id: str
    stock_code: str
    side: OrderSide
    volume: int
    price: float
    amount: float
    trade_time: str
    commission: float
    def __init__(self, trade_id: _Optional[str] = ..., order_id: _Optional[str] = ..., stock_code: _Optional[str] = ..., side: _Optional[_Union[OrderSide, str]] = ..., volume: _Optional[int] = ..., price: _Optional[float] = ..., amount: _Optional[float] = ..., trade_time: _Optional[str] = ..., commission: _Optional[float] = ...) -> None: ...

class TradeListResponse(_message.Message):
    __slots__ = ("trades", "status")
    TRADES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    trades: _containers.RepeatedCompositeFieldContainer[TradeInfo]
    status: _common_pb2.Status
    def __init__(self, trades: _Optional[_Iterable[_Union[TradeInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class AssetRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class AssetInfo(_message.Message):
    __slots__ = ("total_asset", "market_value", "cash", "frozen_cash", "available_cash", "profit_loss", "profit_loss_ratio")
    TOTAL_ASSET_FIELD_NUMBER: _ClassVar[int]
    MARKET_VALUE_FIELD_NUMBER: _ClassVar[int]
    CASH_FIELD_NUMBER: _ClassVar[int]
    FROZEN_CASH_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_CASH_FIELD_NUMBER: _ClassVar[int]
    PROFIT_LOSS_FIELD_NUMBER: _ClassVar[int]
    PROFIT_LOSS_RATIO_FIELD_NUMBER: _ClassVar[int]
    total_asset: float
    market_value: float
    cash: float
    frozen_cash: float
    available_cash: float
    profit_loss: float
    profit_loss_ratio: float
    def __init__(self, total_asset: _Optional[float] = ..., market_value: _Optional[float] = ..., cash: _Optional[float] = ..., frozen_cash: _Optional[float] = ..., available_cash: _Optional[float] = ..., profit_loss: _Optional[float] = ..., profit_loss_ratio: _Optional[float] = ...) -> None: ...

class AssetResponse(_message.Message):
    __slots__ = ("asset", "status")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    asset: AssetInfo
    status: _common_pb2.Status
    def __init__(self, asset: _Optional[_Union[AssetInfo, _Mapping]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class RiskInfoRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class RiskInfoResponse(_message.Message):
    __slots__ = ("position_ratio", "cash_ratio", "max_drawdown", "var_95", "var_99", "status")
    POSITION_RATIO_FIELD_NUMBER: _ClassVar[int]
    CASH_RATIO_FIELD_NUMBER: _ClassVar[int]
    MAX_DRAWDOWN_FIELD_NUMBER: _ClassVar[int]
    VAR_95_FIELD_NUMBER: _ClassVar[int]
    VAR_99_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    position_ratio: float
    cash_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    status: _common_pb2.Status
    def __init__(self, position_ratio: _Optional[float] = ..., cash_ratio: _Optional[float] = ..., max_drawdown: _Optional[float] = ..., var_95: _Optional[float] = ..., var_99: _Optional[float] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class StrategyListRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class StrategyInfo(_message.Message):
    __slots__ = ("strategy_name", "strategy_type", "status", "created_time", "last_update_time", "parameters")
    class ParametersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    STRATEGY_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    strategy_name: str
    strategy_type: str
    status: str
    created_time: str
    last_update_time: str
    parameters: _containers.ScalarMap[str, str]
    def __init__(self, strategy_name: _Optional[str] = ..., strategy_type: _Optional[str] = ..., status: _Optional[str] = ..., created_time: _Optional[str] = ..., last_update_time: _Optional[str] = ..., parameters: _Optional[_Mapping[str, str]] = ...) -> None: ...

class StrategyListResponse(_message.Message):
    __slots__ = ("strategies", "status")
    STRATEGIES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    strategies: _containers.RepeatedCompositeFieldContainer[StrategyInfo]
    status: _common_pb2.Status
    def __init__(self, strategies: _Optional[_Iterable[_Union[StrategyInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...
