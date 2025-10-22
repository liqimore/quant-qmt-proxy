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
    """合约信息"""
    instrument_code: str
    instrument_name: str
    market_type: str
    instrument_type: str
    list_date: Optional[str] = None
    delist_date: Optional[str] = None


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
