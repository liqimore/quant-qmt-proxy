"""
数据相关模型
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PeriodType(str, Enum):
    """周期类型"""
    TICK = "tick"
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1mon"
    QUARTER = "1q"
    YEAR_HALF = "1hy"
    YEAR = "1y"


class MarketType(str, Enum):
    """市场类型"""
    SHANGHAI = "SH"
    SHENZHEN = "SZ"
    BEIJING = "BJ"
    FUTURES = "FUTURES"
    OPTION = "OPTION"


class DataRequest(BaseModel):
    """数据请求基础模型"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_date: str = Field('', description="开始日期 YYYYMMDD 或 YYYYMMDDHHMMSS")
    end_date: str = Field('', description="结束日期 YYYYMMDD 或 YYYYMMDDHHMMSS")
    period: PeriodType = Field(PeriodType.DAILY, description="数据周期")
    
    @field_validator('stock_codes')
    def validate_stock_codes(cls, v):
        if not v or len(v) == 0:
            raise ValueError('股票代码列表不能为空')
        return v
    
    @field_validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v == '':
            return v
        if (len(v) != 8 and len(v) != 14) or not v.isdigit():
            raise ValueError('日期格式必须为YYYYMMDD 或 YYYYMMDDHHMMSS')
        return v


class MarketDataRequest(DataRequest):
    """市场数据请求"""
    fields: Optional[List[str]] = Field(None, description="字段列表")
    adjust_type: Optional[str] = Field("none", description="复权类型")
    fill_data: bool = Field(True, description="是否填充缺失数据")
    disable_download: bool = Field(False, description="是否禁用下载功能")


