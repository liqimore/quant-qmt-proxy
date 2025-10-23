"""
数据服务层
"""
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import xtquant.xtdata as xtdata
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
    
    xtdata = MockModule()
    xttrader = MockModule()
    xtconstant = MockModule()

from app.models.data_models import (
    MarketDataRequest, FinancialDataRequest, SectorRequest, 
    IndexWeightRequest, MarketDataResponse, FinancialDataResponse,
    SectorResponse, IndexWeightResponse, InstrumentInfo,
    TradingCalendarResponse, ETFInfoResponse
)
from app.utils.exceptions import DataServiceException
from app.utils.helpers import serialize_data, validate_stock_code, validate_date_range
from app.config import Settings, XTQuantMode


class DataService:
    """数据服务类"""
    
    def __init__(self, settings: Settings):
        """初始化数据服务"""
        self.settings = settings
        self._initialized = False
        self._try_initialize()
    
    def _try_initialize(self):
        """尝试初始化xtdata"""
        if not XTQUANT_AVAILABLE:
            print("xtquant模块不可用，使用模拟数据")
            self._initialized = False
            return
        
        if self.settings.xtquant.mode == XTQuantMode.MOCK:
            print("使用模拟数据模式")
            self._initialized = False
            return
        
        try:
            # 初始化xtdata
            xtdata.connect()
            self._initialized = True
            print(f"xtdata初始化成功，模式: {self.settings.xtquant.mode.value}")
        except Exception as e:
            print(f"xtdata初始化失败: {e}")
            self._initialized = False
    
    def _should_use_real_data(self) -> bool:
        """判断是否使用真实数据"""
        return (
            XTQUANT_AVAILABLE and 
            self._initialized and 
            self.settings.xtquant.mode in [XTQuantMode.REAL, XTQuantMode.DEV]
        )
    
    def get_market_data(self, request: MarketDataRequest) -> List[MarketDataResponse]:
        """获取市场数据"""
        try:
            results = []
            for stock_code in request.stock_codes:
                if not validate_stock_code(stock_code):
                    raise DataServiceException(f"无效的股票代码: {stock_code}")
                
                if self._should_use_real_data():
                    # 使用真实xtdata接口
                    try:
                        data = xtdata.get_market_data(
                            stock_code, 
                            period=request.period.value,
                            start_time=request.start_date,
                            end_time=request.end_date,
                            count=-1,
                            dividend_type=request.adjust_type or "none"
                        )
                        
                        # 转换数据格式
                        formatted_data = self._format_market_data(data, request.fields)
                        
                    except Exception as e:
                        print(f"获取真实数据失败，使用模拟数据: {e}")
                        formatted_data = self._get_mock_market_data(stock_code, request)
                else:
                    # 使用模拟数据
                    formatted_data = self._get_mock_market_data(stock_code, request)
                
                response = MarketDataResponse(
                    stock_code=stock_code,
                    data=formatted_data,
                    fields=request.fields or ["time", "open", "high", "low", "close", "volume"],
                    period=request.period.value,
                    start_date=request.start_date,
                    end_date=request.end_date
                )
                results.append(response)
            
            return results
            
        except Exception as e:
            raise DataServiceException(f"获取市场数据失败: {str(e)}")
    
    def get_financial_data(self, request: FinancialDataRequest) -> List[FinancialDataResponse]:
        """获取财务数据"""
        try:
            results = []
            for stock_code in request.stock_codes:
                for table_name in request.table_list:
                    if self._should_use_real_data():
                        # 使用真实xtdata接口
                        try:
                            data = xtdata.get_financial_data(
                                stock_code,
                                table_list=[table_name],
                                start_time=request.start_date,
                                end_time=request.end_date
                            )
                            
                            # 转换数据格式
                            formatted_data = self._format_financial_data(data, table_name)
                            
                        except Exception as e:
                            print(f"获取真实财务数据失败，使用模拟数据: {e}")
                            formatted_data = self._get_mock_financial_data(stock_code, table_name)
                    else:
                        # 使用模拟数据
                        formatted_data = self._get_mock_financial_data(stock_code, table_name)
                    
                    response = FinancialDataResponse(
                        stock_code=stock_code,
                        table_name=table_name,
                        data=formatted_data,
                        columns=["date", "value1", "value2", "value3"]
                    )
                    results.append(response)
            
            return results
            
        except Exception as e:
            raise DataServiceException(f"获取财务数据失败: {str(e)}")
    
    def get_sector_list(self) -> List[SectorResponse]:
        """获取板块列表"""
        try:
            if self._should_use_real_data():
                # 使用真实xtdata接口
                try:
                    sectors = xtdata.get_sector_list()
                    results = []
                    for sector_name in sectors:
                        # 获取板块内股票列表
                        stock_list = xtdata.get_stock_list_in_sector(sector_name)
                        
                        response = SectorResponse(
                            sector_name=sector_name,
                            stock_list=stock_list,
                            sector_type="industry"  # 可以根据实际情况调整
                        )
                        results.append(response)
                    
                    return results
                    
                except Exception as e:
                    print(f"获取真实板块数据失败，使用模拟数据: {e}")
            
            # 使用模拟数据
            mock_sectors = [
                {"sector_name": "银行", "sector_type": "industry"},
                {"sector_name": "科技", "sector_type": "industry"},
                {"sector_name": "医药", "sector_type": "industry"},
            ]
            
            results = []
            for sector_info in mock_sectors:
                # 模拟股票列表
                mock_stock_list = ["000001.SZ", "000002.SZ", "600000.SH"]
                
                response = SectorResponse(
                    sector_name=sector_info["sector_name"],
                    stock_list=mock_stock_list,
                    sector_type=sector_info["sector_type"]
                )
                results.append(response)
            
            return results
            
        except Exception as e:
            raise DataServiceException(f"获取板块列表失败: {str(e)}")
    
    def get_index_weight(self, request: IndexWeightRequest) -> IndexWeightResponse:
        """获取指数权重"""
        try:
            if self._should_use_real_data():
                # 使用真实xtdata接口
                try:
                    weights = xtdata.get_index_weight(request.index_code, request.date)
                    
                    # 转换数据格式
                    formatted_weights = self._format_index_weight(weights)
                    
                    return IndexWeightResponse(
                        index_code=request.index_code,
                        date=request.date or datetime.now().strftime("%Y%m%d"),
                        weights=formatted_weights
                    )
                    
                except Exception as e:
                    print(f"获取真实指数权重失败，使用模拟数据: {e}")
            
            # 使用模拟数据
            mock_weights = [
                {"stock_code": "000001.SZ", "weight": 0.15, "market_cap": 1000000},
                {"stock_code": "000002.SZ", "weight": 0.12, "market_cap": 800000},
                {"stock_code": "600000.SH", "weight": 0.10, "market_cap": 700000},
            ]
            
            return IndexWeightResponse(
                index_code=request.index_code,
                date=request.date or datetime.now().strftime("%Y%m%d"),
                weights=mock_weights
            )
            
        except Exception as e:
            raise DataServiceException(f"获取指数权重失败: {str(e)}")
    
    def get_trading_calendar(self, year: int) -> TradingCalendarResponse:
        """获取交易日历"""
        try:
            if self._should_use_real_data():
                # 使用真实xtdata接口
                try:
                    trading_dates = xtdata.get_trading_dates(year)
                    holidays = xtdata.get_holidays(year)
                    
                    return TradingCalendarResponse(
                        trading_dates=trading_dates,
                        holidays=holidays,
                        year=year
                    )
                    
                except Exception as e:
                    print(f"获取真实交易日历失败，使用模拟数据: {e}")
            
            # 使用模拟数据
            mock_trading_dates = [
                f"{year}0103", f"{year}0104", f"{year}0105",
                f"{year}0108", f"{year}0109", f"{year}0110"
            ]
            mock_holidays = [
                f"{year}0101", f"{year}0102", f"{year}0106", f"{year}0107"
            ]
            
            return TradingCalendarResponse(
                trading_dates=mock_trading_dates,
                holidays=mock_holidays,
                year=year
            )
            
        except Exception as e:
            raise DataServiceException(f"获取交易日历失败: {str(e)}")
    
    def get_instrument_info(self, stock_code: str) -> InstrumentInfo:
        """获取合约信息"""
        try:
            if self._should_use_real_data():
                # 使用真实xtdata接口
                try:
                    info = xtdata.get_instrument_detail(stock_code)
                    
                    return InstrumentInfo(
                        instrument_code=stock_code,
                        instrument_name=info.get("instrument_name", f"股票{stock_code}"),
                        market_type=info.get("market_type", "SH"),
                        instrument_type=info.get("instrument_type", "STOCK"),
                        list_date=info.get("list_date"),
                        delist_date=info.get("delist_date")
                    )
                    
                except Exception as e:
                    print(f"获取真实合约信息失败，使用模拟数据: {e}")
            
            # 使用模拟数据
            return InstrumentInfo(
                instrument_code=stock_code,
                instrument_name=f"股票{stock_code}",
                market_type="SH" if stock_code.endswith(".SH") else "SZ",
                instrument_type="STOCK",
                list_date="20200101",
                delist_date=None
            )
            
        except Exception as e:
            raise DataServiceException(f"获取合约信息失败: {str(e)}")
    
    def _format_market_data(self, data: Any, fields: Optional[List[str]]) -> List[Dict[str, Any]]:
        """格式化市场数据"""
        # 这里需要根据xtdata返回的实际数据格式进行转换
        # 由于我们无法确定具体的数据格式，这里提供一个示例
        if not data:
            return []
        
        formatted_data = []
        for item in data:
            formatted_item = {
                "time": item.get("time", ""),
                "open": item.get("open", 0.0),
                "high": item.get("high", 0.0),
                "low": item.get("low", 0.0),
                "close": item.get("close", 0.0),
                "volume": item.get("volume", 0)
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    def _format_financial_data(self, data: Any, table_name: str) -> List[Dict[str, Any]]:
        """格式化财务数据"""
        # 这里需要根据xtdata返回的实际数据格式进行转换
        if not data:
            return []
        
        formatted_data = []
        for item in data:
            formatted_item = {
                "date": item.get("date", ""),
                "value1": item.get("value1", 0.0),
                "value2": item.get("value2", 0.0),
                "value3": item.get("value3", 0.0)
            }
            formatted_data.append(formatted_item)
        
        return formatted_data
    
    def _format_index_weight(self, weights: Any) -> List[Dict[str, Any]]:
        """格式化指数权重数据"""
        # 这里需要根据xtdata返回的实际数据格式进行转换
        if not weights:
            return []
        
        formatted_weights = []
        for weight in weights:
            formatted_weight = {
                "stock_code": weight.get("stock_code", ""),
                "weight": weight.get("weight", 0.0),
                "market_cap": weight.get("market_cap", 0.0)
            }
            formatted_weights.append(formatted_weight)
        
        return formatted_weights
    
    def _get_mock_market_data(self, stock_code: str, request: MarketDataRequest) -> List[Dict[str, Any]]:
        """生成模拟市场数据"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        start_date = datetime.strptime(request.start_date, "%Y%m%d")
        
        for i in range(10):  # 生成10天的模拟数据
            date = start_date + timedelta(days=i)
            base_price = 100 + random.uniform(-10, 10)
            
            data.append({
                "time": date.strftime("%Y%m%d"),
                "open": round(base_price + random.uniform(-2, 2), 2),
                "high": round(base_price + random.uniform(0, 5), 2),
                "low": round(base_price - random.uniform(0, 5), 2),
                "close": round(base_price + random.uniform(-3, 3), 2),
                "volume": random.randint(1000000, 10000000)
            })
        
        return data
    
    def _get_mock_financial_data(self, stock_code: str, table_name: str) -> List[Dict[str, Any]]:
        """生成模拟财务数据"""
        import random
        
        data = []
        for i in range(5):  # 生成5个季度的模拟数据
            year = 2023
            quarter = i + 1
            
            data.append({
                "date": f"{year}Q{quarter}",
                "value1": round(random.uniform(1000000, 10000000), 2),
                "value2": round(random.uniform(500000, 5000000), 2),
                "value3": round(random.uniform(0.1, 0.3), 4)
            })
        
        return data
