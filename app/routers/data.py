"""
数据服务路由
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.dependencies import get_data_service, verify_api_key
from app.models.data_models import (  # 阶段2: 行情数据请求模型; 阶段3: 数据下载请求模型; 阶段5: Level2请求模型; 阶段6: 订阅请求模型
    DividFactorsRequest,
    DownloadFinancialDataBatchRequest,
    DownloadFinancialDataRequest,
    DownloadHistoryContractsRequest,
    DownloadHistoryDataBatchRequest,
    DownloadHistoryDataRequest,
    DownloadIndexWeightRequest,
    ETFInfoResponse,
    FinancialDataRequest,
    FinancialDataResponse,
    FullKlineRequest,
    FullTickRequest,
    IndexWeightRequest,
    IndexWeightResponse,
    InstrumentInfo,
    L2OrderRequest,
    L2QuoteRequest,
    L2TransactionRequest,
    LocalDataRequest,
    MarketDataRequest,
    MarketDataResponse,
    SectorRequest,
    SectorResponse,
    SubscriptionRequest,
    TradingCalendarResponse,
)
from app.services.data_service import DataService
from app.utils.exceptions import DataServiceException, handle_xtquant_exception
from app.utils.helpers import format_response
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/data", tags=["数据服务"])


@router.post("/market", response_model=List[MarketDataResponse])
async def get_market_data(
    request: MarketDataRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
) -> List[MarketDataResponse]:
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
)-> List[FinancialDataResponse]:
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
) -> List[SectorResponse]:
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
        # 调用 get_sector_list 获取所有板块，或实现单独的 get_sector_stocks 方法
        # 这里先使用 get_sector_list 并过滤
        all_sectors = data_service.get_sector_list()
        
        # 查找匹配的板块
        for sector in all_sectors:
            if sector.sector_name == request.sector_name:
                return format_response(
                    data=sector.dict(),
                    message="获取板块股票列表成功"
                )
        
        # 未找到板块
        return format_response(
            data={"sector_name": request.sector_name, "stock_list": []},
            message=f"未找到板块: {request.sector_name}"
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


# ==================== 阶段1: 基础信息接口 ====================

@router.get("/instrument-type/{stock_code}")
async def get_instrument_type(
    stock_code: str,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取合约类型"""
    try:
        result = data_service.get_instrument_type(stock_code)
        return format_response(data=result, message="获取合约类型成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取合约类型失败: {str(e)}"}
        )


@router.get("/holidays")
async def get_holidays(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取节假日列表"""
    try:
        result = data_service.get_holidays()
        return format_response(data=result, message="获取节假日列表成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取节假日列表失败: {str(e)}"}
        )


@router.get("/convertible-bonds")
async def get_cb_info(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取可转债信息"""
    try:
        result = data_service.get_cb_info()
        return format_response(data=result, message="获取可转债信息成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取可转债信息失败: {str(e)}"}
        )


@router.get("/ipo-info")
async def get_ipo_info(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取新股申购信息"""
    try:
        result = data_service.get_ipo_info()
        return format_response(data=result, message="获取新股申购信息成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取新股申购信息失败: {str(e)}"}
        )


@router.get("/period-list")
async def get_period_list(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取可用周期列表"""
    try:
        result = data_service.get_period_list()
        return format_response(data=result, message="获取可用周期列表成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取可用周期列表失败: {str(e)}"}
        )


@router.get("/data-dir")
async def get_data_dir(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取本地数据路径"""
    try:
        result = data_service.get_data_dir()
        return format_response(data=result, message="获取数据路径成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取数据路径失败: {str(e)}"}
        )


# ==================== 阶段2: 行情数据获取接口 ====================

@router.post("/local-data")
async def get_local_data(
    request: LocalDataRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取本地行情数据"""
    try:
        result = data_service.get_local_data(request)
        return format_response(data=result, message="获取本地行情数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取本地行情数据失败: {str(e)}"}
        )


@router.post("/full-tick")
async def get_full_tick(
    request: FullTickRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取完整tick数据"""
    try:
        result = data_service.get_full_tick(request)
        return format_response(data=result, message="获取完整tick数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取完整tick数据失败: {str(e)}"}
        )


@router.post("/divid-factors")
async def get_divid_factors(
    request: DividFactorsRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取除权除息数据"""
    try:
        result = data_service.get_divid_factors(request.stock_code)
        return format_response(data=result, message="获取除权除息数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取除权除息数据失败: {str(e)}"}
        )


@router.post("/full-kline")
async def get_full_kline(
    request: FullKlineRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取完整K线数据（带复权信息）"""
    try:
        result = data_service.get_full_kline(request)
        return format_response(data=result, message="获取完整K线数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取完整K线数据失败: {str(e)}"}
        )


# ==================== 阶段3: 数据下载接口 ====================

@router.post("/download/history-data")
async def download_history_data(
    request: DownloadHistoryDataRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载单只股票历史数据"""
    try:
        result = data_service.download_history_data(
            request.stock_code, request.period, request.start_time, 
            request.end_time, request.incrementally
        )
        return format_response(data=result, message="下载历史数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载历史数据失败: {str(e)}"}
        )