class FinancialDataRequest(BaseModel):
    """财务数据请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    table_list: List[str] = Field(..., description="财务表列表")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")


class SectorRequest(BaseModel):
    """板块数据请求"""
    sector_name: str = Field(..., description="板块名称")
    sector_type: Optional[str] = Field(None, description="板块类型")


class IndexWeightRequest(BaseModel):
    """指数权重请求"""
    index_code: str = Field(..., description="指数代码")
    date: Optional[str] = Field(None, description="日期")


class MarketDataResponse(BaseModel):
    """市场数据响应"""
    stock_code: str
    data: List[Dict[str, Any]]
    fields: List[str]
    period: str
    start_date: str
    end_date: str


class FinancialDataResponse(BaseModel):
    """财务数据响应"""
    stock_code: str
    table_name: str
    data: List[Dict[str, Any]]
    columns: List[str]


class SectorResponse(BaseModel):
    """板块响应"""
    sector_name: str
    stock_list: List[str]
    sector_type: Optional[str] = None


class IndexWeightResponse(BaseModel):
    """指数权重响应"""
    index_code: str
    date: str
    weights: List[Dict[str, Any]]


class InstrumentInfo(BaseModel):
    """合约信息（完整字段，参考xtquant文档）"""
    # 基础信息
    ExchangeID: Optional[str] = Field(None, description="合约市场代码")
    InstrumentID: Optional[str] = Field(None, description="合约代码")
    InstrumentName: Optional[str] = Field(None, description="合约名称")
    ProductID: Optional[str] = Field(None, description="合约的品种ID(期货)")
    ProductName: Optional[str] = Field(None, description="合约的品种名称(期货)")
    ProductType: Optional[int] = Field(None, description="合约的类型")
    ExchangeCode: Optional[str] = Field(None, description="交易所代码")
    UniCode: Optional[str] = Field(None, description="统一规则代码")
    
    # 日期信息
    CreateDate: Optional[str] = Field(None, description="创建日期")
    OpenDate: Optional[str] = Field(None, description="上市日期")
    ExpireDate: Optional[int] = Field(None, description="退市日或者到期日")
    
    # 价格信息
    PreClose: Optional[float] = Field(None, description="前收盘价格")
    SettlementPrice: Optional[float] = Field(None, description="前结算价格")
    UpStopPrice: Optional[float] = Field(None, description="当日涨停价")
    DownStopPrice: Optional[float] = Field(None, description="当日跌停价")
    
    # 股本信息
    FloatVolume: Optional[float] = Field(None, description="流通股本")
    TotalVolume: Optional[float] = Field(None, description="总股本")
    
    # 期货相关
    LongMarginRatio: Optional[float] = Field(None, description="多头保证金率")
    ShortMarginRatio: Optional[float] = Field(None, description="空头保证金率")
    PriceTick: Optional[float] = Field(None, description="最小价格变动单位")
    VolumeMultiple: Optional[int] = Field(None, description="合约乘数")
    MainContract: Optional[int] = Field(None, description="主力合约标记")
    LastVolume: Optional[int] = Field(None, description="昨日持仓量")
    
    # 状态信息
    InstrumentStatus: Optional[int] = Field(None, description="合约停牌状态")
    IsTrading: Optional[bool] = Field(None, description="合约是否可交易")
    IsRecent: Optional[bool] = Field(None, description="是否是近月合约")
    
    # 兼容旧字段名
    instrument_code: Optional[str] = Field(None, description="合约代码（兼容字段）")
    instrument_name: Optional[str] = Field(None, description="合约名称（兼容字段）")
    market_type: Optional[str] = Field(None, description="市场类型（兼容字段）")
    instrument_type: Optional[str] = Field(None, description="合约类型（兼容字段）")
    list_date: Optional[str] = Field(None, description="上市日期（兼容字段）")
    delist_date: Optional[str] = Field(None, description="退市日期（兼容字段）")


class TradingCalendarResponse(BaseModel):
    """交易日历响应"""
    trading_dates: List[str]
    holidays: List[str]
    year: int


class ETFInfoResponse(BaseModel):
    """ETF信息响应"""
    etf_code: str
    etf_name: str
    underlying_asset: str
    creation_unit: int
    redemption_unit: int


# ==================== 阶段1: 基础信息接口模型 ====================

class InstrumentTypeInfo(BaseModel):
    """合约类型信息（get_instrument_type返回）"""
    stock_code: str = Field(..., description="合约代码")
    index: bool = Field(False, description="是否为指数")
    stock: bool = Field(False, description="是否为股票")
    fund: bool = Field(False, description="是否为基金")
    etf: bool = Field(False, description="是否为ETF")
    bond: bool = Field(False, description="是否为债券")
    option: bool = Field(False, description="是否为期权")
    futures: bool = Field(False, description="是否为期货")


class HolidayInfo(BaseModel):
    """节假日信息（get_holidays返回）"""
    holidays: List[str] = Field(..., description="节假日列表，YYYYMMDD格式")


class ConvertibleBondInfo(BaseModel):
    """可转债信息（get_cb_info返回，包含xtdata所有字段）"""
    # 基本信息
    bond_code: str = Field(..., description="可转债代码")
    bond_name: Optional[str] = Field(None, description="可转债名称")
    stock_code: Optional[str] = Field(None, description="正股代码")
    stock_name: Optional[str] = Field(None, description="正股名称")
    
    # 转股信息
    conversion_price: Optional[float] = Field(None, description="转股价格")
    conversion_value: Optional[float] = Field(None, description="转股价值")
    conversion_premium_rate: Optional[float] = Field(None, description="转股溢价率")
    
    # 价格信息
    current_price: Optional[float] = Field(None, description="可转债当前价格")
    par_value: Optional[float] = Field(None, description="债券面值")
    
    # 日期信息
    list_date: Optional[str] = Field(None, description="上市日期")
    maturity_date: Optional[str] = Field(None, description="到期日期")
    conversion_begin_date: Optional[str] = Field(None, description="转股起始日")
    conversion_end_date: Optional[str] = Field(None, description="转股结束日")
    
    # 其他字段（根据xtdata实际返回的完整字段）
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始数据（包含所有xtdata字段）")


class IpoInfo(BaseModel):
    """新股申购信息（get_ipo_info返回，包含xtdata所有字段）"""
    # 基本信息
    security_code: str = Field(..., description="证券代码")
    code_name: Optional[str] = Field(None, description="代码简称")
    market: Optional[str] = Field(None, description="所属市场")
    
    # 发行信息
    act_issue_qty: Optional[int] = Field(None, description="发行总量（股）")
    online_issue_qty: Optional[int] = Field(None, description="网上发行量（股）")
    online_sub_code: Optional[str] = Field(None, description="申购代码")
    online_sub_max_qty: Optional[int] = Field(None, description="申购上限（股）")
    publish_price: Optional[float] = Field(None, description="发行价格")
    
    # 财务信息
    is_profit: Optional[int] = Field(None, description="是否已盈利 0:未盈利 1:已盈利")
    industry_pe: Optional[float] = Field(None, description="行业市盈率")
    after_pe: Optional[float] = Field(None, description="发行后市盈率")
    
    # 日期信息
    subscribe_date: Optional[str] = Field(None, description="申购日期")
    lottery_date: Optional[str] = Field(None, description="摇号日期")
    list_date: Optional[str] = Field(None, description="上市日期")
    
    # 其他字段
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始数据（包含所有xtdata字段）")


class PeriodListResponse(BaseModel):
    """可用周期列表响应（get_period_list返回）"""
    periods: List[str] = Field(..., description="可用周期列表")


class DataDirResponse(BaseModel):
    """数据目录响应（get_data_dir返回）"""
    data_dir: str = Field(..., description="本地数据路径")


# ==================== 阶段2: 行情数据获取接口模型 ====================

class LocalDataRequest(BaseModel):
    """本地行情数据请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_time: str = Field("", description="开始时间，YYYYMMDD格式")
    end_time: str = Field("", description="结束时间，YYYYMMDD格式")
    period: str = Field("1d", description="K线周期")
    fields: Optional[List[str]] = Field(None, description="字段列表")
    adjust_type: Optional[str] = Field("none", description="复权类型")


