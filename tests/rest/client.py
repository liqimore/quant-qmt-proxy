"""
REST API 测试客户端封装

提供易用的 REST API 测试客户端，简化测试代码
"""

import httpx
from typing import Dict, Any, List, Optional
import logging


class RESTTestClient:
    """
    REST API 测试客户端
    
    封装了所有 REST API 调用，提供统一的接口和错误处理
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "dev-api-key-001", timeout: int = 60):
        """
        初始化测试客户端
        
        Args:
            base_url: REST API 基础 URL
            api_key: API 认证密钥
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # 创建 HTTP 客户端
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout
        )
    
    def close(self):
        """关闭客户端"""
        self.client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
    
    # ==================== 健康检查接口 ====================
    
    def get_root(self) -> httpx.Response:
        """GET / - 根路径"""
        return self.client.get("/")
    
    def get_info(self) -> httpx.Response:
        """GET /info - 应用信息"""
        return self.client.get("/info")
    
    def check_health(self) -> httpx.Response:
        """GET /health/ - 健康检查"""
        return self.client.get("/health/")
    
    def check_ready(self) -> httpx.Response:
        """GET /health/ready - 就绪检查"""
        return self.client.get("/health/ready")
    
    def check_live(self) -> httpx.Response:
        """GET /health/live - 存活检查"""
        return self.client.get("/health/live")
    
    # ==================== 数据服务接口 ====================
    
    def get_market_data(
        self,
        stock_codes: List[str],
        start_date: str,
        end_date: str,
        period: str = "1d",
        fields: Optional[List[str]] = None
    ) -> httpx.Response:
        """
        POST /api/v1/data/market - 获取市场数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (1m, 5m, 1d 等)
            fields: 字段列表
        """
        data = {
            "stock_codes": stock_codes,
            "start_date": start_date,
            "end_date": end_date,
            "period": period,
        }
        if fields:
            data["fields"] = fields
        
        return self.client.post("/api/v1/data/market", json=data)
    
    def get_sector_list(self) -> httpx.Response:
        """GET /api/v1/data/sectors - 获取板块列表"""
        return self.client.get("/api/v1/data/sectors")
    
    def get_stock_list_in_sector(self, sector_name: str) -> httpx.Response:
        """
        POST /api/v1/data/sector - 获取板块股票
        
        Args:
            sector_name: 板块名称
        """
        data = {"sector_name": sector_name}
        return self.client.post("/api/v1/data/sector", json=data)
    
    def get_index_weight(self, index_code: str, date: Optional[str] = None) -> httpx.Response:
        """
        POST /api/v1/data/index-weight - 获取指数权重
        
        Args:
            index_code: 指数代码
            date: 日期 (YYYYMMDD)，None 表示最新
        """
        data = {
            "index_code": index_code,
            "date": date
        }
        return self.client.post("/api/v1/data/index-weight", json=data)
    
    def get_trading_calendar(self, year: int) -> httpx.Response:
        """
        GET /api/v1/data/trading-calendar/{year} - 获取交易日历
        
        Args:
            year: 年份
        """
        return self.client.get(f"/api/v1/data/trading-calendar/{year}")
    
    def get_instrument_info(self, stock_code: str) -> httpx.Response:
        """
        GET /api/v1/data/instrument/{stock_code} - 获取合约信息
        
        Args:
            stock_code: 股票代码
        """
        return self.client.get(f"/api/v1/data/instrument/{stock_code}")
    
    def get_financial_data(
        self,
        stock_codes: List[str],
        table_list: List[str],
        start_date: str,
        end_date: str
    ) -> httpx.Response:
        """
        POST /api/v1/data/financial - 获取财务数据
        
        Args:
            stock_codes: 股票代码列表
            table_list: 财务报表列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        """
        data = {
            "stock_codes": stock_codes,
            "table_list": table_list,
            "start_date": start_date,
            "end_date": end_date
        }
        return self.client.post("/api/v1/data/financial", json=data)
    
    # ==================== 交易服务接口 ====================
    
    def connect(
        self,
        account_id: str,
        password: str,
        account_type: str = "SECURITY"
    ) -> httpx.Response:
        """
        POST /api/v1/trading/connect - 连接交易账户
        
        Args:
            account_id: 账户ID
            password: 密码
            account_type: 账户类型
        """
        data = {
            "account_id": account_id,
            "password": password,
            "account_type": account_type
        }
        return self.client.post("/api/v1/trading/connect", json=data)
    
    def disconnect(self, session_id: str) -> httpx.Response:
        """
        POST /api/v1/trading/disconnect/{session_id} - 断开账户
        
        Args:
            session_id: 会话ID
        """
        return self.client.post(f"/api/v1/trading/disconnect/{session_id}")
    
    def get_account_info(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/account/{session_id} - 获取账户信息
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/account/{session_id}")
    
    def get_positions(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/positions/{session_id} - 获取持仓信息
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/positions/{session_id}")
    
    def get_asset(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/asset/{session_id} - 获取资产信息
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/asset/{session_id}")
    
    def get_risk(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/risk/{session_id} - 获取风险信息
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/risk/{session_id}")
    
    def get_strategies(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/strategies/{session_id} - 获取策略列表
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/strategies/{session_id}")
    
    def get_orders(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/orders/{session_id} - 获取订单列表
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/orders/{session_id}")
    
    def get_trades(self, session_id: str) -> httpx.Response:
        """
        GET /api/v1/trading/trades/{session_id} - 获取成交记录
        
        Args:
            session_id: 会话ID
        """
        return self.client.get(f"/api/v1/trading/trades/{session_id}")
    
    def submit_order(
        self,
        session_id: str,
        stock_code: str,
        side: str,
        volume: int,
        price: Optional[float] = None,
        order_type: str = "LIMIT"
    ) -> httpx.Response:
        """
        POST /api/v1/trading/order/{session_id} - 提交订单
        
        Args:
            session_id: 会话ID
            stock_code: 股票代码
            side: 买卖方向 (BUY/SELL)
            volume: 数量
            price: 价格（市价单可为 None）
            order_type: 订单类型 (LIMIT/MARKET)
        """
        data = {
            "stock_code": stock_code,
            "side": side,
            "volume": volume,
            "order_type": order_type
        }
        if price is not None:
            data["price"] = price
        
        return self.client.post(f"/api/v1/trading/order/{session_id}", json=data)
    
    def cancel_order(self, session_id: str, order_id: str) -> httpx.Response:
        """
        POST /api/v1/trading/cancel/{session_id} - 撤销订单
        
        Args:
            session_id: 会话ID
            order_id: 订单ID
        """
        data = {"order_id": order_id}
        return self.client.post(f"/api/v1/trading/cancel/{session_id}", json=data)
    
    # ==================== 辅助方法 ====================
    
    def assert_success(self, response: httpx.Response, expected_status: int = 200) -> Dict[str, Any]:
        """
        断言响应成功并返回结果
        
        Args:
            response: HTTP 响应
            expected_status: 期望的状态码
        
        Returns:
            响应 JSON 数据
        
        Raises:
            AssertionError: 如果响应失败
        """
        assert response.status_code == expected_status, \
            f"请求失败: HTTP {response.status_code}, {response.text[:200]}"
        
        result = response.json()
        
        # 某些端点可能没有 success 字段
        if "success" in result:
            assert result.get("success") is not False, \
                f"API 返回失败: {result.get('message', 'Unknown error')}"
        
        return result
    
    def log_response(self, response: httpx.Response, name: str = "API"):
        """
        记录响应信息
        
        Args:
            response: HTTP 响应
            name: 请求名称
        """
        self.logger.info(f"{name} - Status: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                self.logger.debug(f"{name} - Response: {result}")
            except Exception:
                self.logger.debug(f"{name} - Response: {response.text[:200]}")
        else:
            self.logger.error(f"{name} - Error: {response.text[:200]}")
