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
from app.utils.logger import logger


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
            import time
            
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
                logger.warning("xtdata 连接超时，使用模拟数据（请检查QMT是否运行）")
                self._initialized = False
            else:
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
            XTQUANT_AVAILABLE and 
            self._initialized and 
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
                            dividend_type=request.adjust_type or "none"
                        )
                        
                        logger.debug(f"获取成功，原始数据类型: {type(data)}")
                        if hasattr(data, 'shape'):
                            logger.debug(f"数据形状: {data.shape}")
                        
                        # 打印原始数据结构用于调试
                        if isinstance(data, dict):
                            logger.debug(f"数据字典keys: {list(data.keys())}")
                            for k, v in data.items():
                                logger.debug(f"[{k}] 类型: {type(v)}, 形状: {v.shape if hasattr(v, 'shape') else 'N/A'}")
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