class FullTickRequest(BaseModel):
    """完整tick数据请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_time: str = Field("", description="开始时间")
    end_time: str = Field("", description="结束时间")


class DividFactorsRequest(BaseModel):
    """除权除息数据请求"""
    stock_code: str = Field(..., description="股票代码")


class FullKlineRequest(BaseModel):
    """完整K线数据请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_time: str = Field("", description="开始时间，YYYYMMDD格式")
    end_time: str = Field("", description="结束时间，YYYYMMDD格式")
    period: str = Field("1d", description="K线周期")
    fields: Optional[List[str]] = Field(None, description="字段列表")
    adjust_type: Optional[str] = Field("none", description="复权类型")


class DividendFactor(BaseModel):
    """除权数据（get_divid_factors返回，包含xtdata所有字段）"""
    time: str = Field(..., description="除权日期")
    interest: Optional[float] = Field(None, description="每股股利（税前，元）")
    stock_bonus: Optional[float] = Field(None, description="每股红股（股）")
    stock_gift: Optional[float] = Field(None, description="每股转增股本（股）")
    allot_num: Optional[float] = Field(None, description="每股配股数（股）")
    allot_price: Optional[float] = Field(None, description="配股价格（元）")
    gugai: Optional[int] = Field(None, description="是否股改")
    dr: Optional[float] = Field(None, description="除权系数")


class TickData(BaseModel):
    """分笔数据（包含xtdata所有tick字段）"""
    time: str = Field(..., description="时间戳")
    last_price: float = Field(..., description="最新价")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    last_close: Optional[float] = Field(None, description="前收盘价")
    amount: Optional[float] = Field(None, description="成交总额")
    volume: Optional[int] = Field(None, description="成交总量")
    pvolume: Optional[int] = Field(None, description="原始成交总量")
    stock_status: Optional[int] = Field(None, description="证券状态")
    open_int: Optional[int] = Field(None, description="持仓量")
    last_settlement_price: Optional[float] = Field(None, description="前结算")
    ask_price: Optional[List[float]] = Field(None, description="委卖价")
    bid_price: Optional[List[float]] = Field(None, description="委买价")
    ask_vol: Optional[List[int]] = Field(None, description="委卖量")
    bid_vol: Optional[List[int]] = Field(None, description="委买量")
    transaction_num: Optional[int] = Field(None, description="成交笔数")


# ==================== 阶段3: 数据下载接口模型 ====================

