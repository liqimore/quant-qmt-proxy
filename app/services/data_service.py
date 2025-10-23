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
        print("\n" + "=" * 70)
        print("🔧 DataService 初始化开始")
        print("=" * 70)
        
        if not XTQUANT_AVAILABLE:
            print("❌ xtquant模块不可用，使用模拟数据")
            self._initialized = False
            return
        
        print(f"✅ xtquant模块已导入")
        print(f"📋 配置模式: {self.settings.xtquant.mode.value}")
        
        if self.settings.xtquant.mode == XTQuantMode.MOCK:
            print("⚠️  使用模拟数据模式（不连接真实QMT）")
            self._initialized = False
            return
        
        try:
            print(f"\n🔗 准备连接QMT服务...")
            
            # 设置数据路径（如果配置了QMT路径）
            if self.settings.xtquant.data.qmt_userdata_path:
                qmt_data_dir = os.path.join(
                    self.settings.xtquant.data.qmt_userdata_path,
                    'datadir'
                )
                xtdata.data_dir = qmt_data_dir
                print(f"📁 设置数据路径: {qmt_data_dir}")
                print(f"   路径存在: {os.path.exists(qmt_data_dir)}")
            
            # 初始化xtdata
            print(f"🔌 正在连接xtquant服务...")
            xtdata.enable_hello = True  # 显示连接信息
            client = xtdata.connect()
            
            if client and client.is_connected():
                self._initialized = True
                actual_data_dir = xtdata.get_data_dir()
                print(f"✅ xtdata连接成功！")
                print(f"   模式: {self.settings.xtquant.mode.value}")
                print(f"   实际数据路径: {actual_data_dir}")
                print(f"   客户端状态: 已连接")
            else:
                print(f"❌ xtdata连接失败：客户端未连接")
                self._initialized = False
                
        except Exception as e:
            print(f"❌ xtdata初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self._initialized = False
        
        print("=" * 70 + "\n")
    
    def _should_use_real_data(self) -> bool:
        """判断是否使用真实数据"""
        return (
            XTQUANT_AVAILABLE and 
            self._initialized and 
            self.settings.xtquant.mode in [XTQuantMode.REAL, XTQuantMode.DEV]
        )
    
    def get_market_data(self, request: MarketDataRequest) -> List[MarketDataResponse]:
        """获取市场数据"""
        print(f"\n📊 获取市场数据请求:")
        print(f"   股票代码: {request.stock_codes}")
        print(f"   周期: {request.period.value}")
        print(f"   开始日期: {request.start_date}")
        print(f"   结束日期: {request.end_date}")
        print(f"   使用真实数据: {self._should_use_real_data()}")
        print(f"   xtdata已初始化: {self._initialized}")
        
        try:
            results = []
            for stock_code in request.stock_codes:
                if not validate_stock_code(stock_code):
                    raise DataServiceException(f"无效的股票代码: {stock_code}")
                
                if self._should_use_real_data():
                    # 使用真实xtdata接口
                    print(f"\n🔍 正在获取 {stock_code} 的真实数据...")
                    try:
                        # 先下载历史数据（确保本地有数据）
                        print(f"   📥 下载历史数据...")
                        xtdata.download_history_data(
                            stock_code=stock_code,
                            period=request.period.value,
                            start_time=request.start_date,
                            end_time=request.end_date
                        )
                        
                        # 注意：stock_list必须是列表，field_list也必须是列表
                        data = xtdata.get_market_data(
                            field_list=request.fields or [],
                            stock_list=[stock_code],  # 必须是列表
                            period=request.period.value,
                            start_time=request.start_date,
                            end_time=request.end_date,
                            count=-1,
                            dividend_type=request.adjust_type or "none"
                        )
                        
                        print(f"   ✅ 获取成功，原始数据类型: {type(data)}")
                        if hasattr(data, 'shape'):
                            print(f"   数据形状: {data.shape}")
                        
                        # 打印原始数据结构用于调试
                        if isinstance(data, dict):
                            print(f"   数据字典keys: {list(data.keys())}")
                            for k, v in data.items():
                                print(f"   [{k}] 类型: {type(v)}, 形状: {v.shape if hasattr(v, 'shape') else 'N/A'}")
                                if hasattr(v, 'head'):
                                    print(f"   前几行:\n{v.head()}")
                        
                        # 转换数据格式
                        formatted_data = self._format_market_data(data, request.fields)
                        print(f"   格式化后数据条数: {len(formatted_data)}")
                        if formatted_data:
                            print(f"   格式化后首条数据: {formatted_data[0]}")
                        
                    except Exception as e:
                        print(f"   ❌ 获取真实数据失败: {e}")
                        import traceback
                        traceback.print_exc()
                        # dev/real模式下直接抛出异常，不回退到mock
                        raise DataServiceException(f"获取市场数据失败 [{stock_code}]: {str(e)}")
                else:
                    # 使用模拟数据（仅mock模式）
                    print(f"\n🎭 使用模拟数据 for {stock_code}")
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
        print(f"\n💰 获取财务数据请求:")
        print(f"   股票代码: {request.stock_codes}")
        print(f"   表名: {request.table_list}")
        print(f"   使用真实数据: {self._should_use_real_data()}")
        
        try:
            results = []
            for stock_code in request.stock_codes:
                for table_name in request.table_list:
                    if self._should_use_real_data():
                        # 使用真实xtdata接口
                        print(f"\n🔍 正在获取 {stock_code} 的 {table_name} 财务数据...")
                        try:
                            # 注意：第一个参数必须是列表
                            data = xtdata.get_financial_data(
                                [stock_code],  # 必须是列表
                                table_list=[table_name],
                                start_time=request.start_date,
                                end_time=request.end_date
                            )
                            
                            print(f"   ✅ 获取成功，数据类型: {type(data)}")
                            print(f"   数据内容: {data}")
                            
                            # 转换数据格式
                            # xtdata返回格式: {stock_code: {table_name: DataFrame}}
                            formatted_data = self._format_financial_data(data, stock_code, table_name)
                            print(f"   格式化后数据条数: {len(formatted_data)}")
                            
                        except Exception as e:
                            print(f"   ❌ 获取真实财务数据失败: {e}")
                            # dev/real模式下直接抛出异常，不回退到mock
                            raise DataServiceException(f"获取财务数据失败 [{stock_code}/{table_name}]: {str(e)}")
                    else:
                        # 使用模拟数据（仅mock模式）
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
                    print(f"获取真实板块数据失败: {e}")
                    # dev/real模式下直接抛出异常，不回退到mock
                    raise DataServiceException(f"获取板块列表失败: {str(e)}")
            
            # 使用模拟数据（仅mock模式）
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
                    # xtdata.get_index_weight只接受一个参数: index_code
                    # 返回的是当前最新的指数成分权重
                    weights_data = xtdata.get_index_weight(request.index_code)
                    
                    print(f"   获取指数权重成功，数据类型: {type(weights_data)}")
                    
                    # 转换数据格式
                    if isinstance(weights_data, dict):
                        # 如果返回字典，尝试转换
                        formatted_weights = []
                        for stock_code, weight_info in weights_data.items():
                            formatted_weights.append({
                                "stock_code": stock_code,
                                "weight": weight_info if isinstance(weight_info, (int, float)) else 0.0,
                                "market_cap": 0.0
                            })
                    elif isinstance(weights_data, list):
                        formatted_weights = self._format_index_weight(weights_data)
                    else:
                        print(f"   ⚠️  未知的权重数据格式: {type(weights_data)}")
                        formatted_weights = []
                    
                    return IndexWeightResponse(
                        index_code=request.index_code,
                        date=request.date or datetime.now().strftime("%Y%m%d"),
                        weights=formatted_weights
                    )
                    
                except Exception as e:
                    print(f"获取真实指数权重失败: {e}")
                    import traceback
                    traceback.print_exc()
                    # dev/real模式下直接抛出异常，不回退到mock
                    raise DataServiceException(f"获取指数权重失败 [{request.index_code}]: {str(e)}")
            
            # 使用模拟数据（仅mock模式）
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
                    # xtdata.get_trading_dates需要市场代码和时间范围
                    # 获取指定年份的交易日
                    start_time = f"{year}0101"
                    end_time = f"{year}1231"
                    
                    # 获取沪深市场的交易日（SSE=上交所，SZSE=深交所）
                    trading_dates_sh = xtdata.get_trading_dates(market="SSE", start_time=start_time, end_time=end_time)
                    
                    # 转换为字符串格式 YYYYMMDD
                    trading_dates = [str(d) for d in trading_dates_sh] if trading_dates_sh else []
                    
                    # 生成该年所有日期，然后排除交易日得到假期
                    from datetime import datetime, timedelta
                    all_dates = []
                    start_date = datetime(year, 1, 1)
                    end_date = datetime(year, 12, 31)
                    current_date = start_date
                    while current_date <= end_date:
                        all_dates.append(current_date.strftime("%Y%m%d"))
                        current_date += timedelta(days=1)
                    
                    # 假期 = 所有日期 - 交易日
                    holidays = [d for d in all_dates if d not in trading_dates]
                    
                    return TradingCalendarResponse(
                        trading_dates=trading_dates,
                        holidays=holidays,
                        year=year
                    )
                    
                except Exception as e:
                    print(f"获取真实交易日历失败: {e}")
                    import traceback
                    traceback.print_exc()
                    # dev/real模式下直接抛出异常，不回退到mock
                    raise DataServiceException(f"获取交易日历失败 [{year}]: {str(e)}")
            
            # 使用模拟数据（仅mock模式）
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
                    print(f"获取真实合约信息失败: {e}")
                    # dev/real模式下直接抛出异常，不回退到mock
                    raise DataServiceException(f"获取合约信息失败 [{stock_code}]: {str(e)}")
            
            # 使用模拟数据（仅mock模式）
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
        """格式化市场数据
        xtquant返回格式: {'field_name': DataFrame, ...}
        DataFrame的行是股票代码（index），列是日期
        """
        if not data:
            return []
        
        print(f"   📝 格式化数据，类型: {type(data)}")
        
        formatted_data = []
        
        # 处理xtdata特殊格式: {'time': DataFrame, 'open': DataFrame, ...}
        if isinstance(data, dict) and len(data) > 0:
            # 获取第一个field的DataFrame来确定日期列
            first_field = list(data.keys())[0]
            first_df = data[first_field]
            
            if hasattr(first_df, 'columns') and hasattr(first_df, 'index'):
                # 获取股票代码（index的第一个值）
                stock_code = first_df.index[0] if len(first_df.index) > 0 else None
                if not stock_code:
                    return []
                
                # 获取所有日期（DataFrame的列）
                dates = list(first_df.columns)
                print(f"   处理股票: {stock_code}, 日期数: {len(dates)}")
                
                # 遍历每个日期，构建记录
                for date in dates:
                    record = {}
                    
                    # 添加时间字段
                    if 'time' in data:
                        time_value = data['time'].loc[stock_code, date]
                        # 时间戳转换为日期字符串
                        if isinstance(time_value, (int, float)) and time_value > 1000000000000:  # 毫秒时间戳
                            from datetime import datetime
                            record['time'] = datetime.fromtimestamp(time_value / 1000).strftime('%Y%m%d')
                        else:
                            record['time'] = str(date)
                    else:
                        record['time'] = str(date)
                    
                    # 添加其他字段
                    for field in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                        if field in data:
                            try:
                                value = data[field].loc[stock_code, date]
                                # 转换为Python原生类型
                                if hasattr(value, 'item'):  # numpy类型
                                    if field == 'volume':
                                        record[field] = int(value)
                                    else:
                                        record[field] = float(value)
                                else:
                                    record[field] = value
                            except Exception as e:
                                print(f"   ⚠️  获取字段 {field} 失败: {e}")
                    
                    formatted_data.append(record)
                
                print(f"   ✅ 格式化完成，共 {len(formatted_data)} 条记录")
                if formatted_data:
                    print(f"   首条: {formatted_data[0]}")
                    print(f"   末条: {formatted_data[-1]}")
            else:
                print(f"   ⚠️  DataFrame格式不符合预期")
        else:
            print(f"   ⚠️  未知数据格式: {type(data)}")
        
        return formatted_data
    
    def _dataframe_to_list(self, df: Any, fields: Optional[List[str]]) -> List[Dict[str, Any]]:
        """将pandas DataFrame转换为列表"""
        try:
            # 重置索引，将时间索引变成列
            df_reset = df.reset_index()
            
            # 转换为字典列表
            records = df_reset.to_dict('records')
            
            formatted_data = []
            for record in records:
                formatted_item = {}
                
                # 处理时间字段
                if 'time' in record:
                    formatted_item['time'] = str(record['time'])
                elif 'index' in record:
                    formatted_item['time'] = str(record['index'])
                
                # 处理数据字段
                for field in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                    if field in record:
                        value = record[field]
                        # 转换为Python原生类型
                        if hasattr(value, 'item'):  # numpy类型
                            formatted_item[field] = float(value) if field != 'volume' else int(value)
                        else:
                            formatted_item[field] = value
                
                formatted_data.append(formatted_item)
            
            return formatted_data
            
        except Exception as e:
            print(f"   ❌ DataFrame转换失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _format_financial_data(self, data: Any, stock_code: str, table_name: str) -> List[Dict[str, Any]]:
        """格式化财务数据
        xtdata返回格式: {stock_code: {table_name: DataFrame}}
        """
        if not data:
            return []
        
        try:
            # 提取DataFrame
            if isinstance(data, dict):
                if stock_code in data:
                    tables = data[stock_code]
                    if isinstance(tables, dict) and table_name in tables:
                        df = tables[table_name]
                        
                        # 检查DataFrame是否为空
                        if hasattr(df, 'empty') and df.empty:
                            print(f"   ⚠️  DataFrame为空")
                            return []
                        
                        # 将DataFrame转换为字典列表
                        if hasattr(df, 'to_dict'):
                            print(f"   DataFrame形状: {df.shape}")
                            print(f"   DataFrame列: {list(df.columns) if hasattr(df, 'columns') else 'N/A'}")
                            
                            # 重置索引，将索引变成列
                            df_reset = df.reset_index()
                            records = df_reset.to_dict('records')
                            
                            formatted_data = []
                            for record in records:
                                # 保留所有字段
                                formatted_item = {}
                                for key, value in record.items():
                                    # 转换为Python原生类型
                                    if hasattr(value, 'item'):  # numpy类型
                                        formatted_item[key] = value.item()
                                    else:
                                        formatted_item[key] = value
                                formatted_data.append(formatted_item)
                            
                            return formatted_data
                        else:
                            print(f"   ⚠️  不是DataFrame: {type(df)}")
                            return []
                else:
                    print(f"   ⚠️  股票代码 {stock_code} 不在返回数据中")
                    return []
            else:
                print(f"   ⚠️  未知数据格式: {type(data)}")
                return []
                
        except Exception as e:
            print(f"   ❌ 格式化财务数据失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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