@router.post("/download/history-data-batch")
async def download_history_data_batch(
    request: DownloadHistoryDataBatchRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """批量下载历史数据"""
    try:
        result = data_service.download_history_data_batch(
            request.stock_list, request.period, request.start_time, request.end_time
        )
        return format_response(data=result, message="批量下载历史数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"批量下载历史数据失败: {str(e)}"}
        )


@router.post("/download/financial-data")
async def download_financial_data(
    request: DownloadFinancialDataRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载财务数据"""
    try:
        # 直接传入请求模型给服务层
        result = data_service.download_financial_data(request)
        return format_response(data=result, message="下载财务数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载财务数据失败: {str(e)}"}
        )


@router.post("/download/financial-data-batch")
async def download_financial_data_batch(
    request: DownloadFinancialDataBatchRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """批量下载财务数据（带回调）"""
    try:
        result = data_service.download_financial_data_batch(request)
        return format_response(data=result, message="批量下载财务数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"批量下载财务数据失败: {str(e)}"}
        )


@router.post("/download/sector-data")
async def download_sector_data(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载板块数据"""
    try:
        result = data_service.download_sector_data()
        return format_response(data=result, message="下载板块数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载板块数据失败: {str(e)}"}
        )


@router.post("/download/index-weight")
async def download_index_weight(
    request: DownloadIndexWeightRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载指数权重数据"""
    try:
        result = data_service.download_index_weight(request)
        return format_response(data=result, message="下载指数权重数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载指数权重数据失败: {str(e)}"}
        )


@router.post("/download/cb-data")
async def download_cb_data(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载可转债数据"""
    try:
        result = data_service.download_cb_data()
        return format_response(data=result, message="下载可转债数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载可转债数据失败: {str(e)}"}
        )


@router.post("/download/etf-info")
async def download_etf_info(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载ETF基础信息"""
    try:
        result = data_service.download_etf_info()
        return format_response(data=result, message="下载ETF信息任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载ETF信息失败: {str(e)}"}
        )


@router.post("/download/holiday-data")
async def download_holiday_data(
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载节假日数据"""
    try:
        result = data_service.download_holiday_data()
        return format_response(data=result, message="下载节假日数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载节假日数据失败: {str(e)}"}
        )


@router.post("/download/history-contracts")
async def download_history_contracts(
    request: DownloadHistoryContractsRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """下载历史合约数据"""
    try:
        result = data_service.download_history_contracts(request)
        return format_response(data=result, message="下载历史合约数据任务已提交")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"下载历史合约数据失败: {str(e)}"}
        )


# ==================== 阶段4: 板块管理接口 ====================