class DownloadTaskStatus(str, Enum):
    """下载任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DownloadHistoryDataRequest(BaseModel):
    """下载历史数据请求"""
    stock_code: str = Field(..., description="股票代码")
    period: str = Field("1d", description="周期")
    start_time: str = Field("", description="起始时间")
    end_time: str = Field("", description="结束时间")
    incrementally: bool = Field(False, description="是否增量下载")


class DownloadHistoryDataBatchRequest(BaseModel):
    """批量下载历史数据请求"""
    stock_list: List[str] = Field(..., description="股票代码列表")
    period: str = Field("1d", description="周期")
    start_time: str = Field("", description="起始时间")
    end_time: str = Field("", description="结束时间")


class DownloadFinancialDataRequest(BaseModel):
    """下载财务数据请求"""
    stock_list: List[str] = Field(..., description="股票代码列表")
    table_list: List[str] = Field(..., description="财务表列表")
    start_date: str = Field("", description="起始日期")
    end_date: str = Field("", description="结束日期")


class DownloadFinancialDataBatchRequest(BaseModel):
    """批量下载财务数据请求（带回调）"""
    stock_list: List[str] = Field(..., description="股票代码列表")
    table_list: List[str] = Field(..., description="财务表列表")
    start_date: str = Field("", description="起始日期")
    end_date: str = Field("", description="结束日期")
    callback_func: Optional[str] = Field(None, description="回调函数名（可选）")


class DownloadIndexWeightRequest(BaseModel):
    """下载指数权重请求"""
    index_code: Optional[str] = Field(None, description="指数代码（可选，为空则下载全部）")


class DownloadHistoryContractsRequest(BaseModel):
    """下载历史合约信息请求"""
    market: Optional[str] = Field(None, description="市场代码（可选）")


class DownloadRequest(BaseModel):
    """数据下载请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    period: Optional[str] = Field(None, description="周期类型")
    start_time: Optional[str] = Field(None, description="起始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    incrementally: Optional[bool] = Field(None, description="是否增量下载")


class DownloadResponse(BaseModel):
    """数据下载响应"""
    task_id: str = Field(..., description="任务ID")
    status: DownloadTaskStatus = Field(..., description="任务状态")
    progress: float = Field(0.0, description="进度 0-100")
    total: int = Field(0, description="总数")
    finished: int = Field(0, description="已完成数")
    message: str = Field("", description="消息")
    current_stock: Optional[str] = Field(None, description="当前处理的股票")


# ==================== 阶段4: 板块管理接口模型 ====================

class SectorCreateRequest(BaseModel):
    """创建板块请求"""
    parent_node: str = Field("", description="父节点，空字符串为'我的'")
    sector_name: str = Field(..., description="板块名称")
    overwrite: bool = Field(True, description="是否覆盖同名板块")


class SectorCreateResponse(BaseModel):
    """创建板块响应"""
    created_name: str = Field(..., description="实际创建的板块名称")
    success: bool = Field(True, description="是否成功")
    message: str = Field("", description="响应消息")


class SectorAddRequest(BaseModel):
    """添加板块请求"""
    sector_name: str = Field(..., description="板块名称")
    stock_list: List[str] = Field(..., description="股票列表")


class SectorRemoveStockRequest(BaseModel):
    """移除板块成分股请求"""
    sector_name: str = Field(..., description="板块名称")
    stock_list: List[str] = Field(..., description="要移除的股票列表")


class SectorResetRequest(BaseModel):
    """重置板块请求"""
    sector_name: str = Field(..., description="板块名称")
    stock_list: List[str] = Field(..., description="新的股票列表")


# ==================== 阶段5: Level2数据接口模型 ====================

class L2QuoteRequest(BaseModel):
    """Level2快照数据请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_time: str = Field("", description="开始时间")
    end_time: str = Field("", description="结束时间")


class L2OrderRequest(BaseModel):
    """Level2逐笔委托请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_time: str = Field("", description="开始时间")
    end_time: str = Field("", description="结束时间")


class L2TransactionRequest(BaseModel):
    """Level2逐笔成交请求"""
    stock_codes: List[str] = Field(..., description="股票代码列表")
    start_time: str = Field("", description="开始时间")
    end_time: str = Field("", description="结束时间")


class L2QuoteData(BaseModel):
    """Level2快照数据（包含xtdata所有l2quote字段）"""
    time: str = Field(..., description="时间戳")
    last_price: float = Field(..., description="最新价")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    amount: Optional[float] = Field(None, description="成交额")
    volume: Optional[int] = Field(None, description="成交总量")
    pvolume: Optional[int] = Field(None, description="原始成交总量")
    open_int: Optional[int] = Field(None, description="持仓量")
    stock_status: Optional[int] = Field(None, description="证券状态")
    transaction_num: Optional[int] = Field(None, description="成交笔数")
    last_close: Optional[float] = Field(None, description="前收盘价")
    last_settlement_price: Optional[float] = Field(None, description="前结算")
    settlement_price: Optional[float] = Field(None, description="今结算")
    pe: Optional[float] = Field(None, description="市盈率")
    ask_price: Optional[List[float]] = Field(None, description="10档委卖价")
    bid_price: Optional[List[float]] = Field(None, description="10档委买价")
    ask_vol: Optional[List[int]] = Field(None, description="10档委卖量")
    bid_vol: Optional[List[int]] = Field(None, description="10档委买量")


class L2OrderData(BaseModel):
    """Level2逐笔委托（包含xtdata所有l2order字段）"""
    time: str = Field(..., description="时间戳")
    price: float = Field(..., description="委托价")
    volume: int = Field(..., description="委托量")
    entrust_no: Optional[int] = Field(None, description="委托号")
    entrust_type: Optional[int] = Field(None, description="委托类型")
    entrust_direction: Optional[int] = Field(None, description="委托方向")


class L2TransactionData(BaseModel):
    """Level2逐笔成交（包含xtdata所有l2transaction字段）"""
    time: str = Field(..., description="时间戳")
    price: float = Field(..., description="成交价")
    volume: int = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    trade_index: Optional[int] = Field(None, description="成交记录号")
    buy_no: Optional[int] = Field(None, description="买方委托号")
    sell_no: Optional[int] = Field(None, description="卖方委托号")
    trade_type: Optional[int] = Field(None, description="成交类型")
    trade_flag: Optional[int] = Field(None, description="成交标志")


# ==================== 阶段6: 行情订阅接口模型 ====================

class SubscriptionType(str, Enum):
    """订阅类型"""
    QUOTE = "quote"  # 单股订阅
    WHOLE_QUOTE = "whole_quote"  # 全推订阅


class SubscriptionRequest(BaseModel):
    """订阅请求"""
    symbols: List[str] = Field(..., min_items=1, description="股票代码列表（不能为空）")    
    period: PeriodType = Field(PeriodType.TICK, description="数据周期")
    start_date: str = Field('', description="开始日期 YYYYMMDD 或 YYYYMMDDHHMMSS")
    adjust_type: str = Field("none", description="复权类型: none, front, back, front_ratio, back_ratio")
    subscription_type: SubscriptionType = Field(
        SubscriptionType.QUOTE,
        description="订阅类型"
    )
    
    @field_validator('symbols')
    def validate_symbols(cls, v):
        if not v or len(v) == 0:
            raise ValueError('股票代码列表不能为空')
        # 过滤掉空字符串
        v = [s.strip() for s in v if s and s.strip()]
        if not v:
            raise ValueError('股票代码列表不能为空')
        return v
    
    @field_validator('start_date')
    def validate_date_format(cls, v):
        if v == '':
            return v
        if (len(v) != 8 and len(v) != 14) or not v.isdigit():
            raise ValueError('日期格式必须为YYYYMMDD 或 YYYYMMDDHHMMSS')
        return v
    
    @field_validator('adjust_type')
    def validate_adjust_type(cls, v):
        if v not in ["none", "front", "back", "front_ratio", "back_ratio"]:
            raise ValueError('复权类型必须是 none, front, back, "front_ratio" 或 "back_ratio"')
        return v


class WholeQuoteRequest(BaseModel):
    """全推订阅请求"""
    markets: List[str] = Field(["SH", "SZ"], description="市场列表")


class SubscriptionResponse(BaseModel):
    """订阅响应"""
    subscription_id: str = Field(..., description="订阅ID")
    status: str = Field(..., description="订阅状态")
    created_at: str = Field(..., description="创建时间")
    symbols: Optional[List[str]] = Field(None, description="订阅的股票代码")
    subscription_type: str = Field(..., description="订阅类型")


class UnsubscribeRequest(BaseModel):
    """取消订阅请求"""
    subscription_id: str = Field(..., description="订阅ID")


class UnsubscribeResponse(BaseModel):
    """取消订阅响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="消息")


class QuoteUpdate(BaseModel):
    """实时行情更新数据"""
    stock_code: str = Field(..., description="股票代码")
    timestamp: str = Field(..., description="时间戳")
    last_price: Optional[float] = Field(None, description="最新价")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    close: Optional[float] = Field(None, description="收盘价")
    volume: Optional[int] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    pre_close: Optional[float] = Field(None, description="前收盘价")
    bid_price: Optional[List[float]] = Field(None, description="委买价（5档）")
    ask_price: Optional[List[float]] = Field(None, description="委卖价（5档）")
    bid_vol: Optional[List[int]] = Field(None, description="委买量（5档）")
    ask_vol: Optional[List[int]] = Field(None, description="委卖量（5档）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_code": "000001.SZ",
                "timestamp": "2024-01-01T09:30:00",
                "last_price": 10.5,
                "open": 10.0,
                "high": 10.8,
                "low": 9.9,
                "close": 10.5,
                "volume": 1000000,
                "amount": 10500000.0
            }
        }


class SubscriptionInfoResponse(BaseModel):
    """订阅信息响应"""
    subscription_id: str
    symbols: List[str]
    adjust_type: str
    subscription_type: str
    created_at: str
    last_heartbeat: str
    active: bool
    queue_size: int
