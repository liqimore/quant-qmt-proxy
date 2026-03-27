import common_pb2 as _common_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DownloadTaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOWNLOAD_PENDING: _ClassVar[DownloadTaskStatus]
    DOWNLOAD_RUNNING: _ClassVar[DownloadTaskStatus]
    DOWNLOAD_COMPLETED: _ClassVar[DownloadTaskStatus]
    DOWNLOAD_FAILED: _ClassVar[DownloadTaskStatus]

class SubscriptionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUBSCRIPTION_QUOTE: _ClassVar[SubscriptionType]
    SUBSCRIPTION_WHOLE_QUOTE: _ClassVar[SubscriptionType]
DOWNLOAD_PENDING: DownloadTaskStatus
DOWNLOAD_RUNNING: DownloadTaskStatus
DOWNLOAD_COMPLETED: DownloadTaskStatus
DOWNLOAD_FAILED: DownloadTaskStatus
SUBSCRIPTION_QUOTE: SubscriptionType
SUBSCRIPTION_WHOLE_QUOTE: SubscriptionType

class MarketDataRequest(_message.Message):
    __slots__ = ("stock_codes", "start_date", "end_date", "period", "fields", "adjust_type")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    ADJUST_TYPE_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_date: str
    end_date: str
    period: _common_pb2.PeriodType
    fields: _containers.RepeatedScalarFieldContainer[str]
    adjust_type: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., period: _Optional[_Union[_common_pb2.PeriodType, str]] = ..., fields: _Optional[_Iterable[str]] = ..., adjust_type: _Optional[str] = ...) -> None: ...

class KlineBar(_message.Message):
    __slots__ = ("time", "open", "high", "low", "close", "volume", "amount")
    TIME_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    def __init__(self, time: _Optional[str] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[int] = ..., amount: _Optional[float] = ...) -> None: ...

