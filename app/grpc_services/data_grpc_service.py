"""
gRPC 数据服务实现
"""
from typing import Any

import grpc
from google.protobuf import empty_pb2
from pydantic import BaseModel

from app.models.data_models import FinancialDataRequest as RestFinancialDataRequest
from app.models.data_models import IndexWeightRequest as RestIndexWeightRequest
from app.models.data_models import MarketDataRequest as RestMarketDataRequest
from app.models.data_models import PeriodType

# 导入现有服务
from app.services.data_service import DataService
from app.utils.exceptions import DataServiceException

# 导入生成的 protobuf 代码
from generated import common_pb2, data_pb2, data_pb2_grpc


def pydantic_to_dict(obj: Any) -> Any:
    """将Pydantic对象转换为字典，如果不是Pydantic对象则直接返回"""
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, list):
        return [pydantic_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: pydantic_to_dict(v) for k, v in obj.items()}
    return obj


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
            common_pb2.PERIOD_TYPE_1Q: PeriodType.QUARTER,
            common_pb2.PERIOD_TYPE_1HY: PeriodType.YEAR_HALF,
            common_pb2.PERIOD_TYPE_1Y: PeriodType.YEAR,
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
            
            # result是InstrumentTypeInfo对象，直接访问属性
            info = data_pb2.InstrumentTypeInfo(
                stock_code=result.stock_code,
                index=result.index,
                stock=result.stock,
                fund=result.fund,
                etf=result.etf,
                bond=result.bond,
                option=result.option,
                futures=result.futures
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
            
            # result是HolidayInfo对象，直接访问属性
            return data_pb2.HolidayInfoResponse(
                holidays=result.holidays,
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
            
            # 检查是否客户端不支持
            if isinstance(results, list) and len(results) > 0:
                # results是ConvertibleBondInfo对象列表，直接访问属性
                bonds = []
                for cb in results:
                    bond = data_pb2.ConvertibleBondInfo(
                        bond_code=cb.bond_code,
                        bond_name=cb.bond_name or '',
                        stock_code=cb.stock_code or '',
                        stock_name=cb.stock_name or '',
                        conversion_price=cb.conversion_price or 0.0,
                        conversion_value=cb.conversion_value or 0.0,
                        conversion_premium_rate=cb.conversion_premium_rate or 0.0,
                        current_price=cb.current_price or 0.0,
                        par_value=cb.par_value or 0.0,
                        list_date=cb.list_date or '',
                        maturity_date=cb.maturity_date or '',
                        conversion_begin_date=cb.conversion_begin_date or '',
                        conversion_end_date=cb.conversion_end_date or ''
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
                # ipo是IpoInfo对象，直接访问属性
                ipo_info = data_pb2.IpoInfo(
                    security_code=ipo.security_code or '',
                    code_name=ipo.code_name or '',
                    market=ipo.market or '',
                    act_issue_qty=ipo.act_issue_qty or 0,
                    online_issue_qty=ipo.online_issue_qty or 0,
                    online_sub_code=ipo.online_sub_code or '',
                    online_sub_max_qty=ipo.online_sub_max_qty or 0,
                    publish_price=ipo.publish_price or 0.0,
                    is_profit=ipo.is_profit or 0,
                    industry_pe=ipo.industry_pe or 0.0,
                    after_pe=ipo.after_pe or 0.0,
                    subscribe_date=ipo.subscribe_date or '',
                    lottery_date=ipo.lottery_date or '',
                    list_date=ipo.list_date or ''
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
            
            # result是PeriodListResponse对象，直接访问属性
            return data_pb2.PeriodListResponse(
                periods=result.periods,
                status=common_pb2.Status(code=0, message="success")
            )
        except Exception as e:
            # 检查是否为不支持的功能
            error_msg = str(e)
            if "function not realize" in error_msg or "未支持此功能" in error_msg:
                context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return data_pb2.PeriodListResponse(
                status=common_pb2.Status(code=500, message=error_msg)
            )
    
    def GetDataDir(
        self, 
        request: empty_pb2.Empty, 
        context: grpc.ServicerContext
    ) -> data_pb2.DataDirResponse:
        """获取本地数据路径"""
        try:
            result = self.data_service.get_data_dir()
            
            # result是DataDirResponse对象，直接访问属性
            return data_pb2.DataDirResponse(
                data_dir=result.data_dir,
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
            # 构造LocalDataRequest对象
            from app.models.data_models import LocalDataRequest as LocalDataReq
            req = LocalDataReq(
                stock_codes=list(request.stock_codes),
                start_time=request.start_time,
                end_time=request.end_time,
                period=request.period,
                fields=list(request.fields) if request.fields else None,
                adjust_type=request.adjust_type if request.adjust_type else "none"
            )
            
            # 调用服务层，返回 List[MarketDataResponse]
            result = self.data_service.get_local_data(req)
            
            # 遍历响应列表，构造 gRPC 响应
            data_map = {}
            for market_data_response in result:
                stock_code = market_data_response.stock_code
                bars = []
                # market_data_response.data 是 List[Dict[str, Any]]
                for item in market_data_response.data:
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
            # 构建FullTickRequest对象
            from app.models.data_models import FullTickRequest as FullTickReq
            req = FullTickReq(
                stock_codes=list(request.stock_codes),
                start_time=request.start_time,
                end_time=request.end_time
            )
            result = self.data_service.get_full_tick(req)
            
            data_map = {}
            for stock_code, tick_list in result.items():
                ticks = []
                for tick in tick_list:
                    # tick 是 TickData Pydantic 模型，使用属性访问
                    tick_data = data_pb2.TickData(
                        time=tick.time or '',
                        last_price=tick.last_price,
                        open=tick.open or 0.0,
                        high=tick.high or 0.0,
                        low=tick.low or 0.0,
                        last_close=tick.last_close or 0.0,
                        amount=tick.amount or 0.0,
                        volume=tick.volume or 0,
                        pvolume=tick.pvolume or 0,
                        stock_status=tick.stock_status or 0,
                        open_int=tick.open_int or 0,
                        last_settlement_price=tick.last_settlement_price or 0.0,
                        ask_price=tick.ask_price or [],
                        bid_price=tick.bid_price or [],
                        ask_vol=tick.ask_vol or [],
                        bid_vol=tick.bid_vol or [],
                        transaction_num=tick.transaction_num or 0
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
            # 构造FullKlineRequest对象
            from app.models.data_models import FullKlineRequest as FullKlineReq
            req = FullKlineReq(
                stock_codes=list(request.stock_codes),
                start_time=request.start_time,
                end_time=request.end_time,
                period=request.period,
                fields=list(request.fields) if request.fields else None,
                adjust_type=request.adjust_type if request.adjust_type else "none"
            )
            
            # 调用服务层，返回 List[MarketDataResponse]
            result = self.data_service.get_full_kline(req)
            
            # 遍历响应列表，构造 gRPC 响应
            data_map = {}
            for market_data_response in result:
                stock_code = market_data_response.stock_code
                bars = []
                # market_data_response.data 是 List[Dict[str, Any]]
                for item in market_data_response.data:
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
            result = self.data_service.get_l2_quote(list(request.stock_codes))
            
            data_map = {}
            for stock_code, quote in result.items():
                # quote 是单个 L2QuoteData 对象，包装为列表
                quote_data = data_pb2.L2QuoteData(
                    time=quote.time or '',
                    last_price=quote.last_price,
                    open=quote.open or 0.0,
                    high=quote.high or 0.0,
                    low=quote.low or 0.0,
                    amount=quote.amount or 0.0,
                    volume=quote.volume or 0,
                    pvolume=quote.pvolume or 0,
                    open_int=quote.open_int or 0,
                    stock_status=quote.stock_status or 0,
                    transaction_num=quote.transaction_num or 0,
                    last_close=quote.last_close or 0.0,
                    last_settlement_price=quote.last_settlement_price or 0.0,
                    settlement_price=quote.settlement_price or 0.0,
                    pe=quote.pe or 0.0,
                    ask_price=quote.ask_price or [],
                    bid_price=quote.bid_price or [],
                    ask_vol=quote.ask_vol or [],
                    bid_vol=quote.bid_vol or []
                )
                # 包装为列表
                data_map[stock_code] = data_pb2.L2QuoteDataList(quotes=[quote_data])
            
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
            result = self.data_service.get_l2_order(list(request.stock_codes))
            
            data_map = {}
            for stock_code, order_list in result.items():
                orders = []
                for order in order_list:
                    # order 是 L2OrderData Pydantic 模型
                    order_data = data_pb2.L2OrderData(
                        time=order.time or '',
                        price=order.price,
                        volume=order.volume,
                        entrust_no=order.entrust_no or 0,
                        entrust_type=order.entrust_type or 0,
                        entrust_direction=order.entrust_direction or 0
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
            result = self.data_service.get_l2_transaction(list(request.stock_codes))
            
            data_map = {}
            for stock_code, trans_list in result.items():
                transactions = []
                for trans in trans_list:
                    # trans 是 L2TransactionData Pydantic 模型
                    trans_data = data_pb2.L2TransactionData(
                        time=trans.time or '',
                        price=trans.price,
                        volume=trans.volume,
                        amount=trans.amount or 0.0,
                        trade_index=trans.trade_index or 0,
                        buy_no=trans.buy_no or 0,
                        sell_no=trans.sell_no or 0,
                        trade_type=trans.trade_type or 0,
                        trade_flag=trans.trade_flag or 0
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
    
    # ==================== 阶段6: 行情订阅接口 ====================
    
    def SubscribeQuote(
        self,
        request: data_pb2.SubscriptionRequest,
        context: grpc.ServicerContext
    ):
        """
        订阅行情（Server Streaming）
        
        持续推送行情数据，直到客户端断开连接
        """
        import asyncio
        from datetime import datetime

        from app.config import get_settings
        from app.dependencies import get_subscription_manager
        
        try:
            settings = get_settings()
            subscription_manager = get_subscription_manager(settings)
            
            # 检测当前线程是否已有事件循环
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # 没有事件循环，创建新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # 通知订阅管理器使用此事件循环
                subscription_manager.set_event_loop(loop)
            
            # 验证股票代码列表
            if not request.symbols or len(list(request.symbols)) == 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("股票代码列表不能为空")
                return
            
            # 创建订阅
            subscription_id = subscription_manager.subscribe_quote(
                symbols=list(request.symbols),
                adjust_type=request.adjust_type or "none"
            )
            
            # 记录订阅信息
            context.set_code(grpc.StatusCode.OK)
            
            # 流式推送数据
            async def stream_data():
                try:
                    async for quote_data in subscription_manager.stream_quotes(subscription_id):
                        # 构造protobuf消息
                        quote_update = data_pb2.QuoteUpdate(
                            stock_code=quote_data.get('stock_code', ''),
                            timestamp=quote_data.get('timestamp', datetime.now().isoformat()),
                            last_price=quote_data.get('last_price', 0.0),
                            open=quote_data.get('open', 0.0),
                            high=quote_data.get('high', 0.0),
                            low=quote_data.get('low', 0.0),
                            close=quote_data.get('close', 0.0),
                            volume=quote_data.get('volume', 0),
                            amount=quote_data.get('amount', 0.0),
                            pre_close=quote_data.get('pre_close', 0.0),
                            bid_price=quote_data.get('bid_price', []),
                            ask_price=quote_data.get('ask_price', []),
                            bid_vol=quote_data.get('bid_vol', []),
                            ask_vol=quote_data.get('ask_vol', [])
                        )
                        
                        yield quote_update
                        
                        # 检查客户端是否断开
                        if context.is_active() is False:
                            break
                
                finally:
                    # 清理订阅
                    subscription_manager.unsubscribe(subscription_id)
            
            # 使用事件循环迭代异步生成器
            try:
                async_gen = stream_data()
                while True:
                    try:
                        quote_update = loop.run_until_complete(async_gen.__anext__())
                        yield quote_update
                    except StopAsyncIteration:
                        break
            finally:
                # 只在当前线程创建的循环时才关闭
                if not loop.is_running():
                    loop.close()
        
        except DataServiceException as e:
            # 处理业务异常
            if e.error_code in ["EMPTY_SYMBOLS", "INVALID_SYMBOLS"]:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            else:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(str(e.message))
            return
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return
    
    def SubscribeWholeQuote(
        self,
        request: data_pb2.WholeQuoteRequest,
        context: grpc.ServicerContext
    ):
        """
        订阅全推行情（Server Streaming）
        """
        import asyncio
        from datetime import datetime

        from app.config import get_settings
        from app.dependencies import get_subscription_manager
        
        try:
            settings = get_settings()
            subscription_manager = get_subscription_manager(settings)
            
            # 检测当前线程是否已有事件循环
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # 没有事件循环，创建新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # 通知订阅管理器使用此事件循环
                subscription_manager.set_event_loop(loop)
            
            # 创建全推订阅
            subscription_id = subscription_manager.subscribe_whole_quote()
            
            context.set_code(grpc.StatusCode.OK)
            
            # 流式推送数据
            async def stream_data():
                try:
                    async for quote_data in subscription_manager.stream_quotes(subscription_id):
                        quote_update = data_pb2.QuoteUpdate(
                            stock_code=quote_data.get('stock_code', ''),
                            timestamp=quote_data.get('timestamp', datetime.now().isoformat()),
                            last_price=quote_data.get('last_price', 0.0),
                            open=quote_data.get('open', 0.0),
                            high=quote_data.get('high', 0.0),
                            low=quote_data.get('low', 0.0),
                            close=quote_data.get('close', 0.0),
                            volume=quote_data.get('volume', 0),
                            amount=quote_data.get('amount', 0.0),
                            pre_close=quote_data.get('pre_close', 0.0),
                            bid_price=quote_data.get('bid_price', []),
                            ask_price=quote_data.get('ask_price', []),
                            bid_vol=quote_data.get('bid_vol', []),
                            ask_vol=quote_data.get('ask_vol', [])
                        )
                        
                        yield quote_update
                        
                        if context.is_active() is False:
                            break
                
                finally:
                    subscription_manager.unsubscribe(subscription_id)
            
            # 使用事件循环迭代异步生成器
            try:
                async_gen = stream_data()
                while True:
                    try:
                        quote_update = loop.run_until_complete(async_gen.__anext__())
                        yield quote_update
                    except StopAsyncIteration:
                        break
            finally:
                # 只在当前线程创建的循环时才关闭
                if not loop.is_running():
                    loop.close()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return
    
    def UnsubscribeQuote(
        self,
        request: data_pb2.UnsubscribeRequest,
        context: grpc.ServicerContext
    ) -> data_pb2.UnsubscribeResponse:
        """取消订阅"""
        from app.config import get_settings
        from app.dependencies import get_subscription_manager
        
        try:
            settings = get_settings()
            subscription_manager = get_subscription_manager(settings)
            
            # 取消订阅
            success = subscription_manager.unsubscribe(request.subscription_id)
            
            return data_pb2.UnsubscribeResponse(
                success=success,
                message="订阅已取消" if success else "订阅不存在",
                status=common_pb2.Status(code=0, message="success")
            )
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.UnsubscribeResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetSubscriptionInfo(
        self,
        request: data_pb2.SubscriptionInfoRequest,
        context: grpc.ServicerContext
    ) -> data_pb2.SubscriptionInfoResponse:
        """获取订阅信息"""
        from app.config import get_settings
        from app.dependencies import get_subscription_manager
        
        try:
            settings = get_settings()
            subscription_manager = get_subscription_manager(settings)
            
            # 获取订阅信息
            info = subscription_manager.get_subscription_info(request.subscription_id)
            
            if not info:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"订阅不存在: {request.subscription_id}")
                return data_pb2.SubscriptionInfoResponse(
                    status=common_pb2.Status(code=404, message="订阅不存在")
                )
            
            return data_pb2.SubscriptionInfoResponse(
                subscription_id=info['subscription_id'],
                symbols=info['symbols'],
                adjust_type=info['adjust_type'],
                subscription_type=info['subscription_type'],
                created_at=info['created_at'],
                last_heartbeat=info['last_heartbeat'],
                active=info['active'],
                queue_size=info['queue_size'],
                status=common_pb2.Status(code=0, message="success")
            )
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.SubscriptionInfoResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def ListSubscriptions(
        self,
        request: empty_pb2.Empty,
        context: grpc.ServicerContext
    ) -> data_pb2.SubscriptionListResponse:
        """列出所有订阅"""
        from app.config import get_settings
        from app.dependencies import get_subscription_manager
        
        try:
            settings = get_settings()
            subscription_manager = get_subscription_manager(settings)
            
            # 列出所有订阅
            subscriptions = subscription_manager.list_subscriptions()
            
            # 构造响应
            sub_list = []
            for info in subscriptions:
                sub_info = data_pb2.SubscriptionInfoResponse(
                    subscription_id=info['subscription_id'],
                    symbols=info['symbols'],
                    adjust_type=info['adjust_type'],
                    subscription_type=info['subscription_type'],
                    created_at=info['created_at'],
                    last_heartbeat=info['last_heartbeat'],
                    active=info['active'],
                    queue_size=info['queue_size'],
                    status=common_pb2.Status(code=0, message="success")
                )
                sub_list.append(sub_info)
            
            return data_pb2.SubscriptionListResponse(
                subscriptions=sub_list,
                status=common_pb2.Status(code=0, message="success")
            )
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return data_pb2.SubscriptionListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )

