"""
数据服务路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.services.data_service import DataService
from app.models.data_models import (
    MarketDataRequest, FinancialDataRequest, SectorRequest,
    IndexWeightRequest, MarketDataResponse, FinancialDataResponse,
    SectorResponse, IndexWeightResponse, InstrumentInfo,
    TradingCalendarResponse, ETFInfoResponse
)
from app.utils.helpers import format_response
from app.utils.exceptions import DataServiceException, handle_xtquant_exception
from app.dependencies import verify_api_key, get_data_service
from app.config import get_settings, Settings

router = APIRouter(prefix="/api/v1/data", tags=["数据服务"])


@router.post("/market", response_model=List[MarketDataResponse])
async def get_market_data(
    request: MarketDataRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取市场数据"""
    try:
        results = data_service.get_market_data(request)
        return results
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取市场数据失败: {str(e)}"}
        )


@router.post("/financial", response_model=List[FinancialDataResponse])
async def get_financial_data(
    request: FinancialDataRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取财务数据"""
    try:
        results = data_service.get_financial_data(request)
        return results
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取财务数据失败: {str(e)}"}
        )


@router.get("/sectors", response_model=List[SectorResponse])
async def get_sector_list(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取板块列表"""
    try:
        results = data_service.get_sector_list()
        return results
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取板块列表失败: {str(e)}"}
        )


@router.post("/sector")
async def get_sector_stocks(
    request: SectorRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取板块内股票列表"""
    try:
        # 这里可以添加获取特定板块股票的逻辑
        return format_response(
            data={"sector_name": request.sector_name, "stock_list": []},
            message="获取板块股票列表成功"
        )
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取板块股票列表失败: {str(e)}"}
        )


@router.post("/index-weight", response_model=IndexWeightResponse)
async def get_index_weight(
    request: IndexWeightRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取指数权重"""
    try:
        result = data_service.get_index_weight(request)
        return result
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取指数权重失败: {str(e)}"}
        )


@router.get("/trading-calendar/{year}", response_model=TradingCalendarResponse)
async def get_trading_calendar(
    year: int,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取交易日历"""
    try:
        result = data_service.get_trading_calendar(year)
        return result
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取交易日历失败: {str(e)}"}
        )


@router.get("/instrument/{stock_code}", response_model=InstrumentInfo)
async def get_instrument_info(
    stock_code: str,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取合约信息"""
    try:
        result = data_service.get_instrument_info(stock_code)
        return result
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取合约信息失败: {str(e)}"}
        )


@router.get("/etf/{etf_code}", response_model=ETFInfoResponse)
async def get_etf_info(
    etf_code: str,
    api_key: str = Depends(verify_api_key)
):
    """获取ETF信息"""
    try:
        # 这里可以添加获取ETF信息的逻辑
        return ETFInfoResponse(
            etf_code=etf_code,
            etf_name=f"ETF{etf_code}",
            underlying_asset="沪深300",
            creation_unit=1000000,
            redemption_unit=1000000
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取ETF信息失败: {str(e)}"}
        )
