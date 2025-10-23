"""
交易服务路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.trading_service import TradingService
from app.models.trading_models import (
    ConnectRequest, ConnectResponse, AccountInfo, PositionInfo,
    OrderRequest, OrderResponse, CancelOrderRequest, TradeInfo,
    AssetInfo, RiskInfo, StrategyInfo
)
from app.utils.helpers import format_response
from app.utils.exceptions import TradingServiceException, handle_xtquant_exception
from app.dependencies import verify_api_key
from app.config import get_settings, Settings

router = APIRouter(prefix="/api/v1/trading", tags=["交易服务"])


@router.post("/connect", response_model=ConnectResponse)
async def connect_account(
    request: ConnectRequest,
    api_key: str = Depends(verify_api_key),
    settings: Settings = Depends(get_settings)
):
    """连接交易账户"""
    try:
        trading_service = TradingService(settings)
        result = trading_service.connect_account(request)
        return result
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"连接账户失败: {str(e)}"}
        )


@router.post("/disconnect/{session_id}")
async def disconnect_account(
    session_id: str,
    api_key: str = Depends(verify_api_key),
    settings: Settings = Depends(get_settings)
):
    """断开交易账户"""
    try:
        trading_service = TradingService(settings)
        success = trading_service.disconnect_account(session_id)
        return format_response(
            data={"success": success},
            message="断开账户成功" if success else "断开账户失败"
        )
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"断开账户失败: {str(e)}"}
        )


@router.get("/account/{session_id}", response_model=AccountInfo)
async def get_account_info(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取账户信息"""
    try:
        trading_service = TradingService()
        result = trading_service.get_account_info(session_id)
        return result
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取账户信息失败: {str(e)}"}
        )


@router.get("/positions/{session_id}", response_model=List[PositionInfo])
async def get_positions(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取持仓信息"""
    try:
        trading_service = TradingService()
        results = trading_service.get_positions(session_id)
        return results
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取持仓信息失败: {str(e)}"}
        )


@router.post("/order/{session_id}", response_model=OrderResponse)
async def submit_order(
    session_id: str,
    request: OrderRequest,
    api_key: str = Depends(verify_api_key)
):
    """提交订单"""
    try:
        trading_service = TradingService()
        result = trading_service.submit_order(session_id, request)
        return result
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"提交订单失败: {str(e)}"}
        )


@router.post("/cancel/{session_id}")
async def cancel_order(
    session_id: str,
    request: CancelOrderRequest,
    api_key: str = Depends(verify_api_key)
):
    """撤销订单"""
    try:
        trading_service = TradingService()
        success = trading_service.cancel_order(session_id, request)
        return format_response(
            data={"success": success},
            message="撤销订单成功" if success else "撤销订单失败"
        )
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"撤销订单失败: {str(e)}"}
        )


@router.get("/orders/{session_id}", response_model=List[OrderResponse])
async def get_orders(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取订单列表"""
    try:
        trading_service = TradingService()
        results = trading_service.get_orders(session_id)
        return results
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取订单列表失败: {str(e)}"}
        )


@router.get("/trades/{session_id}", response_model=List[TradeInfo])
async def get_trades(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取成交记录"""
    try:
        trading_service = TradingService()
        results = trading_service.get_trades(session_id)
        return results
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取成交记录失败: {str(e)}"}
        )


@router.get("/asset/{session_id}", response_model=AssetInfo)
async def get_asset_info(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取资产信息"""
    try:
        trading_service = TradingService()
        result = trading_service.get_asset_info(session_id)
        return result
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取资产信息失败: {str(e)}"}
        )


@router.get("/risk/{session_id}", response_model=RiskInfo)
async def get_risk_info(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取风险信息"""
    try:
        trading_service = TradingService()
        result = trading_service.get_risk_info(session_id)
        return result
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取风险信息失败: {str(e)}"}
        )


@router.get("/strategies/{session_id}", response_model=List[StrategyInfo])
async def get_strategies(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取策略列表"""
    try:
        trading_service = TradingService()
        results = trading_service.get_strategies(session_id)
        return results
    except TradingServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取策略列表失败: {str(e)}"}
        )


@router.get("/status/{session_id}")
async def get_connection_status(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    """获取连接状态"""
    try:
        trading_service = TradingService()
        is_connected = trading_service.is_connected(session_id)
        return format_response(
            data={"connected": is_connected},
            message="连接状态查询成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"查询连接状态失败: {str(e)}"}
        )
