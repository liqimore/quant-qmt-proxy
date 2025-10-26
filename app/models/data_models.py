"""
数据相关模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum


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
    MONTHLY = "1M"


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
    start_date: str = Field(..., description="开始日期 YYYYMMDD")
    end_date: str = Field(..., description="结束日期 YYYYMMDD")
    period: PeriodType = Field(PeriodType.DAILY, description="数据周期")
    
    @validator('stock_codes')
    def validate_stock_codes(cls, v):
        if not v or len(v) == 0:
            raise ValueError('股票代码列表不能为空')
        return v
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if len(v) != 8 or not v.isdigit():
            raise ValueError('日期格式必须为YYYYMMDD')
        return v


class MarketDataRequest(DataRequest):
    """市场数据请求"""
    fields: Optional[List[str]] = Field(None, description="字段列表")
    adjust_type: Optional[str] = Field("none", description="复权类型")


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
