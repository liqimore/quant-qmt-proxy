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