class MarketDataResponse(_message.Message):
    __slots__ = ("stock_code", "bars", "fields", "period", "start_date", "end_date", "status")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    BARS_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    bars: _containers.RepeatedCompositeFieldContainer[KlineBar]
    fields: _containers.RepeatedScalarFieldContainer[str]
    period: str
    start_date: str
    end_date: str
    status: _common_pb2.Status
    def __init__(self, stock_code: _Optional[str] = ..., bars: _Optional[_Iterable[_Union[KlineBar, _Mapping]]] = ..., fields: _Optional[_Iterable[str]] = ..., period: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class MarketDataBatchResponse(_message.Message):
    __slots__ = ("data", "status")
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[MarketDataResponse]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Iterable[_Union[MarketDataResponse, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class FinancialDataRequest(_message.Message):
    __slots__ = ("stock_codes", "table_list", "start_date", "end_date")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    TABLE_LIST_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    table_list: _containers.RepeatedScalarFieldContainer[str]
    start_date: str
    end_date: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., table_list: _Optional[_Iterable[str]] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class FinancialDataRow(_message.Message):
    __slots__ = ("fields",)
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    fields: _containers.ScalarMap[str, str]
    def __init__(self, fields: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FinancialDataResponse(_message.Message):
    __slots__ = ("stock_code", "table_name", "rows", "columns", "status")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    table_name: str
    rows: _containers.RepeatedCompositeFieldContainer[FinancialDataRow]
    columns: _containers.RepeatedScalarFieldContainer[str]
    status: _common_pb2.Status
    def __init__(self, stock_code: _Optional[str] = ..., table_name: _Optional[str] = ..., rows: _Optional[_Iterable[_Union[FinancialDataRow, _Mapping]]] = ..., columns: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class FinancialDataBatchResponse(_message.Message):
    __slots__ = ("data", "status")
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[FinancialDataResponse]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Iterable[_Union[FinancialDataResponse, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class SectorInfo(_message.Message):
    __slots__ = ("sector_name", "stock_list", "sector_type")
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    STOCK_LIST_FIELD_NUMBER: _ClassVar[int]
    SECTOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    sector_name: str
    stock_list: _containers.RepeatedScalarFieldContainer[str]
    sector_type: str
    def __init__(self, sector_name: _Optional[str] = ..., stock_list: _Optional[_Iterable[str]] = ..., sector_type: _Optional[str] = ...) -> None: ...

class SectorListResponse(_message.Message):
    __slots__ = ("sectors", "status")
    SECTORS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    sectors: _containers.RepeatedCompositeFieldContainer[SectorInfo]
    status: _common_pb2.Status
    def __init__(self, sectors: _Optional[_Iterable[_Union[SectorInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class IndexWeightRequest(_message.Message):
    __slots__ = ("index_code", "date")
    INDEX_CODE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    index_code: str
    date: str
    def __init__(self, index_code: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class ComponentWeight(_message.Message):
    __slots__ = ("stock_code", "weight", "market_cap")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAP_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    weight: float
    market_cap: float
    def __init__(self, stock_code: _Optional[str] = ..., weight: _Optional[float] = ..., market_cap: _Optional[float] = ...) -> None: ...

class IndexWeightResponse(_message.Message):
    __slots__ = ("index_code", "date", "weights", "status")
    INDEX_CODE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    WEIGHTS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    index_code: str
    date: str
    weights: _containers.RepeatedCompositeFieldContainer[ComponentWeight]
    status: _common_pb2.Status
    def __init__(self, index_code: _Optional[str] = ..., date: _Optional[str] = ..., weights: _Optional[_Iterable[_Union[ComponentWeight, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class TradingCalendarRequest(_message.Message):
    __slots__ = ("year",)
    YEAR_FIELD_NUMBER: _ClassVar[int]
    year: int
    def __init__(self, year: _Optional[int] = ...) -> None: ...

class TradingCalendarResponse(_message.Message):
    __slots__ = ("trading_dates", "holidays", "year", "status")
    TRADING_DATES_FIELD_NUMBER: _ClassVar[int]
    HOLIDAYS_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    trading_dates: _containers.RepeatedScalarFieldContainer[str]
    holidays: _containers.RepeatedScalarFieldContainer[str]
    year: int
    status: _common_pb2.Status
    def __init__(self, trading_dates: _Optional[_Iterable[str]] = ..., holidays: _Optional[_Iterable[str]] = ..., year: _Optional[int] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class InstrumentInfoRequest(_message.Message):
    __slots__ = ("stock_code",)
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    def __init__(self, stock_code: _Optional[str] = ...) -> None: ...

class InstrumentInfoResponse(_message.Message):
    __slots__ = ("instrument_code", "instrument_name", "market_type", "instrument_type", "list_date", "delist_date", "status")
    INSTRUMENT_CODE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    MARKET_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIST_DATE_FIELD_NUMBER: _ClassVar[int]
    DELIST_DATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    instrument_code: str
    instrument_name: str
    market_type: str
    instrument_type: str
    list_date: str
    delist_date: str
    status: _common_pb2.Status
    def __init__(self, instrument_code: _Optional[str] = ..., instrument_name: _Optional[str] = ..., market_type: _Optional[str] = ..., instrument_type: _Optional[str] = ..., list_date: _Optional[str] = ..., delist_date: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class ETFInfoRequest(_message.Message):
    __slots__ = ("etf_code",)
    ETF_CODE_FIELD_NUMBER: _ClassVar[int]
    etf_code: str
    def __init__(self, etf_code: _Optional[str] = ...) -> None: ...

class ETFInfoResponse(_message.Message):
    __slots__ = ("etf_code", "etf_name", "underlying_asset", "creation_unit", "redemption_unit", "status")
    ETF_CODE_FIELD_NUMBER: _ClassVar[int]
    ETF_NAME_FIELD_NUMBER: _ClassVar[int]
    UNDERLYING_ASSET_FIELD_NUMBER: _ClassVar[int]
    CREATION_UNIT_FIELD_NUMBER: _ClassVar[int]
    REDEMPTION_UNIT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    etf_code: str
    etf_name: str
    underlying_asset: str
    creation_unit: int
    redemption_unit: int
    status: _common_pb2.Status
    def __init__(self, etf_code: _Optional[str] = ..., etf_name: _Optional[str] = ..., underlying_asset: _Optional[str] = ..., creation_unit: _Optional[int] = ..., redemption_unit: _Optional[int] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class InstrumentTypeInfo(_message.Message):
    __slots__ = ("stock_code", "index", "stock", "fund", "etf", "bond", "option", "futures")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    FUND_FIELD_NUMBER: _ClassVar[int]
    ETF_FIELD_NUMBER: _ClassVar[int]
    BOND_FIELD_NUMBER: _ClassVar[int]
    OPTION_FIELD_NUMBER: _ClassVar[int]
    FUTURES_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    index: bool
    stock: bool
    fund: bool
    etf: bool
    bond: bool
    option: bool
    futures: bool
    def __init__(self, stock_code: _Optional[str] = ..., index: bool = ..., stock: bool = ..., fund: bool = ..., etf: bool = ..., bond: bool = ..., option: bool = ..., futures: bool = ...) -> None: ...

class InstrumentTypeRequest(_message.Message):
    __slots__ = ("stock_code",)
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    def __init__(self, stock_code: _Optional[str] = ...) -> None: ...

class InstrumentTypeResponse(_message.Message):
    __slots__ = ("data", "status")
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: InstrumentTypeInfo
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Union[InstrumentTypeInfo, _Mapping]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class HolidayInfoResponse(_message.Message):
    __slots__ = ("holidays", "status")
    HOLIDAYS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    holidays: _containers.RepeatedScalarFieldContainer[str]
    status: _common_pb2.Status
    def __init__(self, holidays: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class ConvertibleBondInfo(_message.Message):
    __slots__ = ("bond_code", "bond_name", "stock_code", "stock_name", "conversion_price", "conversion_value", "conversion_premium_rate", "current_price", "par_value", "list_date", "maturity_date", "conversion_begin_date", "conversion_end_date", "raw_data")
    class RawDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BOND_CODE_FIELD_NUMBER: _ClassVar[int]
    BOND_NAME_FIELD_NUMBER: _ClassVar[int]
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    STOCK_NAME_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_PRICE_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_VALUE_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_PREMIUM_RATE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    PAR_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_DATE_FIELD_NUMBER: _ClassVar[int]
    MATURITY_DATE_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_BEGIN_DATE_FIELD_NUMBER: _ClassVar[int]
    CONVERSION_END_DATE_FIELD_NUMBER: _ClassVar[int]
    RAW_DATA_FIELD_NUMBER: _ClassVar[int]
    bond_code: str
    bond_name: str
    stock_code: str
    stock_name: str
    conversion_price: float
    conversion_value: float
    conversion_premium_rate: float
    current_price: float
    par_value: float
    list_date: str
    maturity_date: str
    conversion_begin_date: str
    conversion_end_date: str
    raw_data: _containers.ScalarMap[str, str]
    def __init__(self, bond_code: _Optional[str] = ..., bond_name: _Optional[str] = ..., stock_code: _Optional[str] = ..., stock_name: _Optional[str] = ..., conversion_price: _Optional[float] = ..., conversion_value: _Optional[float] = ..., conversion_premium_rate: _Optional[float] = ..., current_price: _Optional[float] = ..., par_value: _Optional[float] = ..., list_date: _Optional[str] = ..., maturity_date: _Optional[str] = ..., conversion_begin_date: _Optional[str] = ..., conversion_end_date: _Optional[str] = ..., raw_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ConvertibleBondListResponse(_message.Message):
    __slots__ = ("bonds", "status")
    BONDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    bonds: _containers.RepeatedCompositeFieldContainer[ConvertibleBondInfo]
    status: _common_pb2.Status
    def __init__(self, bonds: _Optional[_Iterable[_Union[ConvertibleBondInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class IpoInfo(_message.Message):
    __slots__ = ("security_code", "code_name", "market", "act_issue_qty", "online_issue_qty", "online_sub_code", "online_sub_max_qty", "publish_price", "is_profit", "industry_pe", "after_pe", "subscribe_date", "lottery_date", "list_date", "raw_data")
    class RawDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SECURITY_CODE_FIELD_NUMBER: _ClassVar[int]
    CODE_NAME_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    ACT_ISSUE_QTY_FIELD_NUMBER: _ClassVar[int]
    ONLINE_ISSUE_QTY_FIELD_NUMBER: _ClassVar[int]
    ONLINE_SUB_CODE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_SUB_MAX_QTY_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_PRICE_FIELD_NUMBER: _ClassVar[int]
    IS_PROFIT_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_PE_FIELD_NUMBER: _ClassVar[int]
    AFTER_PE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBE_DATE_FIELD_NUMBER: _ClassVar[int]
    LOTTERY_DATE_FIELD_NUMBER: _ClassVar[int]
    LIST_DATE_FIELD_NUMBER: _ClassVar[int]
    RAW_DATA_FIELD_NUMBER: _ClassVar[int]
    security_code: str
    code_name: str
    market: str
    act_issue_qty: int
    online_issue_qty: int
    online_sub_code: str
    online_sub_max_qty: int
    publish_price: float
    is_profit: int
    industry_pe: float
    after_pe: float
    subscribe_date: str
    lottery_date: str
    list_date: str
    raw_data: _containers.ScalarMap[str, str]
    def __init__(self, security_code: _Optional[str] = ..., code_name: _Optional[str] = ..., market: _Optional[str] = ..., act_issue_qty: _Optional[int] = ..., online_issue_qty: _Optional[int] = ..., online_sub_code: _Optional[str] = ..., online_sub_max_qty: _Optional[int] = ..., publish_price: _Optional[float] = ..., is_profit: _Optional[int] = ..., industry_pe: _Optional[float] = ..., after_pe: _Optional[float] = ..., subscribe_date: _Optional[str] = ..., lottery_date: _Optional[str] = ..., list_date: _Optional[str] = ..., raw_data: _Optional[_Mapping[str, str]] = ...) -> None: ...

class IpoInfoListResponse(_message.Message):
    __slots__ = ("ipos", "status")
    IPOS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ipos: _containers.RepeatedCompositeFieldContainer[IpoInfo]
    status: _common_pb2.Status
    def __init__(self, ipos: _Optional[_Iterable[_Union[IpoInfo, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class PeriodListResponse(_message.Message):
    __slots__ = ("periods", "status")
    PERIODS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    periods: _containers.RepeatedScalarFieldContainer[str]
    status: _common_pb2.Status
    def __init__(self, periods: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class DataDirResponse(_message.Message):
    __slots__ = ("data_dir", "status")
    DATA_DIR_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data_dir: str
    status: _common_pb2.Status
    def __init__(self, data_dir: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class LocalDataRequest(_message.Message):
    __slots__ = ("stock_codes", "start_time", "end_time", "period")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_time: str
    end_time: str
    period: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., period: _Optional[str] = ...) -> None: ...

class LocalDataResponse(_message.Message):
    __slots__ = ("data", "status")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: KlineDataList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[KlineDataList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, KlineDataList]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Mapping[str, KlineDataList]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class KlineDataList(_message.Message):
    __slots__ = ("bars",)
    BARS_FIELD_NUMBER: _ClassVar[int]
    bars: _containers.RepeatedCompositeFieldContainer[KlineBar]
    def __init__(self, bars: _Optional[_Iterable[_Union[KlineBar, _Mapping]]] = ...) -> None: ...

class TickData(_message.Message):
    __slots__ = ("time", "last_price", "open", "high", "low", "last_close", "amount", "volume", "pvolume", "stock_status", "open_int", "last_settlement_price", "ask_price", "bid_price", "ask_vol", "bid_vol", "transaction_num")
    TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    LAST_CLOSE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PVOLUME_FIELD_NUMBER: _ClassVar[int]
    STOCK_STATUS_FIELD_NUMBER: _ClassVar[int]
    OPEN_INT_FIELD_NUMBER: _ClassVar[int]
    LAST_SETTLEMENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    ASK_VOL_FIELD_NUMBER: _ClassVar[int]
    BID_VOL_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_NUM_FIELD_NUMBER: _ClassVar[int]
    time: str
    last_price: float
    open: float
    high: float
    low: float
    last_close: float
    amount: float
    volume: int
    pvolume: int
    stock_status: int
    open_int: int
    last_settlement_price: float
    ask_price: _containers.RepeatedScalarFieldContainer[float]
    bid_price: _containers.RepeatedScalarFieldContainer[float]
    ask_vol: _containers.RepeatedScalarFieldContainer[int]
    bid_vol: _containers.RepeatedScalarFieldContainer[int]
    transaction_num: int
    def __init__(self, time: _Optional[str] = ..., last_price: _Optional[float] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., last_close: _Optional[float] = ..., amount: _Optional[float] = ..., volume: _Optional[int] = ..., pvolume: _Optional[int] = ..., stock_status: _Optional[int] = ..., open_int: _Optional[int] = ..., last_settlement_price: _Optional[float] = ..., ask_price: _Optional[_Iterable[float]] = ..., bid_price: _Optional[_Iterable[float]] = ..., ask_vol: _Optional[_Iterable[int]] = ..., bid_vol: _Optional[_Iterable[int]] = ..., transaction_num: _Optional[int] = ...) -> None: ...

class FullTickRequest(_message.Message):
    __slots__ = ("stock_codes", "start_time", "end_time")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_time: str
    end_time: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class FullTickResponse(_message.Message):
    __slots__ = ("data", "status")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TickDataList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TickDataList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, TickDataList]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Mapping[str, TickDataList]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class TickDataList(_message.Message):
    __slots__ = ("ticks",)
    TICKS_FIELD_NUMBER: _ClassVar[int]
    ticks: _containers.RepeatedCompositeFieldContainer[TickData]
    def __init__(self, ticks: _Optional[_Iterable[_Union[TickData, _Mapping]]] = ...) -> None: ...

class DividendFactor(_message.Message):
    __slots__ = ("time", "interest", "stock_bonus", "stock_gift", "allot_num", "allot_price", "gugai", "dr")
    TIME_FIELD_NUMBER: _ClassVar[int]
    INTEREST_FIELD_NUMBER: _ClassVar[int]
    STOCK_BONUS_FIELD_NUMBER: _ClassVar[int]
    STOCK_GIFT_FIELD_NUMBER: _ClassVar[int]
    ALLOT_NUM_FIELD_NUMBER: _ClassVar[int]
    ALLOT_PRICE_FIELD_NUMBER: _ClassVar[int]
    GUGAI_FIELD_NUMBER: _ClassVar[int]
    DR_FIELD_NUMBER: _ClassVar[int]
    time: str
    interest: float
    stock_bonus: float
    stock_gift: float
    allot_num: float
    allot_price: float
    gugai: int
    dr: float
    def __init__(self, time: _Optional[str] = ..., interest: _Optional[float] = ..., stock_bonus: _Optional[float] = ..., stock_gift: _Optional[float] = ..., allot_num: _Optional[float] = ..., allot_price: _Optional[float] = ..., gugai: _Optional[int] = ..., dr: _Optional[float] = ...) -> None: ...

class DividFactorsRequest(_message.Message):
    __slots__ = ("stock_code",)
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    def __init__(self, stock_code: _Optional[str] = ...) -> None: ...

class DividFactorsResponse(_message.Message):
    __slots__ = ("factors", "status")
    FACTORS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    factors: _containers.RepeatedCompositeFieldContainer[DividendFactor]
    status: _common_pb2.Status
    def __init__(self, factors: _Optional[_Iterable[_Union[DividendFactor, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class FullKlineRequest(_message.Message):
    __slots__ = ("stock_codes", "start_time", "end_time", "period")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_time: str
    end_time: str
    period: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., period: _Optional[str] = ...) -> None: ...

class FullKlineResponse(_message.Message):
    __slots__ = ("data", "status")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: KlineDataList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[KlineDataList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, KlineDataList]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Mapping[str, KlineDataList]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class DownloadHistoryDataRequest(_message.Message):
    __slots__ = ("stock_code", "period", "start_time", "end_time", "incrementally")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    INCREMENTALLY_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    period: str
    start_time: str
    end_time: str
    incrementally: bool
    def __init__(self, stock_code: _Optional[str] = ..., period: _Optional[str] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., incrementally: bool = ...) -> None: ...

class DownloadHistoryDataBatchRequest(_message.Message):
    __slots__ = ("stock_list", "period", "start_time", "end_time")
    STOCK_LIST_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    stock_list: _containers.RepeatedScalarFieldContainer[str]
    period: str
    start_time: str
    end_time: str
    def __init__(self, stock_list: _Optional[_Iterable[str]] = ..., period: _Optional[str] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class DownloadResponse(_message.Message):
    __slots__ = ("task_id", "status", "progress", "total", "finished", "message", "current_stock", "rpc_status")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STOCK_FIELD_NUMBER: _ClassVar[int]
    RPC_STATUS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    status: DownloadTaskStatus
    progress: float
    total: int
    finished: int
    message: str
    current_stock: str
    rpc_status: _common_pb2.Status
    def __init__(self, task_id: _Optional[str] = ..., status: _Optional[_Union[DownloadTaskStatus, str]] = ..., progress: _Optional[float] = ..., total: _Optional[int] = ..., finished: _Optional[int] = ..., message: _Optional[str] = ..., current_stock: _Optional[str] = ..., rpc_status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class DownloadFinancialDataRequest(_message.Message):
    __slots__ = ("stock_list", "table_list", "start_date", "end_date")
    STOCK_LIST_FIELD_NUMBER: _ClassVar[int]
    TABLE_LIST_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    stock_list: _containers.RepeatedScalarFieldContainer[str]
    table_list: _containers.RepeatedScalarFieldContainer[str]
    start_date: str
    end_date: str
    def __init__(self, stock_list: _Optional[_Iterable[str]] = ..., table_list: _Optional[_Iterable[str]] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class DownloadIndexWeightRequest(_message.Message):
    __slots__ = ("index_code",)
    INDEX_CODE_FIELD_NUMBER: _ClassVar[int]
    index_code: str
    def __init__(self, index_code: _Optional[str] = ...) -> None: ...

class DownloadHistoryContractsRequest(_message.Message):
    __slots__ = ("market",)
    MARKET_FIELD_NUMBER: _ClassVar[int]
    market: str
    def __init__(self, market: _Optional[str] = ...) -> None: ...

class CreateSectorFolderRequest(_message.Message):
    __slots__ = ("parent_node", "folder_name", "overwrite")
    PARENT_NODE_FIELD_NUMBER: _ClassVar[int]
    FOLDER_NAME_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    parent_node: str
    folder_name: str
    overwrite: bool
    def __init__(self, parent_node: _Optional[str] = ..., folder_name: _Optional[str] = ..., overwrite: bool = ...) -> None: ...

class CreateSectorFolderResponse(_message.Message):
    __slots__ = ("created_name", "status")
    CREATED_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    created_name: str
    status: _common_pb2.Status
    def __init__(self, created_name: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class CreateSectorRequest(_message.Message):
    __slots__ = ("parent_node", "sector_name", "overwrite")
    PARENT_NODE_FIELD_NUMBER: _ClassVar[int]
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    parent_node: str
    sector_name: str
    overwrite: bool
    def __init__(self, parent_node: _Optional[str] = ..., sector_name: _Optional[str] = ..., overwrite: bool = ...) -> None: ...

class CreateSectorResponse(_message.Message):
    __slots__ = ("created_name", "status")
    CREATED_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    created_name: str
    status: _common_pb2.Status
    def __init__(self, created_name: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class AddSectorRequest(_message.Message):
    __slots__ = ("sector_name", "stock_list")
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    STOCK_LIST_FIELD_NUMBER: _ClassVar[int]
    sector_name: str
    stock_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sector_name: _Optional[str] = ..., stock_list: _Optional[_Iterable[str]] = ...) -> None: ...

class AddSectorResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class RemoveStockFromSectorRequest(_message.Message):
    __slots__ = ("sector_name", "stock_list")
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    STOCK_LIST_FIELD_NUMBER: _ClassVar[int]
    sector_name: str
    stock_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sector_name: _Optional[str] = ..., stock_list: _Optional[_Iterable[str]] = ...) -> None: ...

class RemoveStockFromSectorResponse(_message.Message):
    __slots__ = ("success", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    status: _common_pb2.Status
    def __init__(self, success: bool = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class RemoveSectorRequest(_message.Message):
    __slots__ = ("sector_name",)
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    sector_name: str
    def __init__(self, sector_name: _Optional[str] = ...) -> None: ...

class RemoveSectorResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class ResetSectorRequest(_message.Message):
    __slots__ = ("sector_name", "stock_list")
    SECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    STOCK_LIST_FIELD_NUMBER: _ClassVar[int]
    sector_name: str
    stock_list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sector_name: _Optional[str] = ..., stock_list: _Optional[_Iterable[str]] = ...) -> None: ...

class ResetSectorResponse(_message.Message):
    __slots__ = ("success", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    status: _common_pb2.Status
    def __init__(self, success: bool = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class L2QuoteData(_message.Message):
    __slots__ = ("time", "last_price", "open", "high", "low", "amount", "volume", "pvolume", "open_int", "stock_status", "transaction_num", "last_close", "last_settlement_price", "settlement_price", "pe", "ask_price", "bid_price", "ask_vol", "bid_vol")
    TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    PVOLUME_FIELD_NUMBER: _ClassVar[int]
    OPEN_INT_FIELD_NUMBER: _ClassVar[int]
    STOCK_STATUS_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_NUM_FIELD_NUMBER: _ClassVar[int]
    LAST_CLOSE_FIELD_NUMBER: _ClassVar[int]
    LAST_SETTLEMENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_PRICE_FIELD_NUMBER: _ClassVar[int]
    PE_FIELD_NUMBER: _ClassVar[int]
    ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    ASK_VOL_FIELD_NUMBER: _ClassVar[int]
    BID_VOL_FIELD_NUMBER: _ClassVar[int]
    time: str
    last_price: float
    open: float
    high: float
    low: float
    amount: float
    volume: int
    pvolume: int
    open_int: int
    stock_status: int
    transaction_num: int
    last_close: float
    last_settlement_price: float
    settlement_price: float
    pe: float
    ask_price: _containers.RepeatedScalarFieldContainer[float]
    bid_price: _containers.RepeatedScalarFieldContainer[float]
    ask_vol: _containers.RepeatedScalarFieldContainer[int]
    bid_vol: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, time: _Optional[str] = ..., last_price: _Optional[float] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., amount: _Optional[float] = ..., volume: _Optional[int] = ..., pvolume: _Optional[int] = ..., open_int: _Optional[int] = ..., stock_status: _Optional[int] = ..., transaction_num: _Optional[int] = ..., last_close: _Optional[float] = ..., last_settlement_price: _Optional[float] = ..., settlement_price: _Optional[float] = ..., pe: _Optional[float] = ..., ask_price: _Optional[_Iterable[float]] = ..., bid_price: _Optional[_Iterable[float]] = ..., ask_vol: _Optional[_Iterable[int]] = ..., bid_vol: _Optional[_Iterable[int]] = ...) -> None: ...

class L2QuoteRequest(_message.Message):
    __slots__ = ("stock_codes", "start_time", "end_time")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_time: str
    end_time: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class L2QuoteResponse(_message.Message):
    __slots__ = ("data", "status")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: L2QuoteDataList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[L2QuoteDataList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, L2QuoteDataList]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Mapping[str, L2QuoteDataList]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class L2QuoteDataList(_message.Message):
    __slots__ = ("quotes",)
    QUOTES_FIELD_NUMBER: _ClassVar[int]
    quotes: _containers.RepeatedCompositeFieldContainer[L2QuoteData]
    def __init__(self, quotes: _Optional[_Iterable[_Union[L2QuoteData, _Mapping]]] = ...) -> None: ...

class L2OrderData(_message.Message):
    __slots__ = ("time", "price", "volume", "entrust_no", "entrust_type", "entrust_direction")
    TIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    ENTRUST_NO_FIELD_NUMBER: _ClassVar[int]
    ENTRUST_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENTRUST_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    time: str
    price: float
    volume: int
    entrust_no: int
    entrust_type: int
    entrust_direction: int
    def __init__(self, time: _Optional[str] = ..., price: _Optional[float] = ..., volume: _Optional[int] = ..., entrust_no: _Optional[int] = ..., entrust_type: _Optional[int] = ..., entrust_direction: _Optional[int] = ...) -> None: ...

class L2OrderRequest(_message.Message):
    __slots__ = ("stock_codes", "start_time", "end_time")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_time: str
    end_time: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class L2OrderResponse(_message.Message):
    __slots__ = ("data", "status")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: L2OrderDataList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[L2OrderDataList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, L2OrderDataList]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Mapping[str, L2OrderDataList]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class L2OrderDataList(_message.Message):
    __slots__ = ("orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[L2OrderData]
    def __init__(self, orders: _Optional[_Iterable[_Union[L2OrderData, _Mapping]]] = ...) -> None: ...

class L2TransactionData(_message.Message):
    __slots__ = ("time", "price", "volume", "amount", "trade_index", "buy_no", "sell_no", "trade_type", "trade_flag")
    TIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TRADE_INDEX_FIELD_NUMBER: _ClassVar[int]
    BUY_NO_FIELD_NUMBER: _ClassVar[int]
    SELL_NO_FIELD_NUMBER: _ClassVar[int]
    TRADE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRADE_FLAG_FIELD_NUMBER: _ClassVar[int]
    time: str
    price: float
    volume: int
    amount: float
    trade_index: int
    buy_no: int
    sell_no: int
    trade_type: int
    trade_flag: int
    def __init__(self, time: _Optional[str] = ..., price: _Optional[float] = ..., volume: _Optional[int] = ..., amount: _Optional[float] = ..., trade_index: _Optional[int] = ..., buy_no: _Optional[int] = ..., sell_no: _Optional[int] = ..., trade_type: _Optional[int] = ..., trade_flag: _Optional[int] = ...) -> None: ...

class L2TransactionRequest(_message.Message):
    __slots__ = ("stock_codes", "start_time", "end_time")
    STOCK_CODES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    stock_codes: _containers.RepeatedScalarFieldContainer[str]
    start_time: str
    end_time: str
    def __init__(self, stock_codes: _Optional[_Iterable[str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class L2TransactionResponse(_message.Message):
    __slots__ = ("data", "status")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: L2TransactionDataList
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[L2TransactionDataList, _Mapping]] = ...) -> None: ...
    DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    data: _containers.MessageMap[str, L2TransactionDataList]
    status: _common_pb2.Status
    def __init__(self, data: _Optional[_Mapping[str, L2TransactionDataList]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class L2TransactionDataList(_message.Message):
    __slots__ = ("transactions",)
    TRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    transactions: _containers.RepeatedCompositeFieldContainer[L2TransactionData]
    def __init__(self, transactions: _Optional[_Iterable[_Union[L2TransactionData, _Mapping]]] = ...) -> None: ...

class SubscriptionRequest(_message.Message):
    __slots__ = ("symbols", "adjust_type", "subscription_type")
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    ADJUST_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    symbols: _containers.RepeatedScalarFieldContainer[str]
    adjust_type: str
    subscription_type: SubscriptionType
    def __init__(self, symbols: _Optional[_Iterable[str]] = ..., adjust_type: _Optional[str] = ..., subscription_type: _Optional[_Union[SubscriptionType, str]] = ...) -> None: ...

class WholeQuoteRequest(_message.Message):
    __slots__ = ("markets",)
    MARKETS_FIELD_NUMBER: _ClassVar[int]
    markets: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, markets: _Optional[_Iterable[str]] = ...) -> None: ...

class SubscriptionResponse(_message.Message):
    __slots__ = ("subscription_id", "status", "created_at", "symbols", "subscription_type", "rpc_status")
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    RPC_STATUS_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    status: str
    created_at: str
    symbols: _containers.RepeatedScalarFieldContainer[str]
    subscription_type: str
    rpc_status: _common_pb2.Status
    def __init__(self, subscription_id: _Optional[str] = ..., status: _Optional[str] = ..., created_at: _Optional[str] = ..., symbols: _Optional[_Iterable[str]] = ..., subscription_type: _Optional[str] = ..., rpc_status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class UnsubscribeRequest(_message.Message):
    __slots__ = ("subscription_id",)
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    def __init__(self, subscription_id: _Optional[str] = ...) -> None: ...

class UnsubscribeResponse(_message.Message):
    __slots__ = ("success", "message", "status")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    status: _common_pb2.Status
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class QuoteUpdate(_message.Message):
    __slots__ = ("stock_code", "timestamp", "last_price", "open", "high", "low", "close", "volume", "amount", "pre_close", "bid_price", "ask_price", "bid_vol", "ask_vol")
    STOCK_CODE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PRE_CLOSE_FIELD_NUMBER: _ClassVar[int]
    BID_PRICE_FIELD_NUMBER: _ClassVar[int]
    ASK_PRICE_FIELD_NUMBER: _ClassVar[int]
    BID_VOL_FIELD_NUMBER: _ClassVar[int]
    ASK_VOL_FIELD_NUMBER: _ClassVar[int]
    stock_code: str
    timestamp: str
    last_price: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float
    pre_close: float
    bid_price: _containers.RepeatedScalarFieldContainer[float]
    ask_price: _containers.RepeatedScalarFieldContainer[float]
    bid_vol: _containers.RepeatedScalarFieldContainer[int]
    ask_vol: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, stock_code: _Optional[str] = ..., timestamp: _Optional[str] = ..., last_price: _Optional[float] = ..., open: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., close: _Optional[float] = ..., volume: _Optional[int] = ..., amount: _Optional[float] = ..., pre_close: _Optional[float] = ..., bid_price: _Optional[_Iterable[float]] = ..., ask_price: _Optional[_Iterable[float]] = ..., bid_vol: _Optional[_Iterable[int]] = ..., ask_vol: _Optional[_Iterable[int]] = ...) -> None: ...

class SubscriptionInfoRequest(_message.Message):
    __slots__ = ("subscription_id",)
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    def __init__(self, subscription_id: _Optional[str] = ...) -> None: ...

class SubscriptionInfoResponse(_message.Message):
    __slots__ = ("subscription_id", "symbols", "adjust_type", "subscription_type", "created_at", "last_heartbeat", "active", "queue_size", "status")
    SUBSCRIPTION_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOLS_FIELD_NUMBER: _ClassVar[int]
    ADJUST_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_HEARTBEAT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    QUEUE_SIZE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    subscription_id: str
    symbols: _containers.RepeatedScalarFieldContainer[str]
    adjust_type: str
    subscription_type: str
    created_at: str
    last_heartbeat: str
    active: bool
    queue_size: int
    status: _common_pb2.Status
    def __init__(self, subscription_id: _Optional[str] = ..., symbols: _Optional[_Iterable[str]] = ..., adjust_type: _Optional[str] = ..., subscription_type: _Optional[str] = ..., created_at: _Optional[str] = ..., last_heartbeat: _Optional[str] = ..., active: bool = ..., queue_size: _Optional[int] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...

class SubscriptionListResponse(_message.Message):
    __slots__ = ("subscriptions", "status")
    SUBSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    subscriptions: _containers.RepeatedCompositeFieldContainer[SubscriptionInfoResponse]
    status: _common_pb2.Status
    def __init__(self, subscriptions: _Optional[_Iterable[_Union[SubscriptionInfoResponse, _Mapping]]] = ..., status: _Optional[_Union[_common_pb2.Status, _Mapping]] = ...) -> None: ...
