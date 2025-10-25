"""
gRPC 交易服务实现
"""
import grpc
from typing import List
from datetime import datetime

# 导入生成的 protobuf 代码
from generated import trading_pb2, trading_pb2_grpc, common_pb2

# 导入现有服务
from app.services.trading_service import TradingService
from app.models.trading_models import (
    ConnectRequest as RestConnectRequest,
    OrderRequest as RestOrderRequest,
    CancelOrderRequest as RestCancelOrderRequest,
    OrderSide as RestOrderSide,
    OrderType as RestOrderType,
    AccountType as RestAccountType
)
from app.utils.exceptions import TradingServiceException


class TradingGrpcService(trading_pb2_grpc.TradingServiceServicer):
    """gRPC 交易服务实现"""
    
    def __init__(self, trading_service: TradingService):
        self.trading_service = trading_service
    
    def Connect(
        self, 
        request: trading_pb2.ConnectRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.ConnectResponse:
        """连接账户"""
        try:
            # 转换请求
            rest_request = RestConnectRequest(
                account_id=request.account_id,
                password=request.password if request.password else None,
                client_id=request.client_id if request.client_id else None
            )
            
            # 调用服务
            result = self.trading_service.connect_account(rest_request)
            
            # 转换响应
            account_info = None
            if result.account_info:
                account_info = self._convert_account_info(result.account_info)
            
            return trading_pb2.ConnectResponse(
                success=result.success,
                message=result.message,
                session_id=result.session_id or "",
                account_info=account_info,
                status=common_pb2.Status(code=0 if result.success else 400, message=result.message)
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.ConnectResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.ConnectResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def Disconnect(
        self, 
        request: trading_pb2.DisconnectRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.DisconnectResponse:
        """断开账户"""
        try:
            # 调用服务
            success = self.trading_service.disconnect_account(request.session_id)
            
            return trading_pb2.DisconnectResponse(
                success=success,
                message="断开账户成功" if success else "断开账户失败",
                status=common_pb2.Status(code=0 if success else 400, message="success" if success else "failed")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.DisconnectResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.DisconnectResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetAccountInfo(
        self, 
        request: trading_pb2.DisconnectRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.ConnectResponse:
        """获取账户信息"""
        try:
            # 调用服务
            result = self.trading_service.get_account_info(request.session_id)
            
            # 转换响应
            account_info = self._convert_account_info(result)
            
            return trading_pb2.ConnectResponse(
                success=True,
                message="获取账户信息成功",
                session_id=request.session_id,
                account_info=account_info,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.ConnectResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.ConnectResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetPositions(
        self, 
        request: trading_pb2.PositionRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.PositionListResponse:
        """获取持仓列表"""
        try:
            # 调用服务
            results = self.trading_service.get_positions(request.session_id)
            
            # 转换响应
            positions = []
            for result in results:
                position = trading_pb2.PositionInfo(
                    stock_code=result.stock_code,
                    stock_name=result.stock_name,
                    volume=result.volume,
                    available_volume=result.available_volume,
                    frozen_volume=result.frozen_volume,
                    cost_price=result.cost_price,
                    market_price=result.market_price,
                    market_value=result.market_value,
                    profit_loss=result.profit_loss,
                    profit_loss_ratio=result.profit_loss_ratio
                )
                positions.append(position)
            
            return trading_pb2.PositionListResponse(
                positions=positions,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.PositionListResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.PositionListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def SubmitOrder(
        self, 
        request: trading_pb2.OrderRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.OrderResponse:
        """提交订单"""
        try:
            # 转换请求
            rest_request = self._convert_order_request(request)
            
            # 调用服务
            result = self.trading_service.submit_order(request.session_id, rest_request)
            
            # 转换响应
            order_info = self._convert_order_info(result)
            
            return trading_pb2.OrderResponse(
                order=order_info,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.OrderResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.OrderResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def CancelOrder(
        self, 
        request: trading_pb2.CancelOrderRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.CancelOrderResponse:
        """撤销订单"""
        try:
            # 转换请求
            rest_request = RestCancelOrderRequest(order_id=request.order_id)
            
            # 调用服务
            success = self.trading_service.cancel_order(request.session_id, rest_request)
            
            return trading_pb2.CancelOrderResponse(
                success=success,
                message="撤销订单成功" if success else "撤销订单失败",
                status=common_pb2.Status(code=0 if success else 400, message="success" if success else "failed")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.CancelOrderResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.CancelOrderResponse(
                success=False,
                message=str(e),
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetOrders(
        self, 
        request: trading_pb2.OrderListRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.OrderListResponse:
        """获取订单列表"""
        try:
            # 调用服务
            results = self.trading_service.get_orders(request.session_id)
            
            # 转换响应
            orders = []
            for result in results:
                order_info = self._convert_order_info(result)
                orders.append(order_info)
            
            return trading_pb2.OrderListResponse(
                orders=orders,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.OrderListResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.OrderListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetTrades(
        self, 
        request: trading_pb2.TradeListRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.TradeListResponse:
        """获取成交记录"""
        try:
            # 调用服务
            results = self.trading_service.get_trades(request.session_id)
            
            # 转换响应
            trades = []
            for result in results:
                side_map = {
                    "BUY": trading_pb2.ORDER_SIDE_BUY,
                    "SELL": trading_pb2.ORDER_SIDE_SELL
                }
                
                trade = trading_pb2.TradeInfo(
                    trade_id=result.trade_id,
                    order_id=result.order_id,
                    stock_code=result.stock_code,
                    side=side_map.get(result.side, trading_pb2.ORDER_SIDE_UNSPECIFIED),
                    volume=result.volume,
                    price=result.price,
                    amount=result.amount,
                    trade_time=result.trade_time.isoformat() if isinstance(result.trade_time, datetime) else str(result.trade_time),
                    commission=result.commission
                )
                trades.append(trade)
            
            return trading_pb2.TradeListResponse(
                trades=trades,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.TradeListResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.TradeListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetAsset(
        self, 
        request: trading_pb2.AssetRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.AssetResponse:
        """获取资产信息"""
        try:
            # 调用服务
            result = self.trading_service.get_asset_info(request.session_id)
            
            # 转换响应
            asset = trading_pb2.AssetInfo(
                total_asset=result.total_asset,
                market_value=result.market_value,
                cash=result.cash,
                frozen_cash=result.frozen_cash,
                available_cash=result.available_cash,
                profit_loss=result.profit_loss,
                profit_loss_ratio=result.profit_loss_ratio
            )
            
            return trading_pb2.AssetResponse(
                asset=asset,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.AssetResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.AssetResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetRiskInfo(
        self, 
        request: trading_pb2.RiskInfoRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.RiskInfoResponse:
        """获取风险信息"""
        try:
            # 调用服务
            result = self.trading_service.get_risk_info(request.session_id)
            
            return trading_pb2.RiskInfoResponse(
                position_ratio=result.position_ratio,
                cash_ratio=result.cash_ratio,
                max_drawdown=result.max_drawdown,
                var_95=result.var_95,
                var_99=result.var_99,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.RiskInfoResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.RiskInfoResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    def GetStrategies(
        self, 
        request: trading_pb2.StrategyListRequest, 
        context: grpc.ServicerContext
    ) -> trading_pb2.StrategyListResponse:
        """获取策略列表"""
        try:
            # 调用服务
            results = self.trading_service.get_strategies(request.session_id)
            
            # 转换响应
            strategies = []
            for result in results:
                # 将parameters字典转换为map<string, string>
                parameters = {k: str(v) for k, v in result.parameters.items()}
                
                strategy = trading_pb2.StrategyInfo(
                    strategy_name=result.strategy_name,
                    strategy_type=result.strategy_type,
                    status=result.status,
                    created_time=result.created_time.isoformat() if isinstance(result.created_time, datetime) else str(result.created_time),
                    last_update_time=result.last_update_time.isoformat() if isinstance(result.last_update_time, datetime) else str(result.last_update_time),
                    parameters=parameters
                )
                strategies.append(strategy)
            
            return trading_pb2.StrategyListResponse(
                strategies=strategies,
                status=common_pb2.Status(code=0, message="success")
            )
            
        except TradingServiceException as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return trading_pb2.StrategyListResponse(
                status=common_pb2.Status(code=400, message=str(e))
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return trading_pb2.StrategyListResponse(
                status=common_pb2.Status(code=500, message=str(e))
            )
    
    # 辅助转换方法
    
    def _convert_account_info(self, account_info):
        """转换账户信息"""
        account_type_map = {
            RestAccountType.FUTURE: trading_pb2.ACCOUNT_TYPE_FUTURE,
            RestAccountType.SECURITY: trading_pb2.ACCOUNT_TYPE_SECURITY,
            RestAccountType.CREDIT: trading_pb2.ACCOUNT_TYPE_CREDIT,
            RestAccountType.FUTURE_OPTION: trading_pb2.ACCOUNT_TYPE_FUTURE_OPTION,
            RestAccountType.STOCK_OPTION: trading_pb2.ACCOUNT_TYPE_STOCK_OPTION
        }
        
        return trading_pb2.AccountInfo(
            account_id=account_info.account_id,
            account_type=account_type_map.get(account_info.account_type, trading_pb2.ACCOUNT_TYPE_UNSPECIFIED),
            account_name=account_info.account_name,
            status=account_info.status,
            balance=account_info.balance,
            available_balance=account_info.available_balance,
            frozen_balance=account_info.frozen_balance,
            market_value=account_info.market_value,
            total_asset=account_info.total_asset
        )
    
    def _convert_order_request(self, pb_request: trading_pb2.OrderRequest) -> RestOrderRequest:
        """转换订单请求"""
        side_map = {
            trading_pb2.ORDER_SIDE_BUY: RestOrderSide.BUY,
            trading_pb2.ORDER_SIDE_SELL: RestOrderSide.SELL
        }
        
        type_map = {
            trading_pb2.ORDER_TYPE_MARKET: RestOrderType.MARKET,
            trading_pb2.ORDER_TYPE_LIMIT: RestOrderType.LIMIT,
            trading_pb2.ORDER_TYPE_STOP: RestOrderType.STOP,
            trading_pb2.ORDER_TYPE_STOP_LIMIT: RestOrderType.STOP_LIMIT
        }
        
        return RestOrderRequest(
            stock_code=pb_request.stock_code,
            side=side_map.get(pb_request.side, RestOrderSide.BUY),
            order_type=type_map.get(pb_request.order_type, RestOrderType.LIMIT),
            volume=int(pb_request.volume),
            price=pb_request.price if pb_request.price else None,
            strategy_name=pb_request.strategy_name if pb_request.strategy_name else None
        )
    
    def _convert_order_info(self, order_response):
        """转换订单信息"""
        side_map = {
            "BUY": trading_pb2.ORDER_SIDE_BUY,
            "SELL": trading_pb2.ORDER_SIDE_SELL
        }
        
        type_map = {
            "MARKET": trading_pb2.ORDER_TYPE_MARKET,
            "LIMIT": trading_pb2.ORDER_TYPE_LIMIT,
            "STOP": trading_pb2.ORDER_TYPE_STOP,
            "STOP_LIMIT": trading_pb2.ORDER_TYPE_STOP_LIMIT
        }
        
        status_map = {
            "PENDING": trading_pb2.ORDER_STATUS_PENDING,
            "SUBMITTED": trading_pb2.ORDER_STATUS_SUBMITTED,
            "PARTIAL_FILLED": trading_pb2.ORDER_STATUS_PARTIAL_FILLED,
            "FILLED": trading_pb2.ORDER_STATUS_FILLED,
            "CANCELLED": trading_pb2.ORDER_STATUS_CANCELLED,
            "REJECTED": trading_pb2.ORDER_STATUS_REJECTED
        }
        
        return trading_pb2.OrderInfo(
            order_id=order_response.order_id,
            stock_code=order_response.stock_code,
            side=side_map.get(order_response.side, trading_pb2.ORDER_SIDE_UNSPECIFIED),
            order_type=type_map.get(order_response.order_type, trading_pb2.ORDER_TYPE_UNSPECIFIED),
            volume=order_response.volume,
            price=order_response.price if order_response.price else 0.0,
            status=status_map.get(order_response.status, trading_pb2.ORDER_STATUS_UNSPECIFIED),
            submitted_time=order_response.submitted_time.isoformat() if isinstance(order_response.submitted_time, datetime) else str(order_response.submitted_time),
            filled_volume=order_response.filled_volume,
            filled_amount=order_response.filled_amount,
            average_price=order_response.average_price if order_response.average_price else 0.0
        )