@router.post("/sector/create-folder")
async def create_sector_folder(
    parent_node: str = "",
    folder_name: str = "",
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """创建板块文件夹"""
    try:
        result = data_service.create_sector_folder(parent_node, folder_name)
        return format_response(data={"created_name": result}, message="创建板块文件夹成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"创建板块文件夹失败: {str(e)}"}
        )


@router.post("/sector/create")
async def create_sector(
    request: dict,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """创建板块"""
    try:
        parent_node = request.get("parent_node", "")
        sector_name = request.get("sector_name", "")
        overwrite = request.get("overwrite", True)
        result = data_service.create_sector(parent_node, sector_name, overwrite)
        return format_response(data={"created_name": result}, message="创建板块成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"创建板块失败: {str(e)}"}
        )


@router.post("/sector/add-stocks")
async def add_sector(
    request: dict,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """添加股票到板块"""
    try:
        sector_name = request.get("sector_name", "")
        stock_list = request.get("stock_list", [])
        data_service.add_sector(sector_name, stock_list)
        return format_response(data=None, message="添加股票到板块成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"添加股票到板块失败: {str(e)}"}
        )


@router.post("/sector/remove-stocks")
async def remove_stock_from_sector(
    request: dict,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """从板块移除股票"""
    try:
        sector_name = request.get("sector_name", "")
        stock_list = request.get("stock_list", [])
        data_service.remove_stock_from_sector(sector_name, stock_list)
        return format_response(data=None, message="从板块移除股票成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"从板块移除股票失败: {str(e)}"}
        )


@router.post("/sector/remove")
async def remove_sector(
    sector_name: str,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """删除板块"""
    try:
        data_service.remove_sector(sector_name)
        return format_response(data=None, message="删除板块成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"删除板块失败: {str(e)}"}
        )


@router.post("/sector/reset")
async def reset_sector(
    request: dict,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """重置板块成分股"""
    try:
        sector_name = request.get("sector_name", "")
        stock_list = request.get("stock_list", [])
        data_service.reset_sector(sector_name, stock_list)
        return format_response(data=None, message="重置板块成分股成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"重置板块成分股失败: {str(e)}"}
        )


# ==================== 阶段5: Level2数据接口 ====================

@router.post("/l2/quote")
async def get_l2_quote(
    request: L2QuoteRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取Level2快照数据（10档行情）"""
    try:
        result = data_service.get_l2_quote(request.stock_codes)
        return format_response(data=result, message="获取Level2快照数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取Level2快照数据失败: {str(e)}"}
        )


@router.post("/l2/order")
async def get_l2_order(
    request: L2OrderRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取Level2逐笔委托数据"""
    try:
        result = data_service.get_l2_order(request.stock_codes)
        return format_response(data=result, message="获取Level2逐笔委托数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取Level2逐笔委托数据失败: {str(e)}"}
        )


@router.post("/l2/transaction")
async def get_l2_transaction(
    request: L2TransactionRequest,
    api_key: str = Depends(verify_api_key),
    data_service: DataService = Depends(get_data_service)
):
    """获取Level2逐笔成交数据"""
    try:
        result = data_service.get_l2_transaction(request.stock_codes)
        return format_response(data=result, message="获取Level2逐笔成交数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取Level2逐笔成交数据失败: {str(e)}"}
        )


# ==================== 阶段6: 行情订阅接口 ====================

@router.post("/subscription", response_model=dict)
async def create_subscription(
    request: SubscriptionRequest,
    api_key: str = Depends(verify_api_key),
    settings: Settings = Depends(get_settings)
):
    """
    创建行情订阅
    
    Args:
        request: 订阅请求（包含股票代码列表、复权类型等）
    
    Returns:
        订阅响应（包含subscription_id）
    """
    try:
        from app.dependencies import get_subscription_manager
        from app.models.data_models import SubscriptionType

        # 获取订阅管理器
        subscription_manager = get_subscription_manager(settings)
        
        # 根据订阅类型创建订阅
        if request.subscription_type == SubscriptionType.WHOLE_QUOTE:
            subscription_id = subscription_manager.subscribe_whole_quote()
        else:
            subscription_id = subscription_manager.subscribe_quote(
                symbols=request.symbols,
                period=request.period.value,
                adjust_type=request.adjust_type
            )
        
        # 构造响应
        response = {
            "subscription_id": subscription_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "symbols": request.symbols if request.subscription_type == SubscriptionType.QUOTE else ["*"],
            "period": request.period.value,
            "subscription_type": request.subscription_type.value,
            "message": "订阅创建成功"
        }
        
        logger.info(f"创建订阅成功: {subscription_id}")
        return response
    
    except DataServiceException as e:
        raise handle_xtquant_exception(e)
    except Exception as e:
        logger.error(f"创建订阅失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"创建订阅失败: {str(e)}"}
        )


@router.delete("/subscription/{subscription_id}")
async def delete_subscription(
    subscription_id: str,
    api_key: str = Depends(verify_api_key),
    settings: Settings = Depends(get_settings)
):
    """
    取消订阅
    
    Args:
        subscription_id: 订阅ID
    
    Returns:
        取消结果
    """
    try:
        from app.dependencies import get_subscription_manager

        # 获取订阅管理器
        subscription_manager = get_subscription_manager(settings)
        
        # 取消订阅
        success = subscription_manager.unsubscribe(subscription_id)
        
        logger.info(f"取消订阅: {subscription_id}, 结果: {success}")
        
        return {
            "success": success,
            "message": "订阅已取消" if success else "订阅不存在",
            "subscription_id": subscription_id
        }
    
    except Exception as e:
        logger.error(f"取消订阅失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"取消订阅失败: {str(e)}"}
        )


@router.get("/subscription/{subscription_id}")
async def get_subscription_info(
    subscription_id: str,
    api_key: str = Depends(verify_api_key),
    settings: Settings = Depends(get_settings)
):
    """
    获取订阅信息
    
    Args:
        subscription_id: 订阅ID
    
    Returns:
        订阅详细信息
    """
    try:
        from app.dependencies import get_subscription_manager

        # 获取订阅管理器
        subscription_manager = get_subscription_manager(settings)
        
        # 获取订阅信息
        info = subscription_manager.get_subscription_info(subscription_id)
        
        if not info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": f"订阅不存在: {subscription_id}"}
            )
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取订阅信息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"获取订阅信息失败: {str(e)}"}
        )


@router.get("/subscriptions")
async def list_subscriptions(
    api_key: str = Depends(verify_api_key),
    settings: Settings = Depends(get_settings)
):
    """
    列出所有订阅
    
    Returns:
        所有订阅列表
    """
    try:
        from app.dependencies import get_subscription_manager

        # 获取订阅管理器
        subscription_manager = get_subscription_manager(settings)
        
        # 列出所有订阅
        subscriptions = subscription_manager.list_subscriptions()
        
        return {
            "subscriptions": subscriptions,
            "total": len(subscriptions)
        }
    
    except Exception as e:
        logger.error(f"列出订阅失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": f"列出订阅失败: {str(e)}"}
        )
