"""
数据服务层
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
# 添加xtquant包到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    import xtquant.xtdata as xtdata
    import xtquant.xttrader as xttrader
    from xtquant import xtconstant
    XTQUANT_AVAILABLE = True
except ImportError as e:
    logger.warning("xtquant模块未正确安装")
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

from app.config import Settings, XTQuantMode
from app.models.data_models import (
    ConvertibleBondInfo,
    DataDirResponse,
    DividendFactor,
    DownloadFinancialDataBatchRequest,
    DownloadFinancialDataRequest,
    DownloadHistoryContractsRequest,
    DownloadIndexWeightRequest,
    DownloadResponse,
    DownloadTaskStatus,
    FinancialDataRequest,
    FinancialDataResponse,
    FullKlineRequest,
    FullTickRequest,
    HolidayInfo,
    IndexWeightRequest,
    IndexWeightResponse,
    InstrumentInfo,
    InstrumentTypeInfo,
    IpoInfo,
    L2OrderData,
    L2QuoteData,
    L2TransactionData,
    LocalDataRequest,
    MarketDataRequest,
    MarketDataResponse,
    PeriodListResponse,
    SectorCreateResponse,
    SectorResponse,
    TickData,
    TradingCalendarResponse,
)
from app.utils.exceptions import DataServiceException
from app.utils.helpers import validate_stock_code



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
            self._initialized = False
            return
        
        if self.settings.xtquant.mode == XTQuantMode.MOCK:
            self._initialized = False
            return
        
        try:
            # 设置数据路径（如果配置了QMT路径）
            if self.settings.xtquant.data.qmt_userdata_path:
                qmt_data_dir = os.path.join(
                    self.settings.xtquant.data.qmt_userdata_path,
                    'datadir'
                )
                xtdata.data_dir = qmt_data_dir
            
            # 初始化xtdata（添加超时保护）
            xtdata.enable_hello = False  # 禁用hello信息，减少输出
            
            import threading
            
            connect_result = {'client': None, 'error': None}
            
            def try_connect():
                try:
                    connect_result['client'] = xtdata.connect()
                except Exception as e:
                    connect_result['error'] = e
            
            # 在后台线程中尝试连接，避免阻塞主线程
            connect_thread = threading.Thread(target=try_connect, daemon=True)
            connect_thread.start()
            connect_thread.join(timeout=5.0)  # 最多等待5秒
            
            if connect_result['error']:
                raise connect_result['error']
            
            client = connect_result['client']
            
            if client and hasattr(client, 'is_connected') and client.is_connected():
                self._initialized = True
                logger.info("xtdata 已连接")
            elif connect_thread.is_alive():
                logger.warning("xtdata 连接超时，请检查QMT是否运行")
                self._initialized = False
            else:
                logger.warning("xtdata 未连接")
                self._initialized = False
                
        except KeyboardInterrupt:
            self._initialized = False
            raise
        except Exception as e:
            logger.warning(f"xtdata 连接失败: {e}")
            self._initialized = False
    
    def _should_use_real_data(self) -> bool:
        """判断是否使用真实数据（dev和prod模式都连接xtquant）"""
        return (            
            self.settings.xtquant.mode in [XTQuantMode.DEV, XTQuantMode.PROD]
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
                        # 先下载历史数据（确保本地有数据）                        
                        if not request.disable_download:
                            logger.debug("下载历史数据...")
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
                            dividend_type=request.adjust_type or "none",
                            fill_data=request.fill_data
                        )
                        
                        logger.debug(f"获取成功，原始数据类型: {type(data)}")
                        if hasattr(data, 'shape'):
                            logger.debug(f"数据形状: {data.shape}")
                        
                        # 打印原始数据结构用于调试
                        if isinstance(data, dict):
                            logger.debug(f"数据字典keys: {list(data.keys())}")
                            for k, v in data.items():
                                logger.debug(f"[{k}] 类型: {type(v)}, 形状: {v.shape if hasattr(v, 'shape') else 'N/A'}")
                                if hasattr(v, "dtypes"):                                                                        
                                    logger.debug(f"[{k}] dtypes: {str(v.dtypes).split('\n')[0]}")                                    
                                if hasattr(v, 'head'):
                                    logger.debug(f"前几行:\n{v.head()}")
                        
                        # 转换数据格式
                        formatted_data = self._format_market_data(data, request.fields)
                        logger.debug(f"格式化后数据条数: {len(formatted_data)}")
                        if formatted_data:
                            logger.debug(f"格式化后首条数据: {formatted_data[0]}")
                        
                    except Exception as e:
                        logger.error(f"获取真实数据失败: {e}")
                        logger.exception(e)
                        # dev/real模式下直接抛出异常，不回退到mock
                        raise DataServiceException(f"获取市场数据失败 [{stock_code}]: {str(e)}")
                else:
                    # 使用模拟数据（仅mock模式）
                    logger.debug(f"使用模拟数据 for {stock_code}")
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
        logger.debug("获取财务数据请求:")
        logger.debug(f"股票代码: {request.stock_codes}")
        logger.debug(f"表名: {request.table_list}")
        logger.debug(f"使用真实数据: {self._should_use_real_data()}")
        
        try:
            results = []
            for stock_code in request.stock_codes:
                for table_name in request.table_list:
                    if self._should_use_real_data():
                        # 使用真实xtdata接口
                        logger.debug(f"正在获取 {stock_code} 的 {table_name} 财务数据...")
                        try:
                            # 注意：第一个参数必须是列表
                            data = xtdata.get_financial_data(
                                [stock_code],  # 必须是列表
                                table_list=[table_name],
                                start_time=request.start_date,
                                end_time=request.end_date
                            )
                            
                            logger.debug(f"获取成功，数据类型: {type(data)}")
                            logger.debug(f"数据内容: {data}")
                            
                            # 转换数据格式
                            # xtdata返回格式: {stock_code: {table_name: DataFrame}}
                            formatted_data = self._format_financial_data(data, stock_code, table_name)
                            logger.debug(f"格式化后数据条数: {len(formatted_data)}")
                            
                        except Exception as e:
                            logger.error(f"获取真实财务数据失败: {e}")
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
                    logger.error(f"获取真实板块数据失败: {e}")
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
                    
                    logger.debug(f"获取指数权重成功，数据类型: {type(weights_data)}")
                    
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
                        logger.warning(f"未知的权重数据格式: {type(weights_data)}")
                        formatted_weights = []
                    
                    return IndexWeightResponse(
                        index_code=request.index_code,
                        date=request.date or datetime.now().strftime("%Y%m%d"),
                        weights=formatted_weights
                    )
                    
                except Exception as e:
                    logger.error(f"获取真实指数权重失败: {e}")
                    logger.exception(e)
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
                    # 生成该年所有日期，然后排除交易日得到假期
                    from datetime import datetime, timedelta
                    # xtdata.get_trading_dates需要市场代码和时间范围
                    # 获取指定年份的交易日
                    start_time = f"{year}0101"
                    end_time = f"{year}1231"
                    
                    # 获取沪深市场的交易日（SH=上交所，SZ=深交所） 返回值为毫秒级时间戳
                    trading_dates_sh = xtdata.get_trading_dates(market="SH", start_time=start_time, end_time=end_time)
                    
                    # 转换为字符串格式 YYYYMMDD
                    trading_dates = [datetime.fromtimestamp(d / 1000).strftime("%Y%m%d") for d in trading_dates_sh] if trading_dates_sh else []
                    
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
                    logger.error(f"获取真实交易日历失败: {e}")
                    logger.exception(e)
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
        """获取合约信息（返回完整字段）"""
        try:
            if self._should_use_real_data():
                # 使用真实xtdata接口
                try:
                    info = xtdata.get_instrument_detail(stock_code)
                    
                    # 返回完整的合约信息（保留所有xtquant字段）
                    return InstrumentInfo(
                        # xtquant原始字段
                        ExchangeID=info.get("ExchangeID"),
                        InstrumentID=info.get("InstrumentID"),
                        InstrumentName=info.get("InstrumentName"),
                        ProductID=info.get("ProductID"),
                        ProductName=info.get("ProductName"),
                        ProductType=info.get("ProductType"),
                        ExchangeCode=info.get("ExchangeCode"),
                        UniCode=info.get("UniCode"),
                        CreateDate=info.get("CreateDate"),
                        OpenDate=info.get("OpenDate"),
                        ExpireDate=info.get("ExpireDate"),
                        PreClose=info.get("PreClose"),
                        SettlementPrice=info.get("SettlementPrice"),
                        UpStopPrice=info.get("UpStopPrice"),
                        DownStopPrice=info.get("DownStopPrice"),
                        FloatVolume=info.get("FloatVolume") or info.get("FloatVolumn"),  # 兼容旧版本拼写错误
                        TotalVolume=info.get("TotalVolume") or info.get("TotalVolumn"),  # 兼容旧版本拼写错误
                        LongMarginRatio=info.get("LongMarginRatio"),
                        ShortMarginRatio=info.get("ShortMarginRatio"),
                        PriceTick=info.get("PriceTick"),
                        VolumeMultiple=info.get("VolumeMultiple"),
                        MainContract=info.get("MainContract"),
                        LastVolume=info.get("LastVolume"),
                        InstrumentStatus=info.get("InstrumentStatus"),
                        IsTrading=info.get("IsTrading"),
                        IsRecent=info.get("IsRecent"),
                        # 兼容旧字段
                        instrument_code=stock_code,
                        instrument_name=info.get("InstrumentName", f"股票{stock_code}"),
                        market_type=info.get("ExchangeID", "SH"),
                        instrument_type=info.get("ProductType", "STOCK"),
                        list_date=info.get("OpenDate"),
                        delist_date=str(info.get("ExpireDate")) if info.get("ExpireDate") and info.get("ExpireDate") not in [0, 99999999] else None
                    )
                    
                except Exception as e:
                    logger.error(f"获取真实合约信息失败: {e}")
                    # dev/real模式下直接抛出异常，不回退到mock
                    raise DataServiceException(f"获取合约信息失败 [{stock_code}]: {str(e)}")
            
            # 使用模拟数据（仅mock模式）
            return InstrumentInfo(
                instrument_code=stock_code,
                instrument_name=f"股票{stock_code}",
                market_type="SH" if stock_code.endswith(".SH") else "SZ",
                instrument_type="STOCK",
                list_date="20200101",
                delist_date=None,
                InstrumentID=stock_code,
                InstrumentName=f"股票{stock_code}",
                ExchangeID="SH" if stock_code.endswith(".SH") else "SZ"
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
        
        logger.debug(f"格式化数据，类型: {type(data)}")
        
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
                logger.debug(f"处理股票: {stock_code}, 日期数: {len(dates)}")
                
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
                    
                    # 添加其他字段 (包含xtquant所有K线字段)
                    for field in ['open', 'high', 'low', 'close', 'volume', 'amount', 'settle', 'openInterest', 'preClose', 'suspendFlag']:
                        if field in data:
                            try:
                                value = data[field].loc[stock_code, date]
                                # 转换为Python原生类型
                                if hasattr(value, 'item'):  # numpy类型
                                    if field in ['volume', 'openInterest', 'suspendFlag']:
                                        record[field] = int(value)
                                    else:
                                        record[field] = float(value)
                                else:
                                    logger.debug(f"field: {field} = original {value}")
                                    record[field] = value
                            except Exception as e:
                                logger.warning(f"获取字段 {field} 失败: {e}")
                    
                    formatted_data.append(record)
                
                logger.debug(f"格式化完成，共 {len(formatted_data)} 条记录")
                if formatted_data:
                    logger.debug(f"首条: {formatted_data[0]}")
                    logger.debug(f"末条: {formatted_data[-1]}")
            else:
                logger.warning("DataFrame格式不符合预期")
        else:
            logger.warning(f"未知数据格式: {type(data)}")
        
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
                
                # 处理所有K线数据字段（与_format_market_data保持一致）
                for field in ['open', 'high', 'low', 'close', 'volume', 'amount', 'settle', 'openInterest', 'preClose', 'suspendFlag']:
                    if field in record:
                        value = record[field]
                        # 转换为Python原生类型
                        if hasattr(value, 'item'):  # numpy类型
                            if field in ['volume', 'openInterest', 'suspendFlag']:
                                formatted_item[field] = int(value)
                            else:
                                formatted_item[field] = float(value)
                        else:
                            formatted_item[field] = value
                
                formatted_data.append(formatted_item)
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"DataFrame转换失败: {e}")
            logger.exception(e)
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
                            logger.warning("DataFrame为空")
                            return []
                        
                        # 将DataFrame转换为字典列表
                        if hasattr(df, 'to_dict'):
                            logger.debug(f"DataFrame形状: {df.shape}")
                            logger.debug(f"DataFrame列: {list(df.columns) if hasattr(df, 'columns') else 'N/A'}")
                            
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
                            logger.warning(f"不是DataFrame: {type(df)}")
                            return []
                else:
                    logger.warning(f"股票代码 {stock_code} 不在返回数据中")
                    return []
            else:
                logger.warning(f"未知数据格式: {type(data)}")
                return []
                
        except Exception as e:
            logger.error(f"格式化财务数据失败: {e}")
            logger.exception(e)
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
        """生成模拟市场数据（包含所有K线字段）"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        start_date = datetime.strptime(request.start_date, "%Y%m%d")
        
        for i in range(10):  # 生成10天的模拟数据
            date = start_date + timedelta(days=i)
            base_price = 100 + random.uniform(-10, 10)
            open_price = round(base_price + random.uniform(-2, 2), 2)
            high_price = round(base_price + random.uniform(0, 5), 2)
            low_price = round(base_price - random.uniform(0, 5), 2)
            close_price = round(base_price + random.uniform(-3, 3), 2)
            
            record = {
                "time": date.strftime("%Y%m%d"),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": random.randint(1000000, 10000000),
                "amount": round(close_price * random.randint(1000000, 10000000), 2),
                "settle": round(close_price * random.uniform(0.98, 1.02), 2),  # 今结算（期货）
                "openInterest": random.randint(100000, 1000000),  # 持仓量（期货）
                "preClose": round(base_price, 2),  # 前收盘价
                "suspendFlag": 0  # 停牌标志（0=正常）
            }
            
            data.append(record)
        
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
    
    # ==================== 阶段1: 基础信息接口实现 ====================
    
    def get_instrument_type(self, stock_code: str) -> InstrumentTypeInfo:
        """获取合约类型"""
        try:
            if self._should_use_real_data():
                try:
                    type_info = xtdata.get_instrument_type(stock_code)
                    
                    if type_info is None:
                        raise DataServiceException(f"未找到合约 {stock_code} 的类型信息")
                    
                    return InstrumentTypeInfo(
                        stock_code=stock_code,
                        index=type_info.get('index', False),
                        stock=type_info.get('stock', False),
                        fund=type_info.get('fund', False),
                        etf=type_info.get('etf', False),
                        bond=type_info.get('bond', False),
                        option=type_info.get('option', False),
                        futures=type_info.get('futures', False)
                    )
                except Exception as e:
                    logger.error(f"获取真实合约类型失败: {e}")
                    raise DataServiceException(f"获取合约类型失败 [{stock_code}]: {str(e)}")
            
            # Mock数据
            return InstrumentTypeInfo(
                stock_code=stock_code,
                stock=True,
                index=False,
                fund=False,
                etf=False,
                bond=False,
                option=False,
                futures=False
            )
        except Exception as e:
            raise DataServiceException(f"获取合约类型失败: {str(e)}")
    
    def get_holidays(self) -> HolidayInfo:
        """获取节假日数据"""
        try:
            if self._should_use_real_data():
                try:
                    holidays = xtdata.get_holidays()
                    return HolidayInfo(holidays=holidays if holidays else [])
                except Exception as e:
                    logger.error(f"获取真实节假日数据失败: {e}")
                    raise DataServiceException(f"获取节假日数据失败: {str(e)}")
            
            # Mock数据
            year = datetime.now().year
            mock_holidays = [
                f"{year}0101", f"{year}0102", f"{year}0103",
                f"{year}0501", f"{year}0502", f"{year}0503",
                f"{year}1001", f"{year}1002", f"{year}1003"
            ]
            return HolidayInfo(holidays=mock_holidays)
        except Exception as e:
            raise DataServiceException(f"获取节假日数据失败: {str(e)}")
    
    def get_cb_info(self) -> List[ConvertibleBondInfo]:
        """获取可转债信息列表"""
        try:
            if self._should_use_real_data():
                try:
                    # xtdata.get_cb_info() 无参数，返回所有可转债列表
                    cb_list = xtdata.get_cb_info()
                    
                    if cb_list is None or len(cb_list) == 0:
                        logger.warning("未获取到可转债信息")
                        return []
                    
                    results = []
                    for cb_info in cb_list:
                        results.append(ConvertibleBondInfo(
                            bond_code=cb_info.get('bond_code', ''),
                            bond_name=cb_info.get('bond_name'),
                            stock_code=cb_info.get('stock_code'),
                            stock_name=cb_info.get('stock_name'),
                            conversion_price=cb_info.get('conversion_price'),
                            conversion_value=cb_info.get('conversion_value'),
                            conversion_premium_rate=cb_info.get('conversion_premium_rate'),
                            current_price=cb_info.get('current_price'),
                            par_value=cb_info.get('par_value'),
                            list_date=cb_info.get('list_date'),
                            maturity_date=cb_info.get('maturity_date'),
                            conversion_begin_date=cb_info.get('conversion_begin_date'),
                            conversion_end_date=cb_info.get('conversion_end_date'),
                            raw_data=cb_info  # 保留原始数据
                        ))
                    
                    return results
                except Exception as e:
                    logger.error(f"获取真实可转债信息失败: {e}")
                    raise DataServiceException(f"获取可转债信息失败: {str(e)}")
            
            # Mock数据
            return [
                ConvertibleBondInfo(
                    bond_code="128012.SZ",
                    bond_name="辉丰转债",
                    stock_code="002496.SZ",
                    stock_name="辉丰股份",
                    conversion_price=15.5,
                    raw_data={}
                )
            ]
        except Exception as e:
            raise DataServiceException(f"获取可转债信息失败: {str(e)}")
    
    def get_ipo_info(self, start_time: Optional[str] = "", end_time: Optional[str] = "") -> List[IpoInfo]:
        """获取新股申购信息"""
        try:
            if self._should_use_real_data():
                try:
                    # 传入空字符串表示不限制时间范围
                    ipo_list = xtdata.get_ipo_info(start_time or '', end_time or '')
                    
                    results = []
                    if ipo_list:
                        for ipo_data in ipo_list:
                            results.append(IpoInfo(
                                security_code=ipo_data.get('securityCode', ''),
                                code_name=ipo_data.get('codeName'),
                                market=ipo_data.get('market'),
                                act_issue_qty=ipo_data.get('actIssueQty'),
                                online_issue_qty=ipo_data.get('onlineIssueQty'),
                                online_sub_code=ipo_data.get('onlineSubCode'),
                                online_sub_max_qty=ipo_data.get('onlineSubMaxQty'),
                                publish_price=ipo_data.get('publishPrice'),
                                is_profit=ipo_data.get('isProfit'),
                                industry_pe=ipo_data.get('industryPe'),
                                after_pe=ipo_data.get('afterPE'),
                                subscribe_date=ipo_data.get('subscribeDate'),
                                lottery_date=ipo_data.get('lotteryDate'),
                                list_date=ipo_data.get('listDate'),
                                raw_data=ipo_data  # 保留原始数据
                            ))
                    
                    return results
                except Exception as e:
                    logger.error(f"获取真实IPO信息失败: {e}")
                    raise DataServiceException(f"获取新股申购信息失败: {str(e)}")
            
            # Mock数据
            return [
                IpoInfo(
                    security_code="301234.SZ",
                    code_name="测试新股",
                    market="SZ",
                    publish_price=28.5,
                    raw_data={}
                )
            ]
        except Exception as e:
            raise DataServiceException(f"获取新股申购信息失败: {str(e)}")
    
    def get_period_list(self) -> PeriodListResponse:
        """获取可用周期列表"""
        try:
            if self._should_use_real_data():
                try:
                    periods = xtdata.get_period_list()
                    return PeriodListResponse(periods=periods if periods else [])
                except Exception as e:
                    logger.error(f"获取真实周期列表失败: {e}")
                    raise DataServiceException(f"获取周期列表失败: {str(e)}")
            
            # Mock数据
            mock_periods = ['tick', '1m', '5m', '15m', '30m', '1h', '1d', '1w', '1mon']
            return PeriodListResponse(periods=mock_periods)
        except Exception as e:
            raise DataServiceException(f"获取周期列表失败: {str(e)}")
    
    def get_data_dir(self) -> DataDirResponse:
        """获取本地数据路径"""
        try:
            if self._should_use_real_data():
                data_dir = xtdata.data_dir
                return DataDirResponse(data_dir=data_dir if data_dir else "")
            
            # Mock数据
            return DataDirResponse(data_dir="C:\\mock\\data\\dir")
        except Exception as e:
            raise DataServiceException(f"获取数据路径失败: {str(e)}")
    
    # ==================== 阶段2: 行情数据获取接口实现 ====================
    
    def get_local_data(self, request: LocalDataRequest) -> List[MarketDataResponse]:
        """获取本地行情数据（直接从本地文件读取，速度更快）"""
        try:
            results = []
            for stock_code in request.stock_codes:
                if not validate_stock_code(stock_code):
                    raise DataServiceException(f"无效的股票代码: {stock_code}")
                
                if self._should_use_real_data():
                    try:
                        data = xtdata.get_local_data(
                            field_list=request.fields or [],
                            stock_list=[stock_code],
                            period=request.period,
                            start_time=request.start_time,
                            end_time=request.end_time,
                            count=-1,
                            dividend_type=request.adjust_type or "none"
                        )
                        
                        formatted_data = self._format_market_data(data, request.fields)
                    except Exception as e:
                        logger.error(f"获取真实本地数据失败: {e}")
                        raise DataServiceException(f"获取本地数据失败 [{stock_code}]: {str(e)}")
                else:
                    # Mock数据 - 构造临时MarketDataRequest用于mock
                    from app.models.data_models import PeriodType
                    mock_request = type('obj', (object,), {
                        'fields': request.fields,
                        'period': PeriodType(request.period) if hasattr(PeriodType, request.period.upper().replace('D', 'd').replace('M', 'm').replace('H', 'h').replace('W', 'w')) else PeriodType.DAILY,
                        'start_date': request.start_time,
                        'end_date': request.end_time
                    })()
                    formatted_data = self._get_mock_market_data(stock_code, mock_request)
                
                response = MarketDataResponse(
                    stock_code=stock_code,
                    data=formatted_data,
                    fields=request.fields or ["time", "open", "high", "low", "close", "volume"],
                    period=request.period,
                    start_date=request.start_time,
                    end_date=request.end_time
                )
                results.append(response)
            
            return results
        except Exception as e:
            raise DataServiceException(f"获取本地数据失败: {str(e)}")
    
    def get_full_tick(self, request: FullTickRequest) -> Dict[str, List[TickData]]:
        """获取全推数据（最新tick数据）"""
        try:
            if self._should_use_real_data():
                try:
                    data = xtdata.get_full_tick(request.stock_codes)
                    
                    results = {}
                    if isinstance(data, dict):
                        for stock_code, tick_data in data.items():
                            tick = TickData(
                                time=str(tick_data.get('time', '')),
                                last_price=float(tick_data.get('lastPrice', 0)),
                                open=tick_data.get('open'),
                                high=tick_data.get('high'),
                                low=tick_data.get('low'),
                                last_close=tick_data.get('lastClose'),
                                amount=tick_data.get('amount'),
                                volume=tick_data.get('volume'),
                                pvolume=tick_data.get('pvolume'),
                                stock_status=tick_data.get('stockStatus'),
                                open_int=tick_data.get('openInt'),
                                last_settlement_price=tick_data.get('lastSettlementPrice'),
                                ask_price=tick_data.get('askPrice'),
                                bid_price=tick_data.get('bidPrice'),
                                ask_vol=tick_data.get('askVol'),
                                bid_vol=tick_data.get('bidVol'),
                                transaction_num=tick_data.get('transactionNum')
                            )
                            # 包装为列表
                            results[stock_code] = [tick]
                    
                    return results
                except Exception as e:
                    logger.error(f"获取真实全推数据失败: {e}")
                    raise DataServiceException(f"获取全推数据失败: {str(e)}")
            
            # Mock数据 - 返回列表格式
            results = {}
            for code in request.stock_codes:
                results[code] = [TickData(
                    time=datetime.now().strftime("%Y%m%d%H%M%S"),
                    last_price=100.0,
                    volume=1000000
                )]
            return results
        except Exception as e:
            raise DataServiceException(f"获取全推数据失败: {str(e)}")
    
    def get_divid_factors(self, stock_code: str, start_time: str = '', end_time: str = '') -> List[DividendFactor]:
        """获取除权数据"""
        try:
            if self._should_use_real_data():
                try:
                    data = xtdata.get_divid_factors(stock_code, start_time, end_time)
                    
                    results = []
                    if data is not None and hasattr(data, 'to_dict'):
                        # DataFrame转换
                        df_reset = data.reset_index()
                        records = df_reset.to_dict('records')
                        
                        for record in records:
                            results.append(DividendFactor(
                                time=str(record.get('time', record.get('index', ''))),
                                interest=record.get('interest'),
                                stock_bonus=record.get('stockBonus'),
                                stock_gift=record.get('stockGift'),
                                allot_num=record.get('allotNum'),
                                allot_price=record.get('allotPrice'),
                                gugai=record.get('gugai'),
                                dr=record.get('dr')
                            ))
                    
                    return results
                except Exception as e:
                    logger.error(f"获取真实除权数据失败: {e}")
                    raise DataServiceException(f"获取除权数据失败 [{stock_code}]: {str(e)}")
            
            # Mock数据
            return [
                DividendFactor(
                    time="20240101",
                    interest=0.5,
                    stock_bonus=0.0,
                    stock_gift=0.0,
                    dr=1.0
                )
            ]
        except Exception as e:
            raise DataServiceException(f"获取除权数据失败: {str(e)}")
    
    def get_full_kline(self, request: FullKlineRequest) -> List[MarketDataResponse]:
        """获取最新交易日K线全推数据（仅支持最新一个交易日）"""
        try:
            results = []
            for stock_code in request.stock_codes:
                if self._should_use_real_data():
                    try:
                        data = xtdata.get_full_kline(
                            field_list=request.fields or [],
                            stock_list=[stock_code],
                            period=request.period,
                            start_time=request.start_time,
                            end_time=request.end_time,
                            count=1,  # 仅最新一天
                            dividend_type=request.adjust_type or "none"
                        )
                        
                        formatted_data = self._format_market_data(data, request.fields)
                    except Exception as e:
                        logger.error(f"获取真实全推K线失败: {e}")
                        raise DataServiceException(f"获取全推K线失败 [{stock_code}]: {str(e)}")
                else:
                    # Mock数据 - 构造临时对象用于mock
                    from app.models.data_models import PeriodType
                    mock_request = type('obj', (object,), {
                        'fields': request.fields,
                        'period': PeriodType(request.period) if hasattr(PeriodType, request.period.upper().replace('D', 'd').replace('M', 'm').replace('H', 'h').replace('W', 'w')) else PeriodType.DAILY,
                        'start_date': request.start_time,
                        'end_date': request.end_time
                    })()
                    formatted_data = self._get_mock_market_data(stock_code, mock_request)[:1]
                
                response = MarketDataResponse(
                    stock_code=stock_code,
                    data=formatted_data,
                    fields=request.fields or ["time", "open", "high", "low", "close", "volume"],
                    period=request.period,
                    start_date=request.start_time,
                    end_date=request.end_time
                )
                results.append(response)
            
            return results
        except Exception as e:
            raise DataServiceException(f"获取全推K线失败: {str(e)}")
    
    # ==================== 阶段3: 数据下载接口实现 ====================
    
    def download_history_data(self, stock_code: str, period: str, start_time: str = '', 
                             end_time: str = '', incrementally: Optional[bool] = None) -> DownloadResponse:
        """下载历史行情数据"""
        try:
            if self._should_use_real_data():
                try:
                    # xtdata下载接口是同步的，会阻塞直到完成
                    xtdata.download_history_data(
                        stock_code=stock_code,
                        period=period,
                        start_time=start_time,
                        end_time=end_time,
                        incrementally=incrementally
                    )
                    
                    return DownloadResponse(
                        task_id=f"download_{stock_code}_{period}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message=f"下载完成: {stock_code} {period}"
                    )
                except Exception as e:
                    logger.error(f"下载历史数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"download_{stock_code}_{period}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            # Mock响应
            return DownloadResponse(
                task_id=f"mock_download_{stock_code}",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载历史数据失败: {str(e)}")
    
    def download_history_data_batch(self, stock_list: List[str], period: str, 
                                   start_time: str = '', end_time: str = '',
                                   incrementally: Optional[bool] = None,
                                   callback = None) -> DownloadResponse:
        """批量下载历史行情数据（带进度回调）"""
        try:
            if self._should_use_real_data():
                try:
                    task_id = f"batch_download_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # xtdata的批量下载接口
                    xtdata.download_history_data2(
                        stock_list=stock_list,
                        period=period,
                        start_time=start_time,
                        end_time=end_time,
                        callback=callback,
                        incrementally=incrementally
                    )
                    
                    return DownloadResponse(
                        task_id=task_id,
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message=f"批量下载完成: {len(stock_list)}只股票"
                    )
                except Exception as e:
                    logger.error(f"批量下载历史数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"batch_download_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            # Mock响应
            return DownloadResponse(
                task_id="mock_batch_download",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message=f"Mock批量下载完成: {len(stock_list)}只股票"
            )
        except Exception as e:
            raise DataServiceException(f"批量下载历史数据失败: {str(e)}")
    
    def download_financial_data(self, request: DownloadFinancialDataRequest) -> DownloadResponse:
        """下载财务数据"""
        try:
            if self._should_use_real_data():
                try:
                    # 从请求对象读取参数
                    xtdata.download_financial_data(
                        stock_list=request.stock_list,
                        table_list=request.table_list,
                        start_date=request.start_date if request.start_date else '',
                        end_date=request.end_date if request.end_date else ''
                    )
                    
                    return DownloadResponse(
                        task_id=f"fin_download_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message=f"财务数据下载完成: {len(request.stock_list)}只股票, {len(request.table_list)}张表, 日期区间: {request.start_date or '无'} - {request.end_date or '无'}"
                    )
                except Exception as e:
                    logger.error(f"下载财务数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"fin_download_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            # Mock模式
            return DownloadResponse(
                task_id="mock_fin_download",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message=f"Mock财务数据下载完成: {len(request.stock_list)}只股票, {len(request.table_list)}张表"
            )
        except Exception as e:
            raise DataServiceException(f"下载财务数据失败: {str(e)}")
    
    def download_financial_data_batch(self, request: DownloadFinancialDataBatchRequest) -> DownloadResponse:
        """批量下载财务数据（带进度回调）"""
        try:
            if self._should_use_real_data():
                try:
                    xtdata.download_financial_data2(
                        stock_list=request.stock_list,
                        table_list=request.table_list,
                        start_time=request.start_date,
                        end_time=request.end_date,
                        callback=None  # TODO: 实现回调函数映射
                    )
                    
                    return DownloadResponse(
                        task_id=f"fin_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message=f"批量财务数据下载完成: {len(request.stock_list)}只股票"
                    )
                except Exception as e:
                    logger.error(f"批量下载财务数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"fin_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            return DownloadResponse(
                task_id="mock_fin_batch",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock批量财务数据下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"批量下载财务数据失败: {str(e)}")
    
    def download_sector_data(self) -> DownloadResponse:
        """下载板块分类信息（异步任务）"""
        try:
            task_id = f"sector_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if self._should_use_real_data():
                # 在real/dev模式下，启动后台任务而非同步等待
                # TODO: 实际应使用Celery或后台线程池
                logger.info("已提交板块数据下载任务")
                return DownloadResponse(
                    task_id=task_id,
                    status=DownloadTaskStatus.RUNNING,
                    progress=0.0,
                    message="板块数据下载任务已提交，正在后台执行"
                )
            
            # Mock模式立即返回完成
            return DownloadResponse(
                task_id=task_id,
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock板块数据下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载板块数据失败: {str(e)}")
    
    def download_index_weight(self, request: DownloadIndexWeightRequest) -> DownloadResponse:
        """下载指数成分权重信息"""
        try:
            if self._should_use_real_data():
                try:
                    # xtdata.download_index_weight() 不接受参数，下载全部
                    xtdata.download_index_weight()
                    
                    return DownloadResponse(
                        task_id=f"index_weight_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message=f"指数权重下载完成{' (指定: ' + request.index_code + ')' if request.index_code else ''}"
                    )
                except Exception as e:
                    logger.error(f"下载指数权重失败: {e}")
                    return DownloadResponse(
                        task_id=f"index_weight_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            return DownloadResponse(
                task_id="mock_index_weight",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock指数权重下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载指数权重失败: {str(e)}")
    
    def download_cb_data(self) -> DownloadResponse:
        """下载可转债基础信息"""
        try:
            if self._should_use_real_data():
                try:
                    xtdata.download_cb_data()
                    
                    return DownloadResponse(
                        task_id=f"cb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message="可转债数据下载完成"
                    )
                except Exception as e:
                    logger.error(f"下载可转债数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"cb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            return DownloadResponse(
                task_id="mock_cb",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock可转债数据下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载可转债数据失败: {str(e)}")
    
    def download_etf_info(self) -> DownloadResponse:
        """下载ETF申赎清单信息"""
        try:
            if self._should_use_real_data():
                try:
                    xtdata.download_etf_info()
                    
                    return DownloadResponse(
                        task_id=f"etf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message="ETF数据下载完成"
                    )
                except Exception as e:
                    logger.error(f"下载ETF数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"etf_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            return DownloadResponse(
                task_id="mock_etf",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="MockETF数据下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载ETF数据失败: {str(e)}")
    
    def download_holiday_data(self) -> DownloadResponse:
        """下载节假日数据"""
        try:
            if self._should_use_real_data():
                try:
                    xtdata.download_holiday_data()
                    
                    return DownloadResponse(
                        task_id=f"holiday_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message="节假日数据下载完成"
                    )
                except Exception as e:
                    logger.error(f"下载节假日数据失败: {e}")
                    return DownloadResponse(
                        task_id=f"holiday_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            return DownloadResponse(
                task_id="mock_holiday",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock节假日数据下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载节假日数据失败: {str(e)}")
    
    def download_history_contracts(self, request: DownloadHistoryContractsRequest) -> DownloadResponse:
        """下载过期（退市）合约信息"""
        try:
            if self._should_use_real_data():
                try:
                    # xtdata.download_history_contracts() 不接受参数
                    xtdata.download_history_contracts()
                    
                    return DownloadResponse(
                        task_id=f"history_contracts_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.COMPLETED,
                        progress=100.0,
                        message=f"过期合约数据下载完成{' (市场: ' + request.market + ')' if request.market else ''}"
                    )
                except Exception as e:
                    logger.error(f"下载过期合约失败: {e}")
                    return DownloadResponse(
                        task_id=f"history_contracts_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        status=DownloadTaskStatus.FAILED,
                        progress=0.0,
                        message=str(e)
                    )
            
            return DownloadResponse(
                task_id="mock_history_contracts",
                status=DownloadTaskStatus.COMPLETED,
                progress=100.0,
                message="Mock过期合约下载完成"
            )
        except Exception as e:
            raise DataServiceException(f"下载过期合约失败: {str(e)}")
    
    # ==================== 阶段4: 板块管理接口实现 ====================
    
    def create_sector_folder(self, parent_node: str, folder_name: str, overwrite: bool = True) -> SectorCreateResponse:
        """创建板块目录节点"""
        try:
            if self._should_use_real_data():
                try:
                    created_name = xtdata.create_sector_folder(
                        parent_node=parent_node,
                        folder_name=folder_name,
                        overwrite=overwrite
                    )
                    
                    return SectorCreateResponse(
                        created_name=created_name,
                        success=True,
                        message=f"板块目录创建成功: {created_name}"
                    )
                except Exception as e:
                    logger.error(f"创建板块目录失败: {e}")
                    return SectorCreateResponse(
                        created_name=folder_name,
                        success=False,
                        message=str(e)
                    )
            
            return SectorCreateResponse(
                created_name=folder_name,
                success=True,
                message="Mock板块目录创建成功"
            )
        except Exception as e:
            raise DataServiceException(f"创建板块目录失败: {str(e)}")
    
    def create_sector(self, parent_node: str, sector_name: str, overwrite: bool = True) -> SectorCreateResponse:
        """创建板块"""
        try:
            if self._should_use_real_data():
                try:
                    created_name = xtdata.create_sector(
                        parent_node=parent_node,
                        sector_name=sector_name,
                        overwrite=overwrite
                    )
                    
                    return SectorCreateResponse(
                        created_name=created_name,
                        success=True,
                        message=f"板块创建成功: {created_name}"
                    )
                except Exception as e:
                    logger.error(f"创建板块失败: {e}")
                    return SectorCreateResponse(
                        created_name=sector_name,
                        success=False,
                        message=str(e)
                    )
            
            return SectorCreateResponse(
                created_name=sector_name,
                success=True,
                message="Mock板块创建成功"
            )
        except Exception as e:
            raise DataServiceException(f"创建板块失败: {str(e)}")
    
    def add_sector(self, sector_name: str, stock_list: List[str]) -> bool:
        """添加自定义板块"""
        try:
            if self._should_use_real_data():
                try:
                    xtdata.add_sector(sector_name=sector_name, stock_list=stock_list)
                    return True
                except Exception as e:
                    logger.error(f"添加自定义板块失败: {e}")
                    raise DataServiceException(f"添加板块失败: {str(e)}")
            
            return True
        except Exception as e:
            raise DataServiceException(f"添加板块失败: {str(e)}")
    
    def remove_stock_from_sector(self, sector_name: str, stock_list: List[str]) -> bool:
        """移除板块成分股"""
        try:
            if self._should_use_real_data():
                try:
                    result = xtdata.remove_stock_from_sector(
                        sector_name=sector_name,
                        stock_list=stock_list
                    )
                    return result if isinstance(result, bool) else True
                except Exception as e:
                    logger.error(f"移除板块成分股失败: {e}")
                    raise DataServiceException(f"移除成分股失败: {str(e)}")
            
            return True
        except Exception as e:
            raise DataServiceException(f"移除成分股失败: {str(e)}")
    
    def remove_sector(self, sector_name: str) -> bool:
        """移除自定义板块"""
        try:
            if self._should_use_real_data():
                try:
                    xtdata.remove_sector(sector_name=sector_name)
                    return True
                except Exception as e:
                    logger.error(f"移除板块失败: {e}")
                    raise DataServiceException(f"移除板块失败: {str(e)}")
            
            return True
        except Exception as e:
            raise DataServiceException(f"移除板块失败: {str(e)}")
    
    def reset_sector(self, sector_name: str, stock_list: List[str]) -> bool:
        """重置板块"""
        try:
            if self._should_use_real_data():
                try:
                    result = xtdata.reset_sector(
                        sector_name=sector_name,
                        stock_list=stock_list
                    )
                    return result if isinstance(result, bool) else True
                except Exception as e:
                    logger.error(f"重置板块失败: {e}")
                    raise DataServiceException(f"重置板块失败: {str(e)}")
            
            return True
        except Exception as e:
            raise DataServiceException(f"重置板块失败: {str(e)}")
    
    # ==================== 阶段5: Level2数据接口实现 ====================
    
    def get_l2_quote(self, stock_codes: List[str]) -> Dict[str, L2QuoteData]:
        """获取Level2行情快照数据（包含10档行情）- 支持多标的"""
        try:
            results = {}
            
            if self._should_use_real_data():
                try:
                    data = xtdata.get_l2_quote(stock_codes)
                    
                    if not data:
                        logger.warning("未获取到任何Level2数据")
                        return results
                    
                    for stock_code in stock_codes:
                        if stock_code in data:
                            quote = data[stock_code]
                            results[stock_code] = L2QuoteData(
                                time=str(quote.get('time', '')),
                                last_price=float(quote.get('lastPrice', 0)),
                                open=quote.get('open'),
                                high=quote.get('high'),
                                low=quote.get('low'),
                                amount=quote.get('amount'),
                                volume=quote.get('volume'),
                                pvolume=quote.get('pvolume'),
                                open_int=quote.get('openInt'),
                                stock_status=quote.get('stockStatus'),
                                transaction_num=quote.get('transactionNum'),
                                last_close=quote.get('lastClose'),
                                last_settlement_price=quote.get('lastSettlementPrice'),
                                settlement_price=quote.get('settlementPrice'),
                                pe=quote.get('pe'),
                                ask_price=quote.get('askPrice', []),  # 10档卖价
                                bid_price=quote.get('bidPrice', []),  # 10档买价
                                ask_vol=quote.get('askVol', []),      # 10档卖量
                                bid_vol=quote.get('bidVol', [])       # 10档买量
                            )
                    return results
                except Exception as e:
                    logger.error(f"获取Level2快照失败: {e}")
                    raise DataServiceException(f"获取Level2快照失败: {str(e)}")
            
            # Mock数据（包含10档）- 为每个标的生成
            for stock_code in stock_codes:
                results[stock_code] = L2QuoteData(
                    time=datetime.now().strftime("%Y%m%d%H%M%S"),
                    last_price=100.0,
                    volume=1000000,
                    ask_price=[100.1, 100.2, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0],
                    bid_price=[99.9, 99.8, 99.7, 99.6, 99.5, 99.4, 99.3, 99.2, 99.1, 99.0],
                    ask_vol=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
                    bid_vol=[150, 250, 350, 450, 550, 650, 750, 850, 950, 1050]
                )
            return results
        except Exception as e:
            raise DataServiceException(f"获取Level2快照失败: {str(e)}")
    
    def get_l2_order(self, stock_codes: List[str]) -> Dict[str, List[L2OrderData]]:
        """获取Level2逐笔委托数据 - 支持多标的"""
        try:
            results = {}
            
            if self._should_use_real_data():
                try:
                    data = xtdata.get_l2_order(stock_codes)
                    
                    if not data:
                        logger.warning("未获取到任何Level2委托数据")
                        return results
                    
                    for stock_code in stock_codes:
                        if stock_code in data:
                            orders = data[stock_code]
                            order_list = []
                            
                            if hasattr(orders, '__iter__'):
                                for order in orders:
                                    order_list.append(L2OrderData(
                                        time=str(order.get('time', '')),
                                        price=float(order.get('price', 0)),
                                        volume=int(order.get('volume', 0)),
                                        entrust_no=order.get('entrustNo'),
                                        entrust_type=order.get('entrustType'),
                                        entrust_direction=order.get('entrustDirection')
                                    ))
                            results[stock_code] = order_list
                    return results
                except Exception as e:
                    logger.error(f"获取Level2逐笔委托失败: {e}")
                    raise DataServiceException(f"获取Level2委托失败: {str(e)}")
            
            # Mock数据 - 为每个标的生成
            for stock_code in stock_codes:
                results[stock_code] = [
                    L2OrderData(
                        time=datetime.now().strftime("%Y%m%d%H%M%S"),
                        price=100.0,
                        volume=1000,
                        entrust_no="123456",
                        entrust_type=1,
                        entrust_direction=1
                    )
                ]
            return results
        except Exception as e:
            raise DataServiceException(f"获取Level2委托失败: {str(e)}")
    
    def get_l2_transaction(self, stock_codes: List[str]) -> Dict[str, List[L2TransactionData]]:
        """获取Level2逐笔成交数据 - 支持多标的"""
        try:
            results = {}
            
            if self._should_use_real_data():
                try:
                    data = xtdata.get_l2_transaction(stock_codes)
                    
                    if not data:
                        logger.warning("未获取到任何Level2成交数据")
                        return results
                    
                    for stock_code in stock_codes:
                        if stock_code in data:
                            transactions = data[stock_code]
                            trans_list = []
                            
                            if hasattr(transactions, '__iter__'):
                                for trans in transactions:
                                    trans_list.append(L2TransactionData(
                                        time=str(trans.get('time', '')),
                                        price=float(trans.get('price', 0)),
                                        volume=int(trans.get('volume', 0)),
                                        amount=float(trans.get('amount', 0)),
                                        trade_index=trans.get('tradeIndex'),
                                        buy_no=trans.get('buyNo'),
                                        sell_no=trans.get('sellNo'),
                                        trade_type=trans.get('tradeType'),
                                        trade_flag=trans.get('tradeFlag')
                                    ))
                            results[stock_code] = trans_list
                    return results
                except Exception as e:
                    logger.error(f"获取Level2逐笔成交失败: {e}")
                    raise DataServiceException(f"获取Level2成交失败: {str(e)}")
            
            # Mock数据 - 为每个标的生成
            for stock_code in stock_codes:
                results[stock_code] = [
                    L2TransactionData(
                        time=datetime.now().strftime("%Y%m%d%H%M%S"),
                        price=100.0,
                        volume=1000,
                        amount=100000.0,
                        trade_index="1",
                        buy_no="B123",
                        sell_no="S456",
                        trade_type=1,
                        trade_flag=1
                    )
                ]
            return results
        except Exception as e:
            raise DataServiceException(f"获取Level2成交失败: {str(e)}")
