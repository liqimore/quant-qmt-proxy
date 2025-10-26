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
        print("\n" + "="*80)
        print("📊 市场数据测试 - 完整响应信息:")
        print("="*80)
        
        # 提取第一条数据
        first_data = None
        if isinstance(result, list) and len(result) > 0:
            first_data = result[0]
            print(f"✓ 返回类型: list, 数据条数: {len(result)}")
        elif isinstance(result, dict):
            if "data" in result and result["data"]:
                first_data = result["data"][0] if isinstance(result["data"], list) else result["data"]
                print(f"✓ 返回类型: dict (data字段), 数据条数: {len(result.get('data', []))}")
            elif "market_data" in result and result["market_data"]:
                first_data = result["market_data"][0] if isinstance(result["market_data"], list) else result["market_data"]
                print(f"✓ 返回类型: dict (market_data字段), 数据条数: {len(result.get('market_data', []))}")
        
        # 打印第一条完整数据
        if first_data:
            print(f"\n📋 第一条数据完整内容:")
            import json
            print(json.dumps(first_data, indent=2, ensure_ascii=False))
            
            # 验证数据合理性
            print(f"\n✓ 数据合理性验证:")
            
            # 检查股票代码
            stock_code = first_data.get("stock_code")
            if stock_code:
                print(f"  - 股票代码: {stock_code} ✓")
                assert stock_code in sample_stock_codes[:2], f"股票代码 {stock_code} 不在请求列表中"
            
            # 检查数据字段
            data_items = first_data.get("data", [])
            if data_items:
                first_item = data_items[0] if isinstance(data_items, list) else data_items
                print(f"  - K线数据条数: {len(data_items) if isinstance(data_items, list) else 1}")
                print(f"  - 第一条K线数据: {first_item}")
                
                # 验证必需字段
                required_fields = ["time", "open", "high", "low", "close", "volume"]
                for field in required_fields:
                    assert field in first_item, f"缺少必需字段: {field}"
                    value = first_item[field]
                    print(f"  - {field}: {value} ✓")
                
                # 验证价格合理性
                if all(k in first_item for k in ["open", "high", "low", "close"]):
                    assert first_item["high"] >= first_item["low"], "最高价应该 >= 最低价"
                    assert first_item["high"] >= first_item["open"], "最高价应该 >= 开盘价"
                    assert first_item["high"] >= first_item["close"], "最高价应该 >= 收盘价"
                    assert first_item["low"] <= first_item["open"], "最低价应该 <= 开盘价"
                    assert first_item["low"] <= first_item["close"], "最低价应该 <= 收盘价"
                    print(f"  - 价格逻辑验证: OHLC关系正确 ✓")
                
                # 验证成交量
                if "volume" in first_item:
                    assert first_item["volume"] >= 0, "成交量应该 >= 0"
                    print(f"  - 成交量验证: 非负数 ✓")
        else:
            print("⚠️  未找到数据，可能是空结果")
        
        print("="*80)
    
    def test_get_sector_list(self, http_client: httpx.Client):
        """测试获取板块列表"""
        response = http_client.get("/api/v1/data/sectors")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🏢 板块列表测试 - 完整响应信息:")
        print("="*80)
        
        # 提取第一条数据
        first_sector = None
        total_count = 0
        
        if isinstance(result, list) and len(result) > 0:
            first_sector = result[0]
            total_count = len(result)
            print(f"✓ 返回类型: list, 板块数量: {total_count}")
        elif isinstance(result, dict):
            if "data" in result and result["data"]:
                data = result["data"]
                if isinstance(data, list) and len(data) > 0:
                    first_sector = data[0]
                    total_count = len(data)
                    print(f"✓ 返回类型: dict (data字段), 板块数量: {total_count}")
        
        # 打印第一条板块信息
        if first_sector:
            import json
            print(f"\n📋 第一个板块完整信息:")
            print(json.dumps(first_sector, indent=2, ensure_ascii=False))
            
            # 验证数据合理性
            print(f"\n✓ 数据合理性验证:")
            
            # 检查板块名称
            sector_name = first_sector.get("sector_name")
            if sector_name:
                print(f"  - 板块名称: {sector_name} ✓")
                assert isinstance(sector_name, str) and len(sector_name) > 0, "板块名称应为非空字符串"
            
            # 检查股票列表
            stock_list = first_sector.get("stock_list", [])
            if stock_list:
                print(f"  - 成分股数量: {len(stock_list)}")
                print(f"  - 前3个成分股: {stock_list[:3]} ✓")
                assert isinstance(stock_list, list), "股票列表应为数组"
                # 验证股票代码格式
                if len(stock_list) > 0:
                    first_stock = stock_list[0]
                    if isinstance(first_stock, str):
                        assert "." in first_stock, "股票代码应包含市场后缀 (如.SH, .SZ)"
                        print(f"  - 股票代码格式: 正确 (示例: {first_stock}) ✓")
            
            # 检查板块类型
            sector_type = first_sector.get("sector_type")
            if sector_type:
                print(f"  - 板块类型: {sector_type} ✓")
        else:
            print("⚠️  未找到板块数据")
        
        print("="*80)
    
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
        print("\n" + "="*80)
        print(f"📅 交易日历测试 - {year}年:")
        print("="*80)
        
        # 打印完整数据
        import json
        print(f"\n完整数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证数据合理性
        print(f"\n✓ 数据合理性验证:")
        
        trading_dates = []
        holidays = []
        
        if isinstance(result, dict):
            trading_dates = result.get("trading_dates", [])
            holidays = result.get("holidays", [])
            year_field = result.get("year")
            
            if year_field:
                print(f"  - 年份: {year_field} ✓")
                assert year_field == year, f"返回年份({year_field})与请求年份({year})不符"
        
        if trading_dates:
            print(f"  - 交易日总数: {len(trading_dates)}")
            print(f"  - 前5个交易日: {trading_dates[:5]}")
            assert len(trading_dates) > 200, f"交易日数量({len(trading_dates)})异常，应该在200-250之间"
            assert len(trading_dates) < 260, f"交易日数量({len(trading_dates)})异常，应该在200-250之间"
            print(f"  - 交易日数量合理 (200-260天) ✓")
            
            # 验证日期格式
            first_date = trading_dates[0]
            assert len(str(first_date)) == 8, "日期格式应为YYYYMMDD (8位)"
            assert str(year) in str(first_date), f"日期应属于{year}年"
            print(f"  - 日期格式: YYYYMMDD ✓")
        
        if holidays:
            print(f"  - 非交易日总数: {len(holidays)}")
            print(f"  - 前5个非交易日: {holidays[:5]}")
            assert len(holidays) > 100, f"非交易日数量({len(holidays)})异常"
            print(f"  - 非交易日数量合理 ✓")
        
        # 验证交易日和非交易日总数应该等于一年的天数
        if trading_dates and holidays:
            total_days = len(trading_dates) + len(holidays)
            expected_days = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365
            assert total_days == expected_days, f"交易日({len(trading_dates)}) + 非交易日({len(holidays)}) = {total_days}，应等于{expected_days}"
            print(f"  - 日期完整性: 交易日 + 非交易日 = {total_days}天 ✓")
        
        print("="*80)
    
    def test_get_instrument_info(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取合约信息"""
        stock_code = sample_stock_codes[0]
        
        response = http_client.get(f"/api/v1/data/instrument/{stock_code}")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📋 合约信息测试 - 完整响应信息:")
        print("="*80)
        print(f"请求股票代码: {stock_code}")
        
        # 打印完整数据
        import json
        print(f"\n完整数据:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证数据合理性
        print(f"\n✓ 数据合理性验证:")
        
        # 检查必需字段
        if "InstrumentID" in result or "instrument_code" in result:
            code = result.get("InstrumentID") or result.get("instrument_code")
            print(f"  - 合约代码: {code} ✓")
            # 验证代码匹配（可能不包含市场后缀）
            code_without_market = stock_code.split('.')[0]  # 提取代码部分，如 "000001"
            assert code_without_market in str(code) or stock_code == str(code), \
                f"返回的合约代码({code})与请求({stock_code})不符"
        
        if "InstrumentName" in result or "instrument_name" in result:
            name = result.get("InstrumentName") or result.get("instrument_name")
            print(f"  - 合约名称: {name} ✓")
            assert name is not None and len(str(name)) > 0, "合约名称不应为空"
        
        # 检查价格字段（如果有）
        if "UpStopPrice" in result and result["UpStopPrice"]:
            print(f"  - 涨停价: {result['UpStopPrice']} ✓")
            assert result["UpStopPrice"] > 0, "涨停价应该大于0"
        
        if "DownStopPrice" in result and result["DownStopPrice"]:
            print(f"  - 跌停价: {result['DownStopPrice']} ✓")
            assert result["DownStopPrice"] > 0, "跌停价应该大于0"
            
        # 验证涨跌停价格关系
        if result.get("UpStopPrice") and result.get("DownStopPrice"):
            assert result["UpStopPrice"] > result["DownStopPrice"], "涨停价应该大于跌停价"
            print(f"  - 涨跌停价格关系: 正确 ✓")
        
        # 检查股本字段（如果有）
        if "TotalVolume" in result and result["TotalVolume"]:
            print(f"  - 总股本: {result['TotalVolume']} ✓")
            assert result["TotalVolume"] > 0, "总股本应该大于0"
        
        if "FloatVolume" in result and result["FloatVolume"]:
            print(f"  - 流通股本: {result['FloatVolume']} ✓")
            assert result["FloatVolume"] > 0, "流通股本应该大于0"
            
        # 验证流通股本不大于总股本
        if result.get("TotalVolume") and result.get("FloatVolume"):
            assert result["FloatVolume"] <= result["TotalVolume"], "流通股本不应大于总股本"
            print(f"  - 股本关系: 流通股本 <= 总股本 ✓")
        
        print("="*80)
    
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
        print("\n" + "="*80)
        print("💰 财务数据测试 - 完整响应信息:")
        print("="*80)
        print(f"请求股票: {sample_stock_codes[0]}, 财务表: Capital")
        
        # 提取第一条数据
        first_data = None
        if isinstance(result, list) and len(result) > 0:
            first_data = result[0]
            print(f"✓ 返回类型: list, 数据条数: {len(result)}")
        elif isinstance(result, dict) and "data" in result and result["data"]:
            first_data = result["data"][0] if isinstance(result["data"], list) else result["data"]
            print(f"✓ 返回类型: dict")
        
        # 打印第一条完整数据
        if first_data:
            import json
            print(f"\n📋 第一条数据完整内容:")
            print(json.dumps(first_data, indent=2, ensure_ascii=False))
            
            # 验证数据合理性
            print(f"\n✓ 数据合理性验证:")
            
            # 检查股票代码
            if "stock_code" in first_data:
                print(f"  - 股票代码: {first_data['stock_code']} ✓")
                assert first_data["stock_code"] == sample_stock_codes[0]
            
            # 检查表名
            if "table_name" in first_data:
                print(f"  - 财务表: {first_data['table_name']} ✓")
                assert first_data["table_name"] == "Capital"
            
            # 检查财务数据
            if "data" in first_data and first_data["data"]:
                financial_items = first_data["data"]
                item_count = len(financial_items) if isinstance(financial_items, list) else 1
                print(f"  - 财务记录数: {item_count}")
                
                if isinstance(financial_items, list) and len(financial_items) > 0:
                    first_item = financial_items[0]
                    print(f"  - 第一条财务记录: {first_item}")
                    
                    # 验证股本表字段
                    if "total_capital" in first_item:
                        print(f"  - 总股本: {first_item['total_capital']} ✓")
                        assert first_item["total_capital"] > 0, "总股本应该大于0"
                    
                    if "circulating_capital" in first_item:
                        print(f"  - 流通股本: {first_item['circulating_capital']} ✓")
                        assert first_item["circulating_capital"] > 0, "流通股本应该大于0"
                    
                    # 验证流通股本不大于总股本
                    if "total_capital" in first_item and "circulating_capital" in first_item:
                        total = first_item["total_capital"]
                        circulating = first_item["circulating_capital"]
                        assert circulating <= total, f"流通股本({circulating})不应大于总股本({total})"
                        print(f"  - 股本关系: 流通股本 <= 总股本 ✓")
                    
                    # 检查日期字段
                    if "m_timetag" in first_item or "m_anntime" in first_item:
                        date_field = first_item.get("m_timetag") or first_item.get("m_anntime")
                        print(f"  - 日期信息: {date_field} ✓")
        else:
            print("⚠️  未找到财务数据，可能是空结果或时间范围内无数据")
        
        print("="*80)


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
        
        print("\n" + "="*80)
        print("📊 [客户端] 市场数据测试:")
        print("="*80)
        
        # 打印第一条数据
        if isinstance(result, list) and len(result) > 0:
            first_data = result[0]
            import json
            print(json.dumps(first_data, indent=2, ensure_ascii=False))
            
            # 基本验证
            if "data" in first_data and first_data["data"]:
                k_data = first_data["data"][0] if isinstance(first_data["data"], list) else first_data["data"]
                print(f"\n✓ K线字段验证:")
                for field in ["time", "open", "high", "low", "close", "volume"]:
                    assert field in k_data, f"缺少字段: {field}"
                    print(f"  - {field}: {k_data[field]} ✓")
        
        print("="*80)
    
    def test_sector_list_with_client(self, client: RESTTestClient):
        """使用客户端测试获取板块列表"""
        response = client.get_sector_list()
        result = client.assert_success(response)
        assert isinstance(result, (list, dict))
    
    def test_stock_list_in_sector_with_client(self, client: RESTTestClient, sample_sector_names):
        """使用客户端测试获取板块股票"""
        response = client.get_stock_list_in_sector(sector_name=sample_sector_names[0])
        result = client.assert_success(response)
        assert result is not None
    
    def test_index_weight_with_client(self, client: RESTTestClient, sample_index_codes):
        """使用客户端测试获取指数权重"""
        response = client.get_index_weight(index_code=sample_index_codes[1])
        result = client.assert_success(response)
        assert result is not None
    
    def test_trading_calendar_with_client(self, client: RESTTestClient):
        """使用客户端测试获取交易日历"""
        year = datetime.now().year
        response = client.get_trading_calendar(year=year)
        result = client.assert_success(response)
        assert isinstance(result, (list, dict))
    
    def test_instrument_info_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取合约信息"""
        response = client.get_instrument_info(stock_code=sample_stock_codes[0])
        result = client.assert_success(response)
        
        print("\n" + "="*80)
        print("📋 [客户端] 合约信息测试:")
        print("="*80)
        print(f"股票代码: {sample_stock_codes[0]}")
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证关键字段
        print(f"\n✓ 关键字段验证:")
        if "InstrumentName" in result or "instrument_name" in result:
            name = result.get("InstrumentName") or result.get("instrument_name")
            print(f"  - 合约名称: {name} ✓")
        
        # 检查是否包含新增的完整字段
        extended_fields = ["UpStopPrice", "DownStopPrice", "TotalVolume", "FloatVolume"]
        found_extended = [f for f in extended_fields if f in result and result[f] is not None]
        if found_extended:
            print(f"  - 扩展字段: {found_extended} ✓")
        
        print("="*80)
    
    def test_financial_data_with_client(self, client: RESTTestClient, sample_stock_codes):
        """使用客户端测试获取财务数据"""
        response = client.get_financial_data(
            stock_codes=[sample_stock_codes[0]],
            table_list=["Capital"],
            start_date="20230101",
            end_date="20241231"
        )
        result = client.assert_success(response)
        assert result is not None


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
    
    def test_complete_data_workflow(self, http_client: httpx.Client, sample_sector_names, sample_stock_codes):
        """测试完整的数据查询工作流"""
        # 1. 获取板块列表
        response = http_client.get("/api/v1/data/sectors")
        assert response.status_code == 200
        
        # 2. 获取板块成分股
        data = {"sector_name": sample_sector_names[0]}
        response = http_client.post("/api/v1/data/sector", json=data)
        assert response.status_code == 200
        
        result = response.json()
        
        # 获取股票列表，支持多种响应格式
        stocks = []
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                # 如果data是字典，尝试获取stock_list字段
                stocks = data_obj.get("stock_list", []) or data_obj.get("stocks", [])
            elif isinstance(data_obj, list):
                # 如果data是列表，直接使用
                stocks = data_obj
        elif "stocks" in result:
            stocks = result["stocks"]
        
        # 如果板块接口没有返回股票，使用样本股票进行测试
        if not stocks:
            stocks = sample_stock_codes[:1]
        
        # 3. 获取第一只股票的行情
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        # 处理股票代码格式（可能是字符串或字典）
        first_stock = stocks[0]
        stock_code = first_stock if isinstance(first_stock, str) else first_stock.get("stock_code", sample_stock_codes[0])
        
        market_data = {
            "stock_codes": [stock_code],
            "start_date": start_date.strftime("%Y%m%d"),
            "end_date": end_date.strftime("%Y%m%d"),
            "period": "1d",
        }
        
        response = http_client.post("/api/v1/data/market", json=market_data)
        assert response.status_code == 200


# ==================== 新增接口测试：阶段1-5 ====================

class TestNewDataAPI:
    """新增数据服务接口测试类"""
    
    # ===== 阶段1: 基础信息接口测试 =====
    
    def test_get_instrument_type(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取合约类型"""
        stock_code = sample_stock_codes[0]
        
        response = http_client.get(f"/api/v1/data/instrument-type/{stock_code}")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 合约类型测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证响应格式
        if "data" in result:
            data = result["data"]
            assert "stock_code" in data
            assert data["stock_code"] == stock_code
            
            # 至少有一个类型为True
            type_fields = ["index", "stock", "fund", "etf", "bond", "option", "futures"]
            has_type = any(data.get(field, False) for field in type_fields)
            assert has_type, "至少应有一个合约类型为True"
            
            print(f"\n✓ 合约类型: {[k for k in type_fields if data.get(k)]}")
        
        print("="*80)
    
    def test_get_holidays(self, http_client: httpx.Client):
        """测试获取节假日列表"""
        response = http_client.get("/api/v1/data/holidays")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🎊 节假日列表测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "data" in result:
            data = result["data"]
            if "holidays" in data:
                holidays = data["holidays"]
                assert isinstance(holidays, list)
                print(f"\n✓ 节假日数量: {len(holidays)}")
                if len(holidays) > 0:
                    print(f"✓ 前5个节假日: {holidays[:5]}")
                    # 验证日期格式
                    assert len(str(holidays[0])) == 8, "日期格式应为YYYYMMDD"
        
        print("="*80)
    
    def test_get_cb_info(self, http_client: httpx.Client):
        """测试获取可转债信息"""
        response = http_client.get("/api/v1/data/convertible-bonds")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🔄 可转债信息测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])  # 只打印前1000字符
        
        if "data" in result:
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                first_cb = data[0]
                assert "bond_code" in first_cb
                print(f"\n✓ 可转债数量: {len(data)}")
                print(f"✓ 第一只可转债代码: {first_cb.get('bond_code')}")
                print(f"✓ 第一只可转债名称: {first_cb.get('bond_name')}")
        
        print("="*80)
    
    def test_get_ipo_info(self, http_client: httpx.Client):
        """测试获取新股申购信息"""
        response = http_client.get("/api/v1/data/ipo-info")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🆕 新股申购信息测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        
        if "data" in result:
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                first_ipo = data[0]
                assert "security_code" in first_ipo
                print(f"\n✓ 新股数量: {len(data)}")
                print(f"✓ 第一只新股代码: {first_ipo.get('security_code')}")
                print(f"✓ 第一只新股名称: {first_ipo.get('code_name')}")
        
        print("="*80)
    
    def test_get_period_list(self, http_client: httpx.Client):
        """测试获取可用周期列表"""
        response = http_client.get("/api/v1/data/period-list")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📅 可用周期列表测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "data" in result:
            data = result["data"]
            if "periods" in data:
                periods = data["periods"]
                assert isinstance(periods, list)
                assert len(periods) > 0
                print(f"\n✓ 可用周期: {periods}")
                # 常见周期应该包含在内
                common_periods = ["1m", "5m", "1d"]
                for period in common_periods:
                    if period in periods:
                        print(f"✓ 包含常用周期: {period}")
        
        print("="*80)
    
    def test_get_data_dir(self, http_client: httpx.Client):
        """测试获取本地数据路径"""
        response = http_client.get("/api/v1/data/data-dir")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📁 本地数据路径测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "data" in result:
            data = result["data"]
            if "data_dir" in data:
                data_dir = data["data_dir"]
                assert isinstance(data_dir, str)
                assert len(data_dir) > 0
                print(f"\n✓ 数据路径: {data_dir}")
        
        print("="*80)
    
    # ===== 阶段2: 行情数据获取接口测试 =====
    
    def test_get_local_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取本地行情数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": sample_stock_codes[:2],
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d"),
            "period": "1d"
        }
        
        response = http_client.post("/api/v1/data/local-data", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 本地行情数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1500])
        
        print("="*80)
    
    def test_get_full_tick(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取完整tick数据"""
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "start_time": "",
            "end_time": ""
        }
        
        response = http_client.post("/api/v1/data/full-tick", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("⏱️  完整Tick数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1500])
        
        # 验证tick字段完整性
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                for stock_code, tick_list in data_obj.items():
                    if isinstance(tick_list, list) and len(tick_list) > 0:
                        first_tick = tick_list[0]
                        # 验证16个tick字段
                        tick_fields = ["time", "last_price", "open", "high", "low", "last_close",
                                     "amount", "volume", "pvolume", "stock_status", "open_int",
                                     "last_settlement_price", "ask_price", "bid_price", 
                                     "ask_vol", "bid_vol", "transaction_num"]
                        found_fields = [f for f in tick_fields if f in first_tick]
                        print(f"\n✓ Tick字段数量: {len(found_fields)}/17")
                        print(f"✓ 包含字段: {found_fields[:5]}...")
        
        print("="*80)
    
    def test_get_divid_factors(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取除权除息数据"""
        data = {"stock_code": sample_stock_codes[0]}
        
        response = http_client.post("/api/v1/data/divid-factors", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("💰 除权除息数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, list) and len(data_obj) > 0:
                first_factor = data_obj[0]
                print(f"\n✓ 除权记录数: {len(data_obj)}")
                # 验证除权字段
                factor_fields = ["time", "interest", "stock_bonus", "stock_gift", 
                               "allot_num", "allot_price", "gugai", "dr"]
                found_fields = [f for f in factor_fields if f in first_factor]
                print(f"✓ 包含字段: {found_fields}")
        
        print("="*80)
    
    def test_get_full_kline(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取完整K线数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        data = {
            "stock_codes": sample_stock_codes[:1],
            "start_time": start_date.strftime("%Y%m%d"),
            "end_time": end_date.strftime("%Y%m%d"),
            "period": "1d"
        }
        
        response = http_client.post("/api/v1/data/full-kline", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📈 完整K线数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1500])
        
        # 验证K线字段完整性（11个字段）
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                for stock_code, kline_list in data_obj.items():
                    if isinstance(kline_list, list) and len(kline_list) > 0:
                        first_kline = kline_list[0]
                        kline_fields = ["time", "open", "high", "low", "close", "volume",
                                      "amount", "settle", "openInterest", "preClose", "suspendFlag"]
                        found_fields = [f for f in kline_fields if f in first_kline]
                        print(f"\n✓ K线字段数量: {len(found_fields)}/11")
                        print(f"✓ 包含字段: {found_fields}")
        
        print("="*80)
    
    # ===== 阶段3: 数据下载接口测试 =====
    
    def test_download_history_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试下载历史数据（单只）"""
        data = {
            "stock_code": sample_stock_codes[0],
            "period": "1d",
            "start_time": "",
            "end_time": "",
            "incrementally": False
        }
        
        response = http_client.post("/api/v1/data/download/history-data", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("⬇️  下载历史数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "data" in result:
            data_obj = result["data"]
            assert "task_id" in data_obj
            assert "status" in data_obj
            print(f"\n✓ 任务ID: {data_obj.get('task_id')}")
            print(f"✓ 任务状态: {data_obj.get('status')}")
            print(f"✓ 进度: {data_obj.get('progress')}%")
        
        print("="*80)
    
    def test_download_history_data_batch(self, http_client: httpx.Client, sample_stock_codes):
        """测试批量下载历史数据"""
        data = {
            "stock_list": sample_stock_codes[:3],
            "period": "1d",
            "start_time": "",
            "end_time": ""
        }
        
        response = http_client.post("/api/v1/data/download/history-data-batch", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("⬇️  批量下载历史数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "data" in result:
            data_obj = result["data"]
            assert "task_id" in data_obj
            print(f"\n✓ 批量任务ID: {data_obj.get('task_id')}")
            print(f"✓ 总数: {data_obj.get('total')}")
            print(f"✓ 已完成: {data_obj.get('finished')}")
        
        print("="*80)
    
    def test_download_financial_data(self, http_client: httpx.Client, sample_stock_codes):
        """测试下载财务数据"""
        data = {
            "stock_list": [sample_stock_codes[0]],
            "table_list": ["Capital"],
            "start_date": "",
            "end_date": ""
        }
        
        response = http_client.post("/api/v1/data/download/financial-data", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("⬇️  下载财务数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    def test_download_sector_data(self, http_client: httpx.Client):
        """测试下载板块数据"""
        response = http_client.post("/api/v1/data/download/sector-data")
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("⬇️  下载板块数据测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    # ===== 阶段4: 板块管理接口测试 =====
    
    def test_create_sector_folder(self, http_client: httpx.Client):
        """测试创建板块文件夹"""
        data = {
            "parent_node": "",
            "folder_name": "测试文件夹_pytest",
            "overwrite": True
        }
        
        response = http_client.post("/api/v1/data/sector/create-folder", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📁 创建板块文件夹测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    def test_create_sector(self, http_client: httpx.Client):
        """测试创建板块"""
        data = {
            "parent_node": "",
            "sector_name": "测试板块_pytest",
            "overwrite": True
        }
        
        response = http_client.post("/api/v1/data/sector/create", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 创建板块测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "data" in result:
            data_obj = result["data"]
            if "created_name" in data_obj:
                print(f"\n✓ 创建的板块名: {data_obj['created_name']}")
        
        print("="*80)
    
    def test_add_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试添加股票到板块"""
        data = {
            "sector_name": "测试板块_pytest",
            "stock_list": sample_stock_codes[:3]
        }
        
        response = http_client.post("/api/v1/data/sector/add-stocks", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("➕ 添加股票到板块测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    def test_reset_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试重置板块"""
        data = {
            "sector_name": "测试板块_pytest",
            "stock_list": sample_stock_codes[:2]
        }
        
        response = http_client.post("/api/v1/data/sector/reset", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🔄 重置板块测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    def test_remove_stock_from_sector(self, http_client: httpx.Client, sample_stock_codes):
        """测试从板块移除股票"""
        data = {
            "sector_name": "测试板块_pytest",
            "stock_list": [sample_stock_codes[0]]
        }
        
        response = http_client.post("/api/v1/data/sector/remove-stocks", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("➖ 从板块移除股票测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    def test_remove_sector(self, http_client: httpx.Client):
        """测试删除板块"""
        data = {"sector_name": "测试板块_pytest"}
        
        response = http_client.post("/api/v1/data/sector/remove", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("🗑️  删除板块测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("="*80)
    
    # ===== 阶段5: Level2数据接口测试 =====
    
    def test_get_l2_quote(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取Level2快照数据（10档）"""
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "start_time": "",
            "end_time": ""
        }
        
        response = http_client.post("/api/v1/data/l2/quote", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📊 Level2快照数据测试（10档）:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1500])
        
        # 验证10档行情字段
        if "data" in result:
            data_obj = result["data"]
            if isinstance(data_obj, dict):
                for stock_code, quote_list in data_obj.items():
                    if isinstance(quote_list, list) and len(quote_list) > 0:
                        first_quote = quote_list[0]
                        # 验证10档价格和量
                        if "ask_price" in first_quote:
                            ask_price = first_quote["ask_price"]
                            if isinstance(ask_price, list):
                                print(f"\n✓ 委卖价档数: {len(ask_price)}")
                                assert len(ask_price) <= 10, "委卖价不应超过10档"
                        
                        if "bid_price" in first_quote:
                            bid_price = first_quote["bid_price"]
                            if isinstance(bid_price, list):
                                print(f"✓ 委买价档数: {len(bid_price)}")
                                assert len(bid_price) <= 10, "委买价不应超过10档"
        
        print("="*80)
    
    def test_get_l2_order(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取Level2逐笔委托"""
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "start_time": "",
            "end_time": ""
        }
        
        response = http_client.post("/api/v1/data/l2/order", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("📝 Level2逐笔委托测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        
        print("="*80)
    
    def test_get_l2_transaction(self, http_client: httpx.Client, sample_stock_codes):
        """测试获取Level2逐笔成交"""
        data = {
            "stock_codes": [sample_stock_codes[0]],
            "start_time": "",
            "end_time": ""
        }
        
        response = http_client.post("/api/v1/data/l2/transaction", json=data)
        assert response.status_code == 200
        
        result = response.json()
        print("\n" + "="*80)
        print("💹 Level2逐笔成交测试:")
        print("="*80)
        
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
        
        print("="*80)

