"""
数据服务接口测试

测试所有数据服务相关的 API 端点
"""

import pytest
import httpx
from datetime import datetime, timedelta
from tests.rest.client import RESTTestClient


class TestDataAPI:
    """数据服务接口测试类"""
    
    def test_get_market_data(self, http_client: httpx.Client, sample_stock_codes, sample_date_range):
        """测试获取市场数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": sample_stock_codes[:2],  # 只测试前两个
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
            "fields": ["time", "open", "high", "low", "close", "volume"]
        }
        
        response = http_client.post("/api/v1/data/market", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "market_data" in result
    
    def test_get_sector_list(self, http_client: httpx.Client):
        """测试获取板块列表"""
        response = http_client.get("/api/v1/data/sectors")
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "sectors" in result
    
    def test_get_stock_list_in_sector(self, http_client: httpx.Client, sample_sector_names):
        """测试获取板块股票"""
        data = {"sector_name": sample_sector_names[0]}
        
        response = http_client.post("/api/v1/data/sector", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "stocks" in result
    
    def test_get_index_weight(self, http_client: httpx.Client, sample_index_codes):
        """测试获取指数权重"""
        data = {
            "index_code": sample_index_codes[1],  # 沪深300
            "date": None  # 最新权重
        }
        
        response = http_client.post("/api/v1/data/index-weight", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "weights" in result
    
    def test_get_trading_calendar(self, http_client: httpx.Client):
        """测试获取交易日历"""
        year = datetime.now().year
        
        response = http_client.get(f"/api/v1/data/trading-calendar/{year}")
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "calendar" in result
    
    def test_get_instrument_info(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取合约信息"""
        stock_code = sample_stock_codes[0]
        
        response = http_client.get(f"/api/v1/data/instrument/{stock_code}")
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "instrument" in result
    
    def test_get_financial_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取财务数据"""
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "table_list": ["Capital"],
            "start_date": "20230101",
            "end_date": "20241231"
        }
        
        response = http_client.post("/api/v1/data/financial", json=data)
        assert response.status_code == 200
        
        result = response.json()
        assert "data" in result or "financial_data" in result


class TestDataAPIWithClient:
    """使用封装客户端的数据服务测试"""
    
    @pytest.fixture
    def client(self, base_url: str, api_key: str):
        """创建测试客户端"""
        with RESTTestClient(base_url=base_url, api_key=api_key) as client:
            yield client
    
    def test_market_data_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取市场数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        response = client.get_market_data(
            stock_codes=sample_stock_codes[:2],
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            period="1d",
            fields=["time", "open", "high", "low", "close", "volume"]
        )
        
        result = client.assert_success(response)
        assert "data" in result or "market_data" in result
    
    def test_sector_list_with_client(self, client: RESTTestClient):
        """使用客户端测试获取板块列表"""
        response = client.get_sector_list()
        result = client.assert_success(response)
        assert "data" in result or "sectors" in result
    
    def test_stock_list_in_sector_with_client(self, client: RESTTestClient, sample_sector_names):
        """使用客户端测试获取板块股票"""
        response = client.get_stock_list_in_sector(sector_name=sample_sector_names[0])
        result = client.assert_success(response)
        assert "data" in result or "stocks" in result
    
    def test_index_weight_with_client(self, client: RESTTestClient, sample_index_codes):
        """使用客户端测试获取指数权重"""
        response = client.get_index_weight(index_code=sample_index_codes[1])
        result = client.assert_success(response)
        assert "data" in result or "weights" in result
    
    def test_trading_calendar_with_client(self, client: RESTTestClient):
        """使用客户端测试获取交易日历"""
        year = datetime.now().year
        response = client.get_trading_calendar(year=year)
        result = client.assert_success(response)
        assert "data" in result or "calendar" in result
    
    def test_instrument_info_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取合约信息"""
        response = client.get_instrument_info(stock_code=sample_stock_codes[0])
        result = client.assert_success(response)
        assert "data" in result or "instrument" in result
    
    def test_financial_data_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取财务数据"""
        response = client.get_financial_data(
            stock_codes=[sample_stock_codes[0]],
            table_list=["Capital"],
            start_date="20230101",
            end_date="20241231"
        )
        result = client.assert_success(response)
        assert "data" in result or "financial_data" in result


@pytest.mark.performance
class TestDataAPIPerformance:
    """数据服务接口性能测试"""
    
    def test_single_stock_data_performance(self, http_client: httpx.Client, sample_stock_codes, performance_timer):
        """测试单只股票行情查询性能"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
        }
        
        performance_timer.start()
        response = http_client.post("/api/v1/data/market", json=data)
        elapsed = performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["single_stock_data"], \
            f"单股行情查询耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['single_stock_data']}ms"
    
    @pytest.mark.slow
    def test_batch_stock_data_performance(self, http_client: httpx.Client, sample_stock_codes, performance_timer):
        """测试批量股票行情查询性能"""
        from tests.rest.config import PERFORMANCE_BENCHMARKS
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": sample_stock_codes,
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
        }
        
        performance_timer.start()
        response = http_client.post("/api/v1/data/market", json=data)
        elapsed = performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed_ms() < PERFORMANCE_BENCHMARKS["batch_stock_data"], \
            f"批量行情查询耗时 {performance_timer.elapsed_ms():.2f}ms，超过基准 {PERFORMANCE_BENCHMARKS['batch_stock_data']}ms"


@pytest.mark.integration
class TestDataAPIIntegration:
    """数据服务接口集成测试"""
    
    def test_complete_data_workflow(self, http_client: httpx.Client, sample_sector_names):
        """测试完整的数据查询工作流"""
        # 1. 获取板块列表
        response = http_client.get("/api/v1/data/sectors")
        assert response.status_code == 200
        
        # 2. 获取板块成分股
        data = {"sector_name": sample_sector_names[0]}
        response = http_client.post("/api/v1/data/sector", json=data)
        assert response.status_code == 200
        
        result = response.json()
        if "data" in result and result["data"]:
            stocks = result["data"]
            if stocks:
                # 3. 获取第一只股票的行情
                end_date = datetime.now()
                start_date = end_date - timedelta(days=5)
                
                market_data = {
                    "stock_codes": [stocks[0]] if isinstance(stocks[0], str) else [stocks[0].get("stock_code", "000001.SZ")],
                    "start_date": start_date.strftime("%Y%m%d"),
                    "end_date": end_date.strftime("%Y%m%d"),
                    "period": "1d",
                }
                
                response = http_client.post("/api/v1/data/market", json=market_data)
                assert response.status_code == 200
