"""
gRPC 数据服务实现
"""
import grpc
from typing import List, Dict, Any, Optional

# 导入生成的 protobuf 代码
from generated import data_pb2, data_pb2_grpc, common_pb2
from google.protobuf import empty_pb2

# 导入现有服务
from app.services.data_service import DataService
from app.models.data_models import (
    MarketDataRequest as RestMarketDataRequest,
    FinancialDataRequest as RestFinancialDataRequest,
    IndexWeightRequest as RestIndexWeightRequest,
    PeriodType
)
from app.utils.exceptions import DataServiceException


class DataGrpcService(data_pb2_grpc.DataServiceServicer):
    """gRPC 数据服务实现"""
    
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def GetMarketData(
        self, 
        request: data_pb2.MarketDataRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.MarketDataBatchResponse:
        """获取市场数据"""
        try:
            # 转换 protobuf 请求为内部模型
            rest_request = self._convert_market_data_request(request)
            
            # 调用现有服务
            results = self.data_service.get_market_data(rest_request)
            
            # 转换响应为 protobuf
            pb_responses = []
            for result in results:
                bars = []
                for item in result.data:
                    bar = data_pb2.KlineBar(
                        time=str(item.get('time', '')),
                        open=float(item.get('open', 0.0)),
                        high=float(item.get('high', 0.0)),
                        low=float(item.get('low', 0.0)),
                        close=float(item.get('close', 0.0)),
                        volume=int(item.get('volume', 0)),
                        amount=float(item.get('amount', 0.0))
                    )
                    bars.append(bar)
                
                pb_response = data_pb2.MarketDataResponse(
                    stock_code=result.stock_code,
                    bars=bars,
                    fields=result.fields,
                    period=result.period,
                    start_date=result.start_date,
                    end_date=result.end_date,
                    status=common_pb2.Status(code=0, message="success")
                )
                pb_responses.append(pb_response)
            
            return data_pb2.MarketDataBatchResponse(
                data=pb_responses,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except DataServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return data_pb2.MarketDataBatchResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.MarketDataBatchResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetFinancialData(
        self, 
        request: data_pb2.FinancialDataRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.FinancialDataBatchResponse:
        """获取财务数据"""
        try:
            # 转换请求
            rest_request = RestFinancialDataRequest(
                stock_codes=list(request.stock_codes),
                table_list=list(request.table_list),
                start_date=request.start_date if request.start_date else None,
                end_date=request.end_date if request.end_date else None
            )
            
            # 调用服务
            results = self.data_service.get_financial_data(rest_request)
            
            # 转换响应
            pb_responses = []
            for result in results:
                rows = []
                for row_data in result.data:
                    # 将字典转换为 map<string, string>
                    fields = {k: str(v) for k, v in row_data.items()}
                    row = data_pb2.FinancialDataRow(fields=fields)
                    rows.append(row)
                
                pb_response = data_pb2.FinancialDataResponse(
                    stock_code=result.stock_code,
                    table_name=result.table_name,
                    rows=rows,
                    columns=result.columns,
                    status=common_pb2.Status(code=0, message="success")
                )
                pb_responses.append(pb_response)
            
            return data_pb2.FinancialDataBatchResponse(
                data=pb_responses,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except DataServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return data_pb2.FinancialDataBatchResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.FinancialDataBatchResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetSectorList(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.SectorListResponse:
        """获取板块列表"""
        try:
            # 调用服务
            results = self.data_service.get_sector_list()
            
            # 转换响应
            sectors = []
            for result in results:
                sector = data_pb2.SectorInfo(
                    sector_name=result.sector_name,
                    stock_list=result.stock_list,
                    sector_type=result.sector_type or ""
                )
                sectors.append(sector)
            
            return data_pb2.SectorListResponse(
                sectors=sectors,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except DataServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return data_pb2.SectorListResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.SectorListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetIndexWeight(
        self, 
        request: data_pb2.IndexWeightRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.IndexWeightResponse:
        """获取指数权重"""
        try:
            # 转换请求
            rest_request = RestIndexWeightRequest(
                index_code=request.index_code,
                date=request.date if request.date else None
            )
            
            # 调用服务
            result = self.data_service.get_index_weight(rest_request)
            
            # 转换响应
            weights = []
            for weight_data in result.weights:
                weight = data_pb2.ComponentWeight(
                    stock_code=weight_data.get('stock_code', ''),
                    weight=float(weight_data.get('weight', 0.0)),
                    market_cap=float(weight_data.get('market_cap', 0.0))
                )
                weights.append(weight)
            
            return data_pb2.IndexWeightResponse(
                index_code=result.index_code,
                date=result.date,
                weights=weights,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except DataServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return data_pb2.IndexWeightResponse(
                index_code=request.index_code,
                date=request.date,
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.IndexWeightResponse(
                index_code=request.index_code,
                date=request.date,
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetTradingCalendar(
        self, 
        request: data_pb2.TradingCalendarRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.TradingCalendarResponse:
        """获取交易日历"""
        try:
            # 调用服务
            result = self.data_service.get_trading_calendar(request.year)
            
            return data_pb2.TradingCalendarResponse(
                trading_dates=result.trading_dates,
                holidays=result.holidays,
                year=result.year,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except DataServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return data_pb2.TradingCalendarResponse(
                year=request.year,
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.TradingCalendarResponse(
                year=request.year,
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetInstrumentInfo(
        self, 
        request: data_pb2.InstrumentInfoRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.InstrumentInfoResponse:
        """获取合约信息"""
        try:
            # 调用服务
            result = self.data_service.get_instrument_info(request.stock_code)
            
            return data_pb2.InstrumentInfoResponse(
                instrument_code=result.instrument_code,
                instrument_name=result.instrument_name,
                market_type=result.market_type,
                instrument_type=result.instrument_type,
                list_date=result.list_date or "",
                delist_date=result.delist_date or "",
                status=common_pb2.Status(code=0, message="success")
            )
            
        except DataServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return data_pb2.InstrumentInfoResponse(
                instrument_code=request.stock_code,
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.InstrumentInfoResponse(
                instrument_code=request.stock_code,
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetETFInfo(
        self, 
        request: data_pb2.ETFInfoRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.ETFInfoResponse:
        """获取ETF信息（占位实现）"""
        try:
            # 这是占位实现，返回模拟数据
            return data_pb2.ETFInfoResponse(
                etf_code=request.etf_code,
                etf_name=f"ETF{request.etf_code}",
                underlying_asset="沪深300",
                creation_unit=1000000,
                redemption_unit=1000000,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.ETFInfoResponse(
                etf_code=request.etf_code,
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def _convert_market_data_request(self, pb_request: data_pb2.MarketDataRequest) -> RestMarketDataRequest:
        """转换 protobuf 请求为内部模型"""
        # 周期类型映射
        period_map = {
            common_pb2.PERIOD_TYPE_TICK: PeriodType.TICK,
            common_pb2.PERIOD_TYPE_1M: PeriodType.MINUTE_1,
            common_pb2.PERIOD_TYPE_5M: PeriodType.MINUTE_5,
            common_pb2.PERIOD_TYPE_15M: PeriodType.MINUTE_15,
            common_pb2.PERIOD_TYPE_30M: PeriodType.MINUTE_30,
            common_pb2.PERIOD_TYPE_1H: PeriodType.HOUR_1,
            common_pb2.PERIOD_TYPE_1D: PeriodType.DAILY,
            common_pb2.PERIOD_TYPE_1W: PeriodType.WEEKLY,
            common_pb2.PERIOD_TYPE_1MON: PeriodType.MONTHLY,
        }
        
        return RestMarketDataRequest(
            stock_codes=list(pb_request.stock_codes),
            start_date=pb_request.start_date,
            end_date=pb_request.end_date,
            period=period_map.get(pb_request.period, PeriodType.DAILY),
            fields=list(pb_request.fields) if pb_request.fields else None,
            adjust_type=pb_request.adjust_type if pb_request.adjust_type else "none"
        )
    
    # ==================== 阶段1: 基础信息接口实现 ====================
    
    def GetInstrumentType(
        self, 
        request: data_pb2.InstrumentTypeRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.InstrumentTypeResponse:
        """获取合约类型"""
        try:
            result = self.data_service.get_instrument_type(request.stock_code)
            
            info = data_pb2.InstrumentTypeInfo(
                stock_code=result['stock_code'],
                index=result.get('index', False),
                stock=result.get('stock', False),
                fund=result.get('fund', False),
                etf=result.get('etf', False),
                bond=result.get('bond', False),
                option=result.get('option', False),
                futures=result.get('futures', False)
            )
            
            return data_pb2.InstrumentTypeResponse(
                data=info,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.InstrumentTypeResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetHolidays(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.HolidayInfoResponse:
        """获取节假日列表"""
        try:
            result = self.data_service.get_holidays()
            
            return data_pb2.HolidayInfoResponse(
                holidays=result.get('holidays', []),
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.HolidayInfoResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetConvertibleBondInfo(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.ConvertibleBondListResponse:
        """获取可转债信息"""
        try:
            results = self.data_service.get_cb_info()
            
            bonds = []
            for cb in results:
                bond = data_pb2.ConvertibleBondInfo(
                    bond_code=cb.get('bond_code', ''),
                    bond_name=cb.get('bond_name', ''),
                    stock_code=cb.get('stock_code', ''),
                    stock_name=cb.get('stock_name', ''),
                    conversion_price=cb.get('conversion_price', 0.0),
                    conversion_value=cb.get('conversion_value', 0.0),
                    conversion_premium_rate=cb.get('conversion_premium_rate', 0.0),
                    current_price=cb.get('current_price', 0.0),
                    par_value=cb.get('par_value', 0.0),
                    list_date=cb.get('list_date', ''),
                    maturity_date=cb.get('maturity_date', ''),
                    conversion_begin_date=cb.get('conversion_begin_date', ''),
                    conversion_end_date=cb.get('conversion_end_date', ''),
                    raw_data=cb.get('raw_data', {})
                )
                bonds.append(bond)
            
            return data_pb2.ConvertibleBondListResponse(
                bonds=bonds,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.ConvertibleBondListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetIpoInfo(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.IpoInfoListResponse:
        """获取新股申购信息"""
        try:
            results = self.data_service.get_ipo_info()
            
            ipos = []
            for ipo in results:
                ipo_info = data_pb2.IpoInfo(
                    security_code=ipo.get('security_code', ''),
                    code_name=ipo.get('code_name', ''),
                    market=ipo.get('market', ''),
                    act_issue_qty=ipo.get('act_issue_qty', 0),
                    online_issue_qty=ipo.get('online_issue_qty', 0),
                    online_sub_code=ipo.get('online_sub_code', ''),
                    online_sub_max_qty=ipo.get('online_sub_max_qty', 0),
                    publish_price=ipo.get('publish_price', 0.0),
                    is_profit=ipo.get('is_profit', 0),
                    industry_pe=ipo.get('industry_pe', 0.0),
                    after_pe=ipo.get('after_pe', 0.0),
                    subscribe_date=ipo.get('subscribe_date', ''),
                    lottery_date=ipo.get('lottery_date', ''),
                    list_date=ipo.get('list_date', ''),
                    raw_data=ipo.get('raw_data', {})
                )
                ipos.append(ipo_info)
            
            return data_pb2.IpoInfoListResponse(
                ipos=ipos,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.IpoInfoListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetPeriodList(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.PeriodListResponse:
        """获取可用周期列表"""
        try:
            result = self.data_service.get_period_list()
            
            return data_pb2.PeriodListResponse(
                periods=result.get('periods', []),
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.PeriodListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetDataDir(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.DataDirResponse:
        """获取本地数据路径"""
        try:
            result = self.data_service.get_data_dir()
            
            return data_pb2.DataDirResponse(
                data_dir=result.get('data_dir', ''),
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DataDirResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    # ==================== 阶段2: 行情数据获取接口实现 ====================
    
    def GetLocalData(
        self, 
        request: data_pb2.LocalDataRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.LocalDataResponse:
        """获取本地行情数据"""
        try:
            result = self.data_service.get_local_data(
                list(request.stock_codes),
                request.start_time,
                request.end_time,
                request.period
            )
            
            data_map = {}
            for stock_code, kline_data in result.items():
                bars = []
                for item in kline_data:
                    bar = data_pb2.KlineBar(
                        time=str(item.get('time', '')),
                        open=float(item.get('open', 0.0)),
                        high=float(item.get('high', 0.0)),
                        low=float(item.get('low', 0.0)),
                        close=float(item.get('close', 0.0)),
                        volume=int(item.get('volume', 0)),
                        amount=float(item.get('amount', 0.0))
                    )
                    bars.append(bar)
                data_map[stock_code] = data_pb2.KlineDataList(bars=bars)
            
            return data_pb2.LocalDataResponse(
                data=data_map,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.LocalDataResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetFullTick(
        self, 
        request: data_pb2.FullTickRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.FullTickResponse:
        """获取完整tick数据"""
        try:
            result = self.data_service.get_full_tick(
                list(request.stock_codes),
                request.start_time,
                request.end_time
            )
            
            data_map = {}
            for stock_code, tick_list in result.items():
                ticks = []
                for tick in tick_list:
                    tick_data = data_pb2.TickData(
                        time=tick.get('time', ''),
                        last_price=tick.get('last_price', 0.0),
                        open=tick.get('open', 0.0),
                        high=tick.get('high', 0.0),
                        low=tick.get('low', 0.0),
                        last_close=tick.get('last_close', 0.0),
                        amount=tick.get('amount', 0.0),
                        volume=tick.get('volume', 0),
                        pvolume=tick.get('pvolume', 0),
                        stock_status=tick.get('stock_status', 0),
                        open_int=tick.get('open_int', 0),
                        last_settlement_price=tick.get('last_settlement_price', 0.0),
                        ask_price=tick.get('ask_price', []),
                        bid_price=tick.get('bid_price', []),
                        ask_vol=tick.get('ask_vol', []),
                        bid_vol=tick.get('bid_vol', []),
                        transaction_num=tick.get('transaction_num', 0)
                    )
                    ticks.append(tick_data)
                data_map[stock_code] = data_pb2.TickDataList(ticks=ticks)
            
            return data_pb2.FullTickResponse(
                data=data_map,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.FullTickResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetDividFactors(
        self, 
        request: data_pb2.DividFactorsRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DividFactorsResponse:
        """获取除权数据"""
        try:
            result = self.data_service.get_divid_factors(request.stock_code)
            
            factors = []
            for factor in result:
                div_factor = data_pb2.DividendFactor(
                    time=factor.get('time', ''),
                    interest=factor.get('interest', 0.0),
                    stock_bonus=factor.get('stock_bonus', 0.0),
                    stock_gift=factor.get('stock_gift', 0.0),
                    allot_num=factor.get('allot_num', 0.0),
                    allot_price=factor.get('allot_price', 0.0),
                    gugai=factor.get('gugai', 0),
                    dr=factor.get('dr', 0.0)
                )
                factors.append(div_factor)
            
            return data_pb2.DividFactorsResponse(
                factors=factors,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DividFactorsResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetFullKline(
        self, 
        request: data_pb2.FullKlineRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.FullKlineResponse:
        """获取完整K线数据"""
        try:
            result = self.data_service.get_full_kline(
                list(request.stock_codes),
                request.start_time,
                request.end_time,
                request.period
            )
            
            data_map = {}
            for stock_code, kline_data in result.items():
                bars = []
                for item in kline_data:
                    bar = data_pb2.KlineBar(
                        time=str(item.get('time', '')),
                        open=float(item.get('open', 0.0)),
                        high=float(item.get('high', 0.0)),
                        low=float(item.get('low', 0.0)),
                        close=float(item.get('close', 0.0)),
                        volume=int(item.get('volume', 0)),
                        amount=float(item.get('amount', 0.0))
                    )
                    bars.append(bar)
                data_map[stock_code] = data_pb2.KlineDataList(bars=bars)
            
            return data_pb2.FullKlineResponse(
                data=data_map,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.FullKlineResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    # ==================== 阶段3: 数据下载接口实现 ====================
    
    def DownloadHistoryData(
        self, 
        request: data_pb2.DownloadHistoryDataRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载历史数据（单只）"""
        try:
            result = self.data_service.download_history_data(
                request.stock_code,
                request.period,
                request.start_time,
                request.end_time,
                request.incrementally
            )
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                current_stock=result.current_stock or '',
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadHistoryDataBatch(
        self, 
        request: data_pb2.DownloadHistoryDataBatchRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """批量下载历史数据"""
        try:
            result = self.data_service.download_history_data_batch(
                list(request.stock_list),
                request.period,
                request.start_time,
                request.end_time
            )
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                current_stock=result.current_stock or '',
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadFinancialData(
        self, 
        request: data_pb2.DownloadFinancialDataRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载财务数据"""
        try:
            result = self.data_service.download_financial_data(
                list(request.stock_list),
                list(request.table_list),
                request.start_date,
                request.end_date
            )
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadFinancialDataBatch(
        self, 
        request: data_pb2.DownloadFinancialDataRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """批量下载财务数据"""
        try:
            result = self.data_service.download_financial_data_batch(
                list(request.stock_list),
                list(request.table_list),
                request.start_date,
                request.end_date
            )
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadSectorData(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载板块数据"""
        try:
            result = self.data_service.download_sector_data()
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadIndexWeight(
        self, 
        request: data_pb2.DownloadIndexWeightRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载指数权重"""
        try:
            result = self.data_service.download_index_weight(request.index_code)
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadCBData(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载可转债数据"""
        try:
            result = self.data_service.download_cb_data()
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadETFInfo(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载ETF信息"""
        try:
            result = self.data_service.download_etf_info()
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadHolidayData(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载节假日数据"""
        try:
            result = self.data_service.download_holiday_data()
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    def DownloadHistoryContracts(
        self, 
        request: data_pb2.DownloadHistoryContractsRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.DownloadResponse:
        """下载历史合约数据"""
        try:
            result = self.data_service.download_history_contracts(request.market)
            
            status_map = {
                'pending': data_pb2.DOWNLOAD_PENDING,
                'running': data_pb2.DOWNLOAD_RUNNING,
                'completed': data_pb2.DOWNLOAD_COMPLETED,
                'failed': data_pb2.DOWNLOAD_FAILED
            }
            
            return data_pb2.DownloadResponse(
                task_id=result.task_id,
                status=status_map.get(result.status, data_pb2.DOWNLOAD_PENDING),
                progress=result.progress,
                total=result.total,
                finished=result.finished,
                message=result.message,
                rpc_status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.DownloadResponse(
                rpc_status=common_pb2.Status(code=500, message=str(e))
            )
    
    # ==================== 阶段4: 板块管理接口实现 ====================
    
    def CreateSectorFolder(
        self, 
        request: data_pb2.CreateSectorFolderRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.CreateSectorFolderResponse:
        """创建板块文件夹"""
        try:
            result = self.data_service.create_sector_folder(
                request.parent_node,
                request.folder_name,
                request.overwrite
            )
            
            return data_pb2.CreateSectorFolderResponse(
                created_name=result,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.CreateSectorFolderResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def CreateSector(
        self, 
        request: data_pb2.CreateSectorRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.CreateSectorResponse:
        """创建板块"""
        try:
            result = self.data_service.create_sector(
                request.parent_node,
                request.sector_name,
                request.overwrite
            )
            
            return data_pb2.CreateSectorResponse(
                created_name=result,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.CreateSectorResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def AddSector(
        self, 
        request: data_pb2.AddSectorRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.AddSectorResponse:
        """添加股票到板块"""
        try:
            self.data_service.add_sector(
                request.sector_name,
                list(request.stock_list)
            )
            
            return data_pb2.AddSectorResponse(
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.AddSectorResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def RemoveStockFromSector(
        self, 
        request: data_pb2.RemoveStockFromSectorRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.RemoveStockFromSectorResponse:
        """从板块移除股票"""
        try:
            result = self.data_service.remove_stock_from_sector(
                request.sector_name,
                list(request.stock_list)
            )
            
            return data_pb2.RemoveStockFromSectorResponse(
                success=result,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.RemoveStockFromSectorResponse(
                success=False,
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def RemoveSector(
        self, 
        request: data_pb2.RemoveSectorRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.RemoveSectorResponse:
        """删除板块"""
        try:
            self.data_service.remove_sector(request.sector_name)
            
            return data_pb2.RemoveSectorResponse(
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.RemoveSectorResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def ResetSector(
        self, 
        request: data_pb2.ResetSectorRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.ResetSectorResponse:
        """重置板块"""
        try:
            result = self.data_service.reset_sector(
                request.sector_name,
                list(request.stock_list)
            )
            
            return data_pb2.ResetSectorResponse(
                success=result,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.ResetSectorResponse(
                success=False,
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    # ==================== 阶段5: Level2数据接口实现 ====================
    
    def GetL2Quote(
        self, 
        request: data_pb2.L2QuoteRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.L2QuoteResponse:
        """获取Level2快照数据"""
        try:
            result = self.data_service.get_l2_quote(
                list(request.stock_codes),
                request.start_time,
                request.end_time
            )
            
            data_map = {}
            for stock_code, quote_list in result.items():
                quotes = []
                for quote in quote_list:
                    quote_data = data_pb2.L2QuoteData(
                        time=quote.get('time', ''),
                        last_price=quote.get('last_price', 0.0),
                        open=quote.get('open', 0.0),
                        high=quote.get('high', 0.0),
                        low=quote.get('low', 0.0),
                        amount=quote.get('amount', 0.0),
                        volume=quote.get('volume', 0),
                        pvolume=quote.get('pvolume', 0),
                        open_int=quote.get('open_int', 0),
                        stock_status=quote.get('stock_status', 0),
                        transaction_num=quote.get('transaction_num', 0),
                        last_close=quote.get('last_close', 0.0),
                        last_settlement_price=quote.get('last_settlement_price', 0.0),
                        settlement_price=quote.get('settlement_price', 0.0),
                        pe=quote.get('pe', 0.0),
                        ask_price=quote.get('ask_price', []),
                        bid_price=quote.get('bid_price', []),
                        ask_vol=quote.get('ask_vol', []),
                        bid_vol=quote.get('bid_vol', [])
                    )
                    quotes.append(quote_data)
                data_map[stock_code] = data_pb2.L2QuoteDataList(quotes=quotes)
            
            return data_pb2.L2QuoteResponse(
                data=data_map,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.L2QuoteResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetL2Order(
        self, 
        request: data_pb2.L2OrderRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.L2OrderResponse:
        """获取Level2逐笔委托"""
        try:
            result = self.data_service.get_l2_order(
                list(request.stock_codes),
                request.start_time,
                request.end_time
            )
            
            data_map = {}
            for stock_code, order_list in result.items():
                orders = []
                for order in order_list:
                    order_data = data_pb2.L2OrderData(
                        time=order.get('time', ''),
                        price=order.get('price', 0.0),
                        volume=order.get('volume', 0),
                        entrust_no=order.get('entrust_no', 0),
                        entrust_type=order.get('entrust_type', 0),
                        entrust_direction=order.get('entrust_direction', 0)
                    )
                    orders.append(order_data)
                data_map[stock_code] = data_pb2.L2OrderDataList(orders=orders)
            
            return data_pb2.L2OrderResponse(
                data=data_map,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.L2OrderResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetL2Transaction(
        self, 
        request: data_pb2.L2TransactionRequest, 
        context: grpc.ServicerContext
    ) -> data_pb2.L2TransactionResponse:
        """获取Level2逐笔成交"""
        try:
            result = self.data_service.get_l2_transaction(
                list(request.stock_codes),
                request.start_time,
                request.end_time
            )
            
            data_map = {}
            for stock_code, trans_list in result.items():
                transactions = []
                for trans in trans_list:
                    trans_data = data_pb2.L2TransactionData(
                        time=trans.get('time', ''),
                        price=trans.get('price', 0.0),
                        volume=trans.get('volume', 0),
                        amount=trans.get('amount', 0.0),
                        trade_index=trans.get('trade_index', 0),
                        buy_no=trans.get('buy_no', 0),
                        sell_no=trans.get('sell_no', 0),
                        trade_type=trans.get('trade_type', 0),
                        trade_flag=trans.get('trade_flag', 0)
                    )
                    transactions.append(trans_data)
                data_map[stock_code] = data_pb2.L2TransactionDataList(transactions=transactions)
            
            return data_pb2.L2TransactionResponse(
                data=data_map,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.L2TransactionResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )

